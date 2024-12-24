from pymongo import MongoClient
from bson import ObjectId

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')  
db = client['zahra']  
collection = db['jobs']  

# Données à insérer
data = {
    "_id": "67671e3359f846f7a577963b",  # ID en format simple (assurez-vous qu'il est unique)
    "title;company;location;summary": "Software Engineer;N/A;N/A;N/A"
}

# Vérifier si l'ID existe déjà
existing_job = collection.find_one({"_id": data["_id"]})
if existing_job:
    print(f"Le job avec l'ID {data['_id']} existe déjà.")
else:
    # Transformation des données
    split_data = data["title;company;location;summary"].split(";")
    formatted_data = {
        "_id": data["_id"],
        "title": split_data[0],
        "company": split_data[1],
        "location": split_data[2],
        "summary": split_data[3]
    }

    # Insertion des données dans MongoDB
    try:
        result = collection.insert_one(formatted_data)
        print("Données insérées avec succès:", result.inserted_id)
    except Exception as e:
        print("Erreur lors de l'insertion:", e)
