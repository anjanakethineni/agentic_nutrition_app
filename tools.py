import requests
from langchain_core.tools import tool

@tool
def get_verified_nutrition(food_item: str) -> str:
    """Lookup nutritional macro breakdown (calories, protein, carbs, fats) for a verified food item per 100g from public open databases."""
    try:
        search_url = f"https://openfoodfacts.org/cgi/search.pl?search_terms={food_item}&search_simple=1&action=process&json=1&page_size=1"
        response = requests.get(search_url, headers={"User-Agent": "AgenticNutritionApp - Web - Version 1.0"})
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            if products:
                product = products[0]
                product_name = product.get("product_name", food_item)
                nutriments = product.get("nutriments", {})
                
                calories = nutriments.get("energy-kcal_100g", "Unknown")
                protein = nutriments.get("proteins_100g", "Unknown")
                carbs = nutriments.get("carbohydrates_100g", "Unknown")
                fat = nutriments.get("fat_100g", "Unknown")
                
                return (f"Verified database metrics for matching item '{product_name}' (per 100g): "
                        f"Calories: {calories} kcal, Protein: {protein}g, Carbohydrates: {carbs}g, Fat: {fat}g.")
        return f"Could not locate verified metrics for '{food_item}' in public registries. Provide a realistic estimate based on visual composition instead."
    except Exception as e:
        return f"Database lookup failed due to network error: {str(e)}. Default to vision estimations."
    