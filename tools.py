import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

PERSIST_PATH = "./chroma_db"

@tool
def search_hospital_diet_guidelines(query: str) -> str:
    """Search verified medical diet protocols, clinical guidelines, keto diets, cancer diets, and hospital publications."""
    if not os.path.exists(PERSIST_PATH):
        return "No local diet guidelines database was found. Rely on general clinical knowledge instead."
    
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = Chroma(
            persist_directory=PERSIST_PATH,
            embedding_function=embeddings
        )
        
        docs = vectorstore.similarity_search(query, k=3)
        if not docs:
            return f"No relevant protocol context found in hospital database for '{query}'."
        
        results = []
        for doc in docs:
            source = doc.metadata.get("source", "Unknown document")
            results.append(f"--- Document Source: {source} ---\n{doc.page_content}")
            
        return "\n\n".join(results)
    except Exception as e:
        return f"Error retrieving document snippets: {str(e)}"

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