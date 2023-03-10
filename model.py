from sqlalchemy import Column, Integer, String, DATETIME, FetchedValue
from database import Base

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

class Allergen(Base):
    __tablename__ = 'allergens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))

class RecipeAllergen(Base):
    __tablename__ = 'recipe_allergens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer)
    allergen_id = Column(Integer, primary_key=True)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))

class RecipeTag(Base):
    __tablename__ = 'recipe_tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer)
    tag_id = Column(Integer, primary_key=True)

class Instruction(Base):
    __tablename__ = 'instructions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer)
    number = Column(Integer)
    content = Column(String(255))