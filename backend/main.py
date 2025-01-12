from http.client import HTTPException
from typing import Union
import json

from bring_api import BringItemOperation
from fastapi import FastAPI
from fastapi.openapi.models import Response

from db.models import Recipes, Ingredients, IngredientsRecipes
from db.query_models import RecipePostModel
from utils import get_db_session
from utils import get_list_id
from utils import create_bring_session

from sqlalchemy import select

app = FastAPI()




@app.get("/items")
async def get_items()-> list[dict]:
    bring_instance, session = await create_bring_session()
    try:
        list_id=await get_list_id(bring_instance= bring_instance, list_name="Einkoofen")
        items = await bring_instance.get_list(list_id)
        return items["purchase"]

    finally:
        await session.close()


@app.post("/items")
async def post_list(item_dict:dict):
    bring_instance, session = create_bring_session()
    list_id=await get_list_id(bring_instance= bring_instance, list_name="Einkoofen")
    try:
        await bring_instance.batch_update_list(
            list_id,
            item_dict,
            BringItemOperation.ADD)
        return Response(status_code=200)
    finally:
        await session.close()


@app.delete("/items")
async def delete_all_items():
    bring_instance, session = await create_bring_session()
    try:
        items=await get_items()
        list_id=await get_list_id(bring_instance= bring_instance, list_name="Einkoofen")
        await bring_instance.batch_update_list(
                list_id,
                items,
                BringItemOperation.REMOVE)
        return Response(status_code=200)
    finally:
        await session.close()

@app.get("/recipe")
def get_recipe():
    session=get_db_session()
    results=session.query(Recipes).all()
    return results

@app.get("/ingredients/{recipe_name}")
def get_ingredients(recipe_name:str):
    session=get_db_session()
    stmt = (
        select(Ingredients.name)
        .join(IngredientsRecipes, Ingredients.name == IngredientsRecipes.ingredient_name)
        .where(IngredientsRecipes.recipe_name == recipe_name)
    )

    result = session.execute(stmt).scalars().all()
    return result


@app.post("/recipe")
def post_recipe(recipe_with_ingredients: RecipePostModel):
    session = get_db_session()
    try:
        recipe_name = recipe_with_ingredients.recipe_name
        # Check if the recipe already exists
        recipe = session.query(Recipes).filter_by(name=recipe_name).first()
        if not recipe:
            # Create a new recipe if it doesn't exist
            recipe = Recipes(name=recipe_name)
            session.add(recipe)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Recipe already exists!"
            )

        # Add ingredients and link them to the recipe
        for ingredient_name in recipe_with_ingredients.ingredients:
            if not ingredient_name:
                continue  # Skip empty ingredient names

            # Check if the ingredient already exists
            ingredient = session.query(Ingredients).filter_by(name=ingredient_name).first()
            if not ingredient:
                # Create a new ingredient if it doesn't exist
                ingredient = Ingredients(name=ingredient_name)
                session.add(ingredient)

            # Add the relationship
            recipe_ingredient = IngredientsRecipes(
                recipe_name=recipe_name,
                ingredient_name=ingredient_name
            )
            session.add(recipe_ingredient)

        # Commit transaction
        session.commit()
        return {"message": "Recipe created or updated successfully", "recipe_name": recipe_name}

    except HTTPException as http_exc:
        session.rollback()
        raise http_exc
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(exc)}"
        )
    finally:
        session.close()


