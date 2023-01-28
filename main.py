from fastapi import FastAPI, UploadFile, File, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import session
from model import Recipe, Ingredient, Allergen, Tag, Instruction, RecipeBase, RecipeIngredient, RecipeTag
# from upload import upload_file
import requests
from dotenv import load_dotenv
import os
# import json
from schemas.recipe import RequestRecipeBase

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

@app.post("/api/post_recipe")
def post_recipe(recipe: RequestRecipeBase = Body(...), image: UploadFile = File(...)):
    try:
        # 画像アップロード
        load_dotenv()
        lamb = os.environ.get('LAMBDA')

        # response = upload_file(image)
        response = requests.post(lamb, files={'file': (image.filename, image.file)})
        
        print(response)
        print(response.json())

        image_url = response.json()

        # db登録
        # Check category_id
        if recipe.category_id < 1:
            raise HTTPException(status_code='404', detail='Category Error')

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
        print(recipe.ingredients)
        for ring in recipe.ingredients:
            if ring and ring.name and ring.quantity:
                res = session.query(Ingredient).filter(Ingredient.name == ring.name).first()

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

                print(db_ring)
                db_rings.append(db_ring)

        session.add_all(db_rings)

        # Create RecipeAllergens

        # Create RecipeTags
        print(recipe.tags)
        db_rtags = list()
        for tag in recipe.tags:
            if tag:
                db_rtag = RecipeTag()
                db_rtag.recipe_id = id

                res = session.query(Tag).filter(Tag.name == tag.name).first()
                if res is None:
                    # Create Tag
                    db_tag = Tag()
                    db_tag.name = tag.name
                    session.add(db_tag)
                    session.flush()

                    db_rtag.tag_id = db_tag.id
                else:
                    db_rtag.tag_id = res.id

                print(db_rtag)
                db_rtags.append(db_rtag)

        session.add_all(db_rtags)

        # Create Instructions
        print(recipe.instructions)
        for index, inst in enumerate(recipe.instructions):
            if inst and inst:
                db_inst = Instruction()
                db_inst.recipe_id = id
                db_inst.number = index
                db_inst.content = inst
                session.add(db_inst)
                print(db_inst)

        session.commit()

    except:
        raise HTTPException(status_code='404', detail='Error')

    finally:
        try:
            session.close()
        except:
            pass

    return {
        'status': 'OK'
    }