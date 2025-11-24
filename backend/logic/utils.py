def normalize(text: str):
    """
    Clean and normalize any ingredient or text:
    - Lowercase
    - Strip spaces
    """
    if not text:
        return ""
    return text.strip().lower()

def extract_ingredients(meal: dict):
    """
    Extract all ingredients from a recipe into a clean list.
    TheMealDB stores ingredients in strIngredient1..20
    """
    ingredients = []

    for i in range(1, 21):
        key = f"strIngredient{i}"
        ing  = meal.get(key)

        if ing and ing.strip() != "":
            ingredients.append(normalize(ing))

    return ingredients

