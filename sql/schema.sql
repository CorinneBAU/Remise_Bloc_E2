-- Schéma de la base veloville (PostgreSQL 14+).
-- À compléter en respectant le contrat du sujet (types, clés, contraintes).
-- Le script doit être rejouable : prévoir les DROP ... IF EXISTS ou
-- CREATE TABLE IF NOT EXISTS.

DROP TABLE IF EXISTS trajet;
DROP TABLE IF EXISTS incident;
DROP TABLE IF EXISTS station;
DROP TABLE IF EXISTS utilisateur;

-- ---------------------------------------------------------------
-- 1. Table station
-- ---------------------------------------------------------------
CREATE TABLE station (
    station_id VARCHAR(10) PRIMARY KEY,
    nom VARCHAR(30),
    commune VARCHAR(30),
    capacite INTEGER 
        CHECK (capacite > 0),
    latitude NUMERIC(8,5),
    longitude NUMERIC(8,5),
    date_mise_en_service DATE
);

-- ---------------------------------------------------------------
-- 2. Table trajet
-- ---------------------------------------------------------------
CREATE TABLE trajet (
    trajet_id VARCHAR(12) PRIMARY KEY,
    velo_id VARCHAR(8),
    depart_horodatage TIMESTAMP,
    station_depart VARCHAR(10) REFERENCES station(station_id) NOT NULL,
    station_arrivee VARCHAR(10) REFERENCES station(station_id),
    duree_secondes INTEGER 
        CHECK (duree_secondes > 0),
    type_usager VARCHAR(20)
        CHECK (type_usager IN ('abonne', 'occasionnel')),
    usager_ref VARCHAR(10) NULL
);

-- ---------------------------------------------------------------
-- 3. Table incident
-- ---------------------------------------------------------------
CREATE TABLE incident (
    incident_id VARCHAR(12) PRIMARY KEY,
    date_signalement TIMESTAMP,
    cible VARCHAR(10)
        CHECK (cible IN ('velo', 'station')),
    velo_id VARCHAR(8) NULL,    
    station_id VARCHAR(10) REFERENCES station(station_id) NULL,
    type_incident VARCHAR(50) 
        CHECK (type_incident IN ('vandalisme', 'selle abimee', 'eclairage HS', 'chaine deraillee', 'ecran borne illisible', 'pneu creve', 'frein defectueux', 'borne hors service')),
    statut VARCHAR(10) 
        CHECK (statut IN ('ouvert','en_cours','resolu')),
    date_resolution TIMESTAMP NULL,
    technicien VARCHAR(30) NULL
    );

-- ---------------------------------------------------------------
-- 4. Table utilisateur
-- ---------------------------------------------------------------
CREATE TABLE utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE,
    mot_de_passe_hash VARCHAR(255),
    role VARCHAR(20) 
        CHECK (role IN ('exploitant','direction'))
);

-- ---------------------------------------------------------------
-- 5. Index utiles aux filtres et aux indicateurs
-- ---------------------------------------------------------------
-- F2 Consulter les stations, filtrer par commune
CREATE INDEX idx_station_commune
ON station(commune);

-- F4 Consulter les trajets, filtrer par période et par station
CREATE INDEX idx_trajet_depart_horodatage
ON trajet(depart_horodatage);

CREATE INDEX idx_trajet_station_depart
ON trajet(station_depart);

CREATE INDEX idx_trajet_station_arrivee
ON trajet(station_arrivee);

-- F5 Consulter les incidents, filtrer par statut
CREATE INDEX idx_incident_statut
ON incident(statut);

-- F9 Indicateur « incidents par statut » : délai moyen de résolution
CREATE INDEX idx_incident_date_signalement
ON incident(date_signalement);