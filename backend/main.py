from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Query

app = FastAPI(
    title="Smart Recipe Finder",
    description="Recipe Suggestion + Ingredient Checker using TheMealDB API",
    version="1.0"
)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# HTML Templates Directory
templates = Jinja2Templates(directory="frontend/templates")

# ---------- MODELS ----------
class IngredientInput(BaseModel):
    ingredients: List[str]

class CompareInput(BaseModel):
    recipe_ids: List[str]
    user_ingredients: str = ""


# ---------- EXTERNAL API HELPERS ----------
def mealdb_search_by_ingredient(ingredient: str):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json().get("meals")


def mealdb_get_recipe_by_id(meal_id: str):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    meals = response.json().get("meals")

    if not isinstance(meals, list):
        return None
    return meals[0] if meals else None

def mealdb_search_recipe(name: str):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={name}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json().get("meals")



# ---------- LOGIC FUNCTIONS ----------
def calculate_match_score(user_ing: List[str], recipe_ing: List[str]):
    matches = [i for i in recipe_ing if i in user_ing]
    if len(recipe_ing) == 0:
        return 0
    return round((len(matches) / len(recipe_ing)) * 100, 2)


def find_missing_ingredients(user_ing: List[str], recipe_ing: List[str]):
    return [i for i in recipe_ing if i not in user_ing]


def suggest_replacements(missing_list: List[str]):
    """
    Simple fallback replacement suggestion.
    (You can expand this later.)
    """
    replacement_dict = {
        "milk": ["almond milk", "soy milk"],
        "butter": ["ghee", "olive oil"],
        "egg": ["banana", "curd"],
        "sugar": ["honey", "jaggery"]
    }

    suggestions = {}

    for item in missing_list:
        suggestions[item] = replacement_dict.get(item.lower(), ["No replacement found"])

    return suggestions


# ---------- ROUTES ----------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/search")
def search_recipes(user_input: IngredientInput):
    user_ingredients = [i.lower() for i in user_input.ingredients]

    matched_ids = []

    for ing in user_ingredients:
        data = mealdb_search_by_ingredient(ing)
        if data:
            for meal in data:
                matched_ids.append(meal["idMeal"])

    unique_ids = list(set(matched_ids))

    return {
        "status": "success",
        "your_ingredients": user_ingredients,
        "matched_recipe_ids": unique_ids,
        "message": "Step 1 complete — IDs fetched successfully."
    }


@app.get("/recipe/{meal_id}")
def recipe_details(meal_id: str, user_ingredients: str = ""):
    """
    Returns:
    - full recipe details
    - ingredients
    - match score
    - missing items
    - replacement suggestions
    """

    # Step 1: Fetch recipe from MealDB
    recipe = mealdb_get_recipe_by_id(meal_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Step 2: Extract ingredients
    recipe_ing = []
    for i in range(1, 21):
        ing = recipe.get(f"strIngredient{i}")
        if ing and ing.strip():
            recipe_ing.append(ing.lower())

    # Step 3: Convert user ingredients
    user_ing = (
        [x.strip().lower() for x in user_ingredients.split(",")]
        if user_ingredients else []
    )

    # Step 4: Logic calculations
    score = calculate_match_score(user_ing, recipe_ing)
    missing = find_missing_ingredients(user_ing, recipe_ing)
    replacements = suggest_replacements(missing)

    # Step 5: Final response
    return {
    "meal_id": meal_id,
    "recipe_name": recipe["strMeal"],
    "category": recipe["strCategory"],
    "area": recipe["strArea"],
    "image": recipe["strMealThumb"],
    "instructions": recipe["strInstructions"],

    "ingredients_required": recipe_ing,
    "your_ingredients": user_ing,

    "match_score": score,
    "missing_ingredients": missing,
    "replacement_suggestions": replacements
}

    
@app.post("/recommend")
def recommend_recipes(user_input: IngredientInput):
    """
    Returns top 5 best recipes ranked by match score.
    Steps:
    1. Get all recipe IDs related to ingredients
    2. Fetch full recipe details for each ID
    3. Calculate match score for each recipe
    4. Sort by highest score and return top 5
    """

    user_ing = [i.lower() for i in user_input.ingredients]
    matched_ids = []

    # Step 1 → find all recipes matching ANY user ingredient
    for ing in user_ing:
        data = mealdb_search_by_ingredient(ing)
        if data:
            for meal in data:
                matched_ids.append(meal["idMeal"])

    unique_ids = list(set(matched_ids))

    results = []

    # Step 2 → fetch recipe details + scoring
    for meal_id in unique_ids:
        recipe = mealdb_get_recipe_by_id(meal_id)
        if recipe:

            # Extract ingredients
            recipe_ing = []
            for i in range(1, 21):
                ing = recipe.get(f"strIngredient{i}")
                if ing and ing.strip():
                    recipe_ing.append(ing.lower())

            # Score + missing + replacement
            score = calculate_match_score(user_ing, recipe_ing)
            missing = find_missing_ingredients(user_ing, recipe_ing)
            replacements = suggest_replacements(missing)

            results.append({
                "meal_id": meal_id,
                "recipe_name": recipe["strMeal"],
                "image": recipe["strMealThumb"],
                "match_score": score,
                "missing_ingredients": missing,
                "replacement_suggestions": replacements
            })

    # Step 3 → Sort by match score (highest first)
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)

    # Step 4 → Return top 5 recipes
    return {
        "your_ingredients": user_ing,
        "total_found": len(results),
        "top_5_recommendations": results[:5]
    }
@app.post("/compare")
def compare_recipes(
    request: Request,
    recipe_id1: str = Form(...),
    recipe_id2: str = Form(...),
    user_ingredients: str = Form("")
):
    recipe_ids = [recipe_id1, recipe_id2]

    # Convert user ingredients
    user_ing = [x.strip().lower() for x in user_ingredients.split(",")] if user_ingredients else []

    results = []

    for meal_id in recipe_ids:
        recipe = mealdb_get_recipe_by_id(meal_id)

        if recipe is None:
            raise HTTPException(status_code=404, detail=f"Recipe {meal_id} not found")

        # Extract ingredients
        recipe_ing = []
        for i in range(1, 21):
            ing = recipe.get(f"strIngredient{i}")
            if ing and ing.strip():
                recipe_ing.append(ing.lower())

        score = calculate_match_score(user_ing, recipe_ing)
        missing = find_missing_ingredients(user_ing, recipe_ing)
        replacements = suggest_replacements(missing)

        results.append({
            "meal_id": meal_id,
            "recipe_name": recipe["strMeal"],
            "match_score": score,
            "ingredients_required": recipe_ing,
            "missing_ingredients": missing,
            "replacement_suggestions": replacements
        })

    # Comparison summary
    comparison = {
        "better_match": (
            results[0]["recipe_name"]
            if results[0]["match_score"] > results[1]["match_score"]
            else results[1]["recipe_name"]
        ),
        "score_difference": abs(results[0]["match_score"] - results[1]["match_score"])
    }

    return {
        "your_ingredients": user_ing,
        "recipe_1": results[0],
        "recipe_2": results[1],
        "comparison_result": comparison
    }

@app.get("/search-recipe")
def search_recipe(name: str):
    meals = mealdb_search_by_ingredient(name)

    if not meals:
        raise HTTPException(status_code=404, detail="No recipes found")

    final_output = []

    for meal in meals[:3]:  # limit to top 3 results
        meal_id = meal["idMeal"]
        full_recipe = mealdb_get_recipe_by_id(meal_id)

        if not full_recipe:
            continue

        # extract ingredients
        ingredients = []
        for i in range(1, 21):
            item = full_recipe.get(f"strIngredient{i}")
            measure = full_recipe.get(f"strMeasure{i}")

            if item and item.strip():
                ingredients.append({
                    "item": item.strip(),
                    "measure": measure.strip() if measure else ""
                })

        # clean instructions (shortened 200 chars)
        instructions = full_recipe.get("strInstructions", "").strip()
        instructions_short = instructions[:200] + "..." if len(instructions) > 200 else instructions

        final_output.append({
            "id": meal_id,
            "name": full_recipe["strMeal"],
            "thumbnail": full_recipe["strMealThumb"],
            "recipe": {
                "ingredients": ingredients,
                "instructions": instructions_short
            }
        })

    return final_output


@app.get("/ui/search")
def ui_search(request: Request, name: str = None):

    results = []
    if name:
        results = search_recipe(name)

    return templates.TemplateResponse(
        "search_results.html",
        {"request": request, "results": results, "query": name}
    )


@app.get("/ui/exclude")
def ui_exclude(request: Request):
    return templates.TemplateResponse(
        "exclude_search.html",
        {"request": request}
    )
@app.get("/search/exclude")
def search_exclude(request: Request, include: str = "", exclude: str = ""):
    include = include.lower().strip()
    exclude_list = [x.strip().lower() for x in exclude.split(",") if x.strip()]

    if include == "":
        return templates.TemplateResponse(
            "exclude_results.html",
            {"request": request, "results": [], "query": include, "excluded": exclude_list}
        )

    # 1. Step: Search by ingredient (returns ONLY ids + names)
    basic_meals = mealdb_search_by_ingredient(include) or []

    final_results = []

    # 2. Step: Convert to *full recipe objects*
    for m in basic_meals:
        meal_id = m.get("idMeal")

        full = mealdb_get_recipe_by_id(meal_id)   # ⬅ FULL DETAILS!!
        if not full:
            continue

        # Extract ingredients from full MealDB recipe
        ingredients = []
        for i in range(1, 21):
            ing = full.get(f"strIngredient{i}")
            if ing and ing.strip():
                ingredients.append(ing.lower())

        ingredients_lower = ingredients

        # Skip if any excluded ingredient is present
        if any(ex in ingredients_lower for ex in exclude_list):
            continue

        # Append safe full objects
        final_results.append(full)

    return templates.TemplateResponse(
        "exclude_results.html",
        {
            "request": request,
            "results": final_results,
            "query": include,
            "excluded": exclude_list
        }
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/recipe", response_class=HTMLResponse)
async def recipe_page(request: Request):
    return templates.TemplateResponse("recipe.html", {"request": request})

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    return templates.TemplateResponse("compare.html", {"request": request})

@app.get("/recommend", response_class=HTMLResponse)
async def recommend_page(request: Request):
    return templates.TemplateResponse("recommend.html", {"request": request})
