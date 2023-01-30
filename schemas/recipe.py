from typing import Optional, List
from pydantic import BaseModel
import json

# For post
class RequestRecipeBase(BaseModel):
    category_id: int
    title: str
    description: Optional[str]
    servings: int
    ingredients: List[RecipeIngredientBase] #本来idで指定
    allergens: Optional[List[int]]
    tags: Optional[List[str]]
    instructions: List[str]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    # class Config:
    #     orm_mode = True

#  For Responses
class IngredientBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class RecipeIngredientBase(BaseModel):
    name: str
    quantity: str

    class Config:
        orm_mode = True

class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class RecipeThumbBase(BaseModel):
    id: int
    category_id: int
    title: str
    image: str
    # image: str
    # description: Optional[str]
    # servings: int
    # ingredients: List[Ingredient]
    # allergens: Optional[List[str]]
    tags: Optional[List[str]]
    # instructions: List[str]

    class Config:
        orm_mode = True

class RecipeBase(BaseModel):
    id: int
    category_id: int
    title: str
    image: str
    description: Optional[str]
    servings: int
    ingredients: List[RecipeIngredientBase] #No id needed
    allergens: Optional[List[str]]
    tags: Optional[List[str]]
    instructions: List[str]

    class Config:
        orm_mode = True