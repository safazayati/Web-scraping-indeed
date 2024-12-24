from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI()

# Configuration du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplacez par votre URI MongoDB
db = client["projet"]
products_collection = db["produits"]

# Fonction pour sérialiser les données MongoDB
def serialize_product(product):
    return {
        "title": product.get("title", "N/A"),
        "company": product.get("company", "N/A"),
        "location": product.get("location", "N/A"),
        "summary": product.get("summary", "N/A"),
    }

@app.get("/products")
def get_products():
    products = products_collection.find()
    return {"products": [serialize_product(product) for product in products]}

@app.get("/products/stats")
def get_products_stats():
    products = list(products_collection.find())
    # Nettoyer les données pour enlever les offres sans informations
    cleaned_products = [p for p in products if "title" in p and p["title"] != "N/A"]

    # Créer un DataFrame pandas
    df = pd.DataFrame([serialize_product(p) for p in cleaned_products])

    # Calculer les statistiques
    job_counts = df['title'].value_counts()
    company_counts = df['company'].value_counts()

    # Tracer les statistiques
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Graphique des titres de postes
    job_counts.plot(kind='bar', ax=ax1, title="Distribution des Titres de Poste")
    ax1.set_xlabel("Title")
    ax1.set_ylabel("Count")

    # Graphique des entreprises
    company_counts.plot(kind='bar', ax=ax2, title="Distribution des Entreprises")
    ax2.set_xlabel("Company")
    ax2.set_ylabel("Count")

    # Enregistrer le graphique en base64
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return {"chart": image_base64}

@app.get("/products/search/{name}")
def search_product(name: str):
    products = products_collection.find({"title": {"$regex": name, "$options": "i"}})
    result = [serialize_product(product) for product in products]
    if not result:
        raise HTTPException(status_code=404, detail="No products found")
    return {"products": result}

@app.get("/products/filter")
def filter_products(category: str = None, min_price: float = 0, max_price: float = float("inf")):
    query = {"price": {"$gte": min_price, "$lte": max_price}}
    if category:
        query["category"] = category
    products = products_collection.find(query)
    return {"products": [serialize_product(product) for product in products]}

@app.get("/products/sort")
def sort_products(order: str = "asc", sort_by: str = "price"):
    sort_order = 1 if order == "asc" else -1
    products = products_collection.find().sort(sort_by, sort_order)
    return {"products": [serialize_product(product) for product in products]}
