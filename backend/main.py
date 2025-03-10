import os
from http.client import HTTPException

from bring_api import BringItemOperation
from fastapi import FastAPI, Depends
from fastapi.openapi.models import Response
from fastapi.security import APIKeyHeader

from db.models import Recipes, Ingredients, IngredientsRecipes
from db.query_models import RecipePostModel
from utils import get_db_session
from utils import get_list_id
from utils import create_bring_session

from sqlalchemy import select

app = FastAPI()


API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def validate_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        return Response(status_code=401, description="Invalid API key")
    return {"user": "Authorized User"}

@app.get("/items")
async def get_items(user: dict = Depends(validate_api_key))-> list[dict]:
    bring_instance, session = await create_bring_session()
    try:
        list_id=await get_list_id(bring_instance= bring_instance)
        items = await bring_instance.get_list(list_id)
        return items["purchase"]

    finally:
        await session.close()


@app.post("/items")
async def post_list(list_of_items_dict:list[dict], user: dict = Depends(validate_api_key)):
    bring_instance, session = await create_bring_session()
    list_id=await get_list_id(bring_instance= bring_instance)
    try:
        await bring_instance.batch_update_list(
            list_id,
            list_of_items_dict,
            BringItemOperation.ADD)
        return Response(description="Posted succesfully", status_code=200)
    finally:
        await session.close()


@app.delete("/items")
async def delete_all_items(user: dict = Depends(validate_api_key)):
    bring_instance, session = await create_bring_session()
    try:
        items=await get_items()
        list_id=await get_list_id(bring_instance= bring_instance)
        await bring_instance.batch_update_list(
                list_id,
                items,
                BringItemOperation.REMOVE)
        return Response(status_code=200)
    finally:
        await session.close()

@app.get("/recipe")
def get_recipe(user: dict = Depends(validate_api_key)):
    with get_db_session() as session:
        response=session.query(Recipes).all()

    return response

@app.get("/ingredients/{recipe_name}")
def get_ingredients(recipe_name:str, user: dict = Depends(validate_api_key)):
    with get_db_session() as session:
        stmt = (
            select(Ingredients.name)
            .join(IngredientsRecipes, Ingredients.name == IngredientsRecipes.ingredient_name)
            .where(IngredientsRecipes.recipe_name == recipe_name)
        )

        result = session.execute(stmt).scalars().all()
    return result


@app.post("/recipe")
def post_recipe(recipe_with_ingredients: RecipePostModel, user: dict = Depends(validate_api_key)):
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
            return Response(
                status_code=404,
                description=f"Recipe already exists!"
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
        return Response(
            status_code=500,
            description=f"An unexpected error occurred: {str(exc)}"
        )
    finally:
        session.close()



@app.delete("/recipe")
def delete_recipe(recipe_name: str, user: dict = Depends(validate_api_key)):
    session = get_db_session()

    try:
        # Check if the recipe exists
        recipe = session.query(Recipes).filter_by(name=recipe_name).first()
        if not recipe:
            return Response(status_code=404, description="Recipe not found")

        # Delete the linked ingredients from IngredientsRecipes (but keep ingredients themselves)
        session.query(IngredientsRecipes).filter_by(recipe_name=recipe_name).delete()

        # Delete the recipe itself
        session.delete(recipe)

        # Commit changes
        session.commit()

        return {"message": f"Recipe '{recipe_name}' deleted successfully"}

    except Exception as exc:
        session.rollback()
        return Response(status_code=500, detail=f"An unexpected error occurred: {str(exc)}")
    finally:
        session.close()

