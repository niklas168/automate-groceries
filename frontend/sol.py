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
        # get ingredients for selected meals
        item_list=[]
        for meal in meals.value:
            url = os.getenv("BACKEND_HOST") + "/ingredients/"+meal
            response=requests.get(url=url)

            if response.status_code == 200:
                item_list.extend(response.json())
            else:
                print(f"Failed to fetch {meal}: {response.status_code}, {response.text}")

        #add those ingredients to groceries
        url = os.getenv("BACKEND_HOST") + "/items"
        list_of_item_dicts=[{"itemId":item_name} for item_name in item_list]

        response=requests.post(url=url,json=list_of_item_dicts)
        if response.status_code != 200:
            print(f"Failed to post {list_of_item_dicts}: {response.status_code}, {response.text}")

        # reset meals
        meals.value = []
        pass

    def delete_recipe(column, row_index):
        #identify recipe
        recipe_name=df.value.loc[int(row_index), column]

        # delete from db
        url = os.getenv("BACKEND_HOST") + "/recipe"
        params = {"recipe_name": recipe_name}
        response=requests.delete(url=url, params=params)

        # when successful delete from df
        if response.status_code == 200:
            df.value.drop(index=int(row_index), inplace=True)
        else:
            print(f"Failed to delete {recipe_name}: {response.status_code}, {response.text}")

        load_meals()


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
