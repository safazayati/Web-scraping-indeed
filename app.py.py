from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

app = FastAPI()

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Connexion à MongoDB
db = client["projet"]  # Nom de la base de données
jobs_collection = db["jobs"]  # Nom de la collection

# Fonction pour sérialiser les données MongoDB
def serialize_job(job):
    return {
        "id": str(job["_id"]),  
        "title": job.get("title", "No title available"),  # Valeur par défaut
        "company": job.get("company", "No company specified"),
        "location": job.get("location", "Location not provided"),
        "url": job.get("url", "No URL available"),
    }

# Endpoint pour obtenir toutes les offres d'emploi avec pagination
@app.get("/jobs")
def get_jobs(skip: int = 0, limit: int = 10):
    jobs = jobs_collection.find().skip(skip).limit(limit)
    return {"jobs": [serialize_job(job) for job in jobs]}

# Endpoint pour rechercher des offres d'emploi par titre
@app.get("/jobs/search/{name}")
def search_job(name: str):
    jobs = jobs_collection.find({"title": {"$regex": name, "$options": "i"}})
    result = [serialize_job(job) for job in jobs]
    if not result:
        raise HTTPException(status_code=404, detail="No jobs found")
    return {"jobs": result}

# Endpoint pour filtrer les offres d'emploi par entreprise ou lieu
@app.get("/jobs/filter")
def filter_jobs(company: str = None, location: str = None):
    query = {}
    if company:
        query["company"] = {"$regex": company, "$options": "i"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    jobs = jobs_collection.find(query)
    return {"jobs": [serialize_job(job) for job in jobs]}

# Endpoint pour obtenir une offre d'emploi par son ID
@app.get("/jobs/{job_id}")
def get_job_by_id(job_id: str):
    try:
        # Vérification de la validité de l'ID
        if not ObjectId.is_valid(job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID format")
        
        # Recherche du job par son ID
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
        
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return serialize_job(job)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
