from sqlalchemy import Column, Integer, String, DATETIME, FetchedValue
from pydantic import BaseModel
from database import Base
from typing import Optional, List

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False)
    title = Column(String(50), nullable=False)
    image = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    servings = Column(Integer, nullable=False)
    created_at = Column(DATETIME, FetchedValue())
    updated_at = Column(DATETIME, FetchedValue())

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer)
    ingredient_id = Column(Integer)
    quantity = Column(String(20))

class Allergen():
    __tablename__ = 'allergens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))

class RecipeAllergen():
    __tablename__ = 'recipe_allergens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer)
    allergen_id = Column(Integer, primary_key=True)

class Tag():
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))

class RecipeTag():
    __tablename__ = 'recipe_tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer)
    tag_id = Column(Integer, primary_key=True)

class Instruction():
    __tablename__ = 'instructions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer)
    number = Column(Integer)
    content = Column(String(255))



#  For Responses
#  For Search
class IngredientBase(BaseModel):
    id: int
    name: str

class RecipeIngredientBase(BaseModel):
    name: str
    quantity: str

class RecipeThumbBase(BaseModel):
    category_id: int
    title: str
    thumb: str
    # image: str
    # description: Optional[str]
    servings: int
    # ingredients: List[Ingredient]
    # allergens: Optional[List[str]]
    tags: Optional[List[str]]
    # instructions: List[str]

class RecipeBase(BaseModel):
    category_id: int
    title: str
    image: str
    description: Optional[str]
    servings: int
    ingredients: List[RecipeIngredientBase] #No id needed
    allergens: Optional[List[str]]
    tags: Optional[List[str]]
    instructions: List[str]