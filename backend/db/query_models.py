from typing import List
from pydantic import BaseModel

class RecipePostModel(BaseModel):
    recipe_name: str
    ingredients: List[str]
