import os
from pathlib import Path

import dotenv
import requests
import pandas as pd

import solara

recipe_name = solara.reactive("")
ingredients = solara.reactive([])
ingredient= solara.reactive("")
#TODO: Why df in the first place, maybe should display ingredients(probably too much info, so maybe dynamic aufklappen)
df=solara.reactive(pd.DataFrame(columns=["Recipe Name"]))
#all_meals=df.value["Recipe Name"].to_list()
meals=solara.reactive([])

@solara.component
def Page():

    show_dialog = solara.use_reactive(False)

    def load_meals():

        url=os.getenv("BACKEND_HOST")+"/recipe"
        response=requests.get(url=url)

        result = []
        for dict_item in response.json():
            result.append(dict_item["name"])

        df.value=pd.DataFrame(result, columns=["Recipe Name"])

    def add_ingredient():
        # Append a new reactive value to the ingredients list
        ingredients.value=ingredients.value+[ingredient.value]
        ingredient.value=""

    def add_recipe_to_db():
        #TODO: make conn to db and add recipe here
        body={
            "recipe_name": recipe_name.value,
            "ingredients": ingredients.value,
        }

        url = os.getenv("BACKEND_HOST")+"/recipe"
        requests.post(url=url, json=body)

        #resetting inputs
        ingredients.value=[]
        recipe_name.value=""
        load_meals()

    def add_items_to_groceries():
        # todo: take meal.value and put it onto grocery list
        meals.value=[]
        pass

    def delete_recipe(column, row_index):
        #TODO: delete recipe name = df of row x column y
        pass

    dotenv.load_dotenv()
    solara.use_effect(load_meals, dependencies=[])

    with solara.lab.Tabs():
        with solara.lab.Tab("Rezeptverwaltung"):
            with solara.Card():
                #solara.Style(css)
                cell_actions = [solara.CellAction(icon="mdi-delete", name="Delete Recipe", on_click=delete_recipe)]
                with solara.Column():
                    solara.DataFrame(df.value, cell_actions=cell_actions)
                    solara.Button("Add recipe", on_click=lambda: show_dialog.set(True),classes=["button-1"])

            with solara.lab.ConfirmationDialog(title="Adding new recipe", on_ok=add_recipe_to_db, open=show_dialog):
                solara.InputText("Recipe Name", value=recipe_name, autofocus=True)
                solara.InputText("Ingredients", value=ingredient, autofocus=True)
                solara.Button("Add", on_click=add_ingredient)
                solara.Markdown(f"Ingredients: {ingredients.value}")

        with solara.lab.Tab("Einkaufslistenvewaltung"):
            with solara.Card():
                solara.SelectMultiple(label="Gerichte", values=meals, all_values=df.value["Recipe Name"].to_list())
                solara.Button(label="Add recipes to grocery list", on_click=add_items_to_groceries)
                solara.Markdown(f"**Selected**: {meals.value}")
