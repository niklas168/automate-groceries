import os

from dotenv import load_dotenv
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class Recipes(Base):
    __tablename__ = 'recipes'
    name: Mapped[str] = mapped_column(String(100), primary_key=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f'<Recipe: {self.name}'


class Ingredients(Base):
    __tablename__ = 'ingredients'
    name: Mapped[str] = mapped_column(String(100), primary_key=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f'<Ingredient: {self.name}'

class IngredientsRecipes(Base):
    __tablename__ = 'ingredients_recipes'
    recipe_name: Mapped[int] = mapped_column(ForeignKey('recipes.name'), primary_key=True)
    ingredient_name: Mapped[int] = mapped_column(ForeignKey('ingredients.name'), primary_key=True)

    def __init__(self, recipe_name, ingredient_name):
        self.recipe_name = recipe_name
        self.ingredient_name = ingredient_name

load_dotenv()
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")

engine=create_engine(
        url="postgresql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        ), echo=True
    )
Base.metadata.create_all(engine)
