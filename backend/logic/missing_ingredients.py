from .utils import normalize

PANTRY_ITEMS = {
    "salt", "pepper", "sugar", "oil", "water", "turmeric",
    "chilli powder", "flour", "rice", "wheat", "garam masala"
}

def find_missing(user_ingredient: str, recipe_ingredients: list):
    """
    Compare user ingredients with recipe ingredients.

    Returns:
          - missing ingredients list
          - matched (True/False)
    """

    user = normalize(user_ingredient)

    missing = []

    for ing in recipe_ingredients:
        if ing == user:
            continue 
        if ing in PANTRY_ITEMS:
            continue
        missing.append(ing)

    matched = user in recipe_ingredients

    return missing, matched