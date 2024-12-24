const express = require('express');
const { MongoClient } = require('mongodb');
const cors = require('cors');

const app = express();
const port = 3000;

// Configuration CORS pour permettre les requêtes depuis le front-end
app.use(cors());

// Connexion à MongoDB
const url = 'mongodb://127.0.0.1:27017';
const dbName = 'zahra';

let db;

MongoClient.connect(url)
    .then(client => {
        console.log('Connecté à MongoDB');
        db = client.db(dbName); // Initialisation de la base de données

        // Une fois la connexion réussie, définir les routes
        // Route de base
        app.get('/', (req, res) => {
            res.send('Bienvenue à l\'API des offres d\'emploi ! Visitez /jobs pour voir les données.');
        });

        // Route pour obtenir les offres d'emploi
        app.get('/jobs', (req, res) => {
            const jobsCollection = db.collection('jobs'); // Accède à la collection 'jobs'
            jobsCollection.find().toArray() // Trouver tous les documents et les convertir en tableau
                .then(jobs => {
                    res.json(jobs); // Envoie les résultats au client
                })
                .catch(err => {
                    res.status(500).send('Erreur lors de la récupération des offres d\'emploi');
                });
        });

        // Lancer le serveur après la connexion réussie à MongoDB
        app.listen(port, () => {
            console.log(`Serveur en cours d'exécution sur http://localhost:${port}`);
        });
    })
    .catch(err => {
        console.error('Erreur de connexion à MongoDB:', err);
    });
