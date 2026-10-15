# Procédure de déploiement

À compléter : prérequis, création de la base et du rôle PostgreSQL, variables
d'environnement, import des données, lancement de l'API et du front, sauvegarde
et restauration, vérifications après déploiement.
# Prérequis
Installer les éléments suivants :

- Python 3.12
- PostgreSQL version > 14
- Git

Vérifier les versions :
python --version
psql --version
git --version

# Récupération du dépôt

Clôner le dépôt :
- git clone <url-du-depot>
- cd veloville

# Création de l'environnement virtuel
Créer l'environnement virtuel :
py -3.12 -m venv .venv

Activer l'environnement :
.\.venv\Scripts\Activate.ps1

Installer les dépendances :
pip install -r requirements.txt

# Configuration de l'environnement
Copier :
.env.example

vers :
.env

# Configuration de l'environnement
Créer le rôle :
- CREATE ROLE veloville LOGIN PASSWORD 'veloville';

Créer la base :
- CREATE DATABASE veloville OWNER veloville;


# Création du schéma
Exécuter le script SQL :
- psql -U veloville -d veloville -f sql/schema.sql

Charger les comptes :
- psql -U veloville -d veloville -f sql/comptes.sql


# Importer les données
Lancer l'import :
python -m scripts.importer

Le script :
- charge les stations ;
- charge les trajets ;
- charge les incidents ;
- applique les règles de fiabilisation ;
- rejette les enregistrements invalides.

Le script est idempotent : les tables sont vidées avant rechargement.

# Vérification de l'import
Dans PostgreSQL : :
- SELECT COUNT(*) FROM station;
- SELECT COUNT(*) FROM trajet;
- SELECT COUNT(*) FROM incident;

Résultats obtenus :
- Stations : 120
- Trajets : 2002
- Incidents : 180

# Lancement de l'API
Démarrer l'API :
- uvicorn api.main:app --reload

Accéder à la documentation :
- http://127.0.0.1:8000/docs

Vérifier l'état de l'API :
- GET /sante

Réponse attendue :
- {
  "statut": "ok"
}

# Routes disponibles
Consultation :
- GET /stations
- GET /stations/{station_id}
- GET /trajets
- GET /incidents

Indicateurs :
- GET /indicateurs/activite-par-jour
- GET /indicateurs/stations-actives
- GET /indicateurs/incidents-par-statut

# Lancement du front Streamlit
Démarrer le front :
- streamlit run front/app.py

Accéder à l'application :
- http://localhost:8501

Pages disponibles : 
- Stations
- Incidents
- Indicateurs

# Sauvegarde de la base
Non implémenté à ce jour - Reste à faire

# Restauration de la base
Non implémenté à ce jour - Reste à faire


# Vérifications après déploiement
Vérifier :

- accès à Swagger
- réponse de /sante
- affichage des stations
- affichage des trajets
- affichage des incidents
- affichage des indicateurs
- démarrage du front Streamlit

# Limites connues

Les éléments suivants ne sont pas implémentés dans la version livrée :

- nettoyage des données à compléter
- authentification JWT
- gestion des rôles
- routes à compléter
- recette à réaliser
- journal détaillé des rejets à enrichir