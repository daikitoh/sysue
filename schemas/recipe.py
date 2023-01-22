from typing import Optional, List
from pydantic import BaseModel
from model import RecipeIngredientBase
import json

# For Requests
class RequestRecipeBase(BaseModel):
    category_id: int
    title: str
    description: Optional[str]
    servings: int
    ingredients: List[RecipeIngredientBase] #本来idで指定
    allergens: Optional[List[str]]
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

    class Config:
        orm_mode = True