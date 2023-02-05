from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import session
from model import Recipe, Ingredient, Allergen, Tag, Instruction, RecipeIngredient, RecipeTag, RecipeAllergen
# from upload import upload_file
import requests
from dotenv import load_dotenv
import os
# import json
from schemas.recipe import RequestRecipeBase, RecipeThumbBase, RecipeBase, IngredientBase, RecipeIngredientBase,TagBase, RecipeTagBase, RecipeAllergenBase, RecipeInstructionBase
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
from typing import List

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", \
    StaticFiles(directory="templates/static"), \
        name="static")

templates = Jinja2Templates(directory='templates')

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request
        }
    )

@app.post("/api/post_recipe/")
def post_recipe(recipe: RequestRecipeBase = Form(), image: UploadFile = File()):
    try:
        # 画像アップロード
        load_dotenv()
        lamb = os.environ.get('LAMBDA')

        # response = upload_file(image)
        response = requests.post(lamb, files={'file': (image.filename, image.file)})

        image_url = response.json()

        # db登録
        # Check category_id
        if recipe.category_id < 1 or recipe.servings < 1:
            raise HTTPException(status_code=404, detail='Category Error')

        # Create Recipe
        db_recipe = Recipe()
        db_recipe.title = recipe.title
        db_recipe.category_id = recipe.category_id
        db_recipe.image = image_url
        db_recipe.description = recipe.description
        db_recipe.servings = recipe.servings

        session.add(db_recipe)
        session.flush()

        id = db_recipe.id

        # Create RecipeIngredients
        # ingredientが存在すればid取得、なければ作成してid返却
        # 本来なら最初からid
        db_rings = list()
        for ring in recipe.ingredients:
            if ring and ring.name and ring.quantity:
                res = session.query(Ingredient).filter(Ingredient.name == func.binary(ring.name)).first()

                db_ring = RecipeIngredient()
                db_ring.recipe_id = id
                db_ring.quantity = ring.quantity

                if res is None:
                    # Create Ingredient
                    db_ing = Ingredient()
                    db_ing.name = ring.name
                    session.add(db_ing)
                    session.flush()

                    db_ring.ingredient_id = db_ing.id
                else:
                    db_ring.ingredient_id = res.id

                db_rings.append(db_ring)

        session.add_all(db_rings)

        # Create RecipeAllergens
        if recipe.allergens:
            for al in recipe.allergens:
                if al:
                    db_al = RecipeAllergen()
                    db_al.recipe_id = id
                    db_al.allergen_id = al
                    session.add(db_al)

        # Create RecipeTags
        if recipe.tags:
            db_rtags = list()
            for tag in recipe.tags:
                if tag:
                    db_rtag = RecipeTag()
                    db_rtag.recipe_id = id

                    res = session.query(Tag).filter(Tag.name == func.binary(tag)).first()
                    if res is None:
                        # Create Tag
                        db_tag = Tag()
                        db_tag.name = tag
                        session.add(db_tag)
                        session.flush()

                        db_rtag.tag_id = db_tag.id
                    else:
                        db_rtag.tag_id = res.id

                    db_rtags.append(db_rtag)

            session.add_all(db_rtags)

        # Create Instructions
        for index, inst in enumerate(recipe.instructions):
            if inst:
                db_inst = Instruction()
                db_inst.recipe_id = id
                db_inst.number = index + 1
                db_inst.content = inst
                session.add(db_inst)

        session.commit()

    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail='Error')

    finally:
        try:
            session.close()
        except:
            pass

    return {
        'status': 'OK'
    }


@app.get("/api/recipes/", response_model=List[RecipeThumbBase])
def get_recipes(
    category_id: int = None,
    title: str = None,
    description: str = None,
    servings: int = None,
    ingredients: List[int] = Query(default=None),
    allergens: List[int] = Query(default=None),
    tags: List[int] = Query(default=None)  # id?
):
    if not category_id and not title and not description and not servings and not ingredients and not allergens and not tags:
        raise HTTPException(status_code=404, detail='Invalid Request')
        
    try:
        joins = []
        if ingredients:
            ings = [0] * len(ingredients)
            for index, i in enumerate(ingredients):
                ings[index] = aliased(RecipeIngredient)
                joins.append((
                    ings[index], and_(ings[index].recipe_id == Recipe.id, ings[index].ingredient_id == i)
                ))
            # joins.append((
            #     RecipeIngredient, and_(RecipeIngredient.recipe_id == Recipe.id, RecipeIngredient.ingredient_id.in_(ingredients))
            # ))
        if tags:
            tgs = [0] * len(tags)
            for index, t in enumerate(tags):
                tgs[index] = aliased(RecipeTag)
                joins.append((
                    tgs[index], and_(tgs[index].recipe_id == Recipe.id, tgs[index].tag_id == t)
                ))
            # joins.append((
            #     RecipeTag, and_(RecipeTag.recipe_id == Recipe.id, RecipeTag.tag_id.in_(tags))
            # ))

        q = session.query(Recipe.id, Recipe.category_id, Recipe.title, Recipe.image,)\
            .filter(Recipe.category_id == category_id if category_id else True)\
            .filter(Recipe.title.like("%" + title + "%") if title else True)\
            .filter(Recipe.description.like("%" + description + "%") if description else True)\
            .filter(Recipe.servings == servings if servings else True)\
            .filter(Recipe.id.not_in(
                session.query(RecipeAllergen.recipe_id).filter(RecipeAllergen.allergen_id.in_(allergens))
            ) if allergens else True)\
            .filter(RecipeTag.tag_id.in_(tags) if tags else True)

        for j in joins:
            q = q.join(*j)

        recipes = q.group_by(Recipe.id).limit(100).all()
        return recipes
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@app.get("/api/recipe/", response_model=RecipeBase)
def get_recipe(id: int):
    try:
        recipe = session.query(Recipe).filter(Recipe.id == id).first()

        if not recipe:
            raise HTTPException(status_code=404, detail='No result')

        recipe.ingredients: List[RecipeIngredientBase] = session.query(Ingredient.name, RecipeIngredient.quantity)\
            .join(RecipeIngredient, and_(RecipeIngredient.ingredient_id == Ingredient.id, RecipeIngredient.recipe_id == id)).all()

        recipe.allergens: List[RecipeAllergenBase] = session.query(Allergen.name)\
            .join(RecipeAllergen, and_(RecipeAllergen.allergen_id == Allergen.id, RecipeAllergen.recipe_id == id)).all()

        recipe.tags: List[RecipeTagBase] = session.query(Tag.name)\
            .join(RecipeTag, and_(RecipeTag.tag_id == Tag.id, RecipeTag.recipe_id == id)).all()

        recipe.instructions: List[RecipeIngredientBase] = session.query(Instruction.number, Instruction.content)\
            .filter(Instruction.recipe_id == id).order_by(Instruction.number).all()

        return recipe

    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@app.get("/api/ingredients/", response_model=List[IngredientBase])
def get_ingredients(keyword: str):
    if not keyword or keyword.isspace():
        raise HTTPException(status_code=404, detail='Invalid Request')
    try:
        return session.query(Ingredient)\
            .filter(Ingredient.name.like("%" + keyword + "%")).limit(100).all()

    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@app.get("/api/tags/", response_model=List[TagBase])
def get_tags(keyword: str):
    if not keyword or keyword.isspace():
        raise HTTPException(status_code=404, detail='Invalid Request')
    try:
        return session.query(Tag)\
            .filter(Tag.name.like("%" + keyword + "%")).limit(100).all()

    except Exception as e:
        raise HTTPException(status_code=404, detail=e)