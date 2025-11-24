import requests

BASE_URL = "https://www.themealdb.com/api/json/v1/1/"


def fetch_all_meals():
    """
    Fetch ALL meals from TheMealDB by searching empty string.
    We will reuse this across all features.
    """

    url = BASE_URL + "search.php?s="
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    return data.get("meals", [])


def search_by_ingredient(ingredient: str):
    """
    Search meals containing a specific ingredient.
    Uses: filter.php?i=ingredient
    Returns minimal recipe info: idMeal, strMeal, strMealThumb
    """

    if not ingredient:
        return []

    url = BASE_URL + f"filter.php?i={ingredient}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    return data.get("meals", [])


def get_recipe_by_id(meal_id: str):
    """
    Fetch full recipe details using meal ID.
    Uses: lookup.php?i=meal_id
    Returns full ingredients, instructions, etc.
    """

    if not meal_id:
        return None

    url = BASE_URL + f"lookup.php?i={meal_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    meals = data.get("meals")

    if not meals:
        return None

    return meals[0]
