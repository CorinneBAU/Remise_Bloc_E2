# VéloVille — Plateforme de valorisation des données

À compléter : présentation du projet, prérequis, installation, lancement de
l'API et du front, exécution des tests, liens vers la documentation
(docs/), auteur et version.


## Contexte

VéloVille est une application de suivi de l’activité d’un réseau de vélos en libre-service.

Le projet permet :

- l’import et la fiabilisation des données issues du système de billettique ;
- le stockage des données dans PostgreSQL ;
- l’exposition d’une API REST FastAPI ;
- le calcul d’indicateurs métier.

## Prérequis

- Python 3.12
- PostgreSQL 14 ou supérieur
- Git
- pip
- un environnement virtuel Python recommandé

Principales bibliothèques utilisées :

- pandas
- SQLAlchemy
- psycopg
- FastAPI
- Uvicorn
- Pydantic
- Streamlit
- requests

## Installation

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd veloville
```

### 2. Créer un environnement virtuel

Sous Windows PowerShell :

```powershell
python -m venv .venv
```

Activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

Sous Linux/macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Créer la base PostgreSQL

La base attendue s'appelle :

```text
veloville
```

Création du rôle :

```bash
CREATE ROLE veloville LOGIN PASSWORD 'veloville';
```


Création de la base :

```bash
CREATE DATABASE veloville OWNER veloville;
```

Exécution du schéma  :

```bash
psql -U veloville -d veloville -f sql/schema.sql;
```

Chargement des comptes :  :

```bash
psql -U veloville -d veloville -f sql/comptes.sql;
```


Le projet ne dépend pas de Docker : toute instance PostgreSQL accessible avec les paramètres de connexion configurés peut être utilisée.

### 5. Configurer les variables d'environnement

# Connexion PostgreSQL (format SQLAlchemy + psycopg 3)
Sous Windows PowerShell :

```powershell
$env: DATABASE_URL=postgresql+psycopg://veloville:veloville@localhost:5432/veloville

$env: TEST_DATABASE_URL=postgresql+psycopg://veloville:veloville@localhost:5432/veloville_test
```

Sous Linux/macOS :

```bash
export DATABASE_URL=postgresql+psycopg://veloville:veloville@localhost:5432/veloville

export TEST_DATABASE_URL=postgresql+psycopg://veloville:veloville@localhost:5432/veloville_test
```

Aucun mot de passe PostgreSQL n'est stocké dans le dépôt.

## Variables d'environnement

Le projet utilise les variables suivantes :

| Variable | Description |
|-----------|-------------|
|DATABASE_URL| Chaîne de connexion PostgreSQL utilisée par l'application|
|TEST_DATABASE_URL| Chaîne de connexion PostgreSQL utilisée par les tests|
|JWT_SECRET| Clé secrète utilisée pour la génération des jetons JWT|
|JWT_ALGORITHM| Algorithme de signature des JWT|
|JWT_EXPIRATION_MINUTES| Durée de validité des jetons|
|API_URL| URL de l'API utilisée par le front Streamlit|
|API_TIMEOUT_SECONDES| Délai maximal d'attente des requêtes HTTP|

## Préparation et chargement des données

Les CSV originaux présents dans `data/` ne doivent jamais être modifiés.

### Étape 3 — audit et nettoyage

Les anomalies suivantes ont été identifiées :

- stations inconnues ;
- trajets dupliqués ;
- durées négatives ou nulles ;
- statuts d’incident avec casse hétérogène ;
- dates incohérentes.

### Étape 4 — création du schéma PostgreSQL

Exécuter :

```bash
psql -U postgres -d veloville -f sql/schema.sql
```

Le script crée :

- `station`
- `trajet`
- `incident`
- `utilisateur`

Il peut être exécuté plusieurs fois.

Le script est idempotent : il peut être relancé sans créer de doublons.

## Lancement de l'API

Depuis la racine :

```bash
python -m uvicorn api.main:app --reload
```

API :

```text
http://127.0.0.1:8000
```

Documentation Swagger :

```text
http://127.0.0.1:8000/docs
```

Test de santé :

```bash
curl http://127.0.0.1:8000/sante
```

Réponse attendue :

```json
{"statut":"ok"}
```

## Lancement du front Streamlit

Dans un second terminal :

```bash
python -m streamlit run front/app.py
```

Interface :

```text
http://localhost:8501
```

## Routes de l'API

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/sante` | Vérifie que l'API fonctionne |
| `POST` | `/auth/login` |  |
| `GET` | `/stations` | liste de toutes les stations de vélos disponibles dans la base de données |
| `GET` | `/stations/{station_id}` | Retourne le détail d'une station à partir de son identifiant. |
| `GET` | `/trajets` | la liste des trajets importés dans la base |
| `GET` | `/incidents` | la liste des incidents enregistrés dans le système |
| `PUT` | `/incidents/{incident_id}/statut` | l'incident mis à jour |
| `GET` | `/indicateurs/activite-par-jour` | Calcule le nombre de trajets effectués par jour. |
| `GET` | `/indicateurs/stations-actives` | Retourne les stations les plus actives en fonction du nombre de trajets enregistrés. |
| `GET` | `/indicateurs/incidents-par-statut` | Retourne la répartition des incidents par statut. |



## Chiffres clés

Les données nettoyées et chargées en base donnent :

- **120 stations**
- **2002 trajets**
- **180 incidents**

## Tests et couverture

Les tests ont été exécutés avec :

```bash
pytest --cov=api/services --cov-report=term-missing
``` 

Résultats obtenus :
- **21 tests exécutés avec succès**
- **couverture des modules métier : 66 %**

L'objectif fixé dans le sujet est atteint (couverture supérieure ou égale à 60 %).

## Choix écoresponsables
#### Pagination côté serveur

Les listes de stations, trajets et incidents sont paginées côté serveur.
Seul le nombre d'enregistrements demandé est transmis au client, ce qui limite les communications réseau et la quantité de données affichées.
La taille de chaque page est également bornée afin d'éviter les requêtes trop volumineuses.

#### Absence de rafraîchissement automatique

L'application Streamlit ne réalise aucun rafraîchissement automatique, ni mise à jour en temps réel.
Les données sont rechargées à la demande de l'utilisateur, ce qui réduit le nombre de requêtes envoyées à l'API et à la base de données.

#### Agrégations réalisées en SQL

Les indicateurs sont calculés à l'aide de requêtes d'agrégation SQL (COUNT, GROUP BY, ...) ce qui réduit les échanges et la consommation de ressources.

#### Mise en cache des données de référence

La liste des communes est mise en cache avec st.cache_data(ttl=3600).
Les données sont conservées pendant une heure, ce qui évite d'interroger l'API à chaque rechargement de la page et réduit la charge serveur.

#### Dépendances limitées

Le projet utilise uniquement les bibliothèques nécessaires à ses fonctionnalités principales (FastAPI, SQLAlchemy, Streamlit, pandas, requests...).
Cela limite l'empreinte logicielle et facilite la maintenance de l'application.





## Limites connues

- Authentification JWT non implémentée
- Certaines fonctionnalités du back-end liées à l'authentification et aux autorisations restent à implémenter.
- Certaines maquettes Streamlit restent à implémenter
- Les tests d'intégration/recette liés à l'authentification et aux contrôles d'accès restent à développer.

## Auteur
Corinne BAUDENS-JANKOWSKI

## Version
Version 1.0 Novembre 2026

