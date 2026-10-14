# 1 / Schéma de données

À compléter : MLD textuel ou image, description des tables, clés et contraintes,
règles de gestion portées par le schéma.
## MLD textuel

STATION(<u>station_id</u>, nom, commune, capacite, latitude, longitude, date_mise_en_service)

TRAJET(<u>trajet_id</u>, velo_id, depart_horodatage, #station_depart, #station_arrivee, duree_secondes, type_usager, usager_ref)

INCIDENT(<u>incident_id</u>, date_signalement, cible, velo_id, #station_id, type_incident, statut, technicien, date_resolution)

UTILISATEUR(<u>id_utilisateur</u>, username, mot_de_passe_hash, role)


## Table STATION

Description : Référentiel des stations du réseau VeloVille

Clé primaire : 

- station_id

Contraintes :

- station_id NOT NULL

- capacité > 0

## Table TRAJET

Description : Historique des trajets effectués par les usagers du réseau VeloVille

Clé primaire : 

- trajet_id

Cles étrangères :

- station_depart -> station(station_id)
- station_arrivee -> station(station_id)

Contraintes :

- trajet_id NOT NULL

- station_depart NOT NULL

- duree_secondes > 0

- type_usager IN ('abonne', 'occasionnel')

## Table INCIDENT

Description :
Historique des incidents signalés sur les vélos ou les stations du réseau VeloVille

Clé primaire : 

- incident_id

Cles étrangères :

- station_id -> station(station_id) lorsque date_resolution est renseignée

Contraintes :

- incident_id NOT  NULL

- cible IN ('velo', 'station')

- type_incident IN ('vandalisme', 'selle abimee', 'eclairage HS', 'chaine deraillee', 'ecran borne illisible', 'pneu creve', 'frein defectueux', 'borne hors service'),

- statut IN ('ouvert','en_cours','resolu')
- date_resolution >= date_signalement



## Table UTILISATEUR

Description : Comptes d'accès à l'application VeloVille

Clé primaire : 

- id_utilisateur

Contraintes :

- id_utilisateur NOT NULL

- username UNIQUE

- role IN ('exploitant','direction')



# 2 / Règles de gestion portées par le schéma

- RG1 : Une station est identifiée de façon unique par station_id. Sa capacité est un entier strictement positif.
- RG2 : Un trajet relie deux stations du référentiel : la station de départ est obligatoire et doit exister ; la station d'arrivée, lorsqu'elle est renseignée, doit exister.
- RG3 : La station d'arrivée d'un trajet peut être inconnue (vélo non restitué au moment de l'export). Le trajet est conservé ; il ne compte pas comme arrivée pour aucune station.
- RG4 : La durée d'un trajet est un entier strictement positif, exprimé en secondes.
- RG5 : Un trajet d'abonné porte un pseudonyme d'usager (usager_ref) ; un trajet d'usager occasionnel n'en porte pas. Aucune donnée directement identifiante n'est conservée.
- RG6 : Un incident vise soit un vélo, soit une station, jamais les deux ni aucun : cible détermine laquelle des deux références est renseignée. Une station visée doit exister dans le référentiel.
- RG7 : Un incident est dans l'un des trois statuts ouvert, en_cours, resolu. Les transitions autorisées sont ouvert -> en_cours, ouvert -> resolu et en_cours -> resolu. Un incident résolu n'évolue plus.
- RG8 : La date de résolution est renseignée si et seulement si l'incident est résolu, et elle est postérieure ou égale à la date de signalement. Le nom du technicien est attendu dès la prise en charge ; son absence est signalée mais n'empêche pas l'enregistrement.


# 3 / Audit qualité des données

| Fichier | Défaut identifié | Règle | Nombre de lignes | Traitement retenu |
|--------|-----------------|-------|-------------------|-------------------|
|Incidents | statut en majuscule ou 'en cours" au lieu de 'en_cours'|RG7|125|Normalisation
|Incidents |date_résolution < date_signalement|        RG8|3|Rejet
|Trajets |durée <= 0|RG4|10|Rejet
|Trajets |station arrivée inconnue|RG2|7|Rejet
Trajets  |depart_horodatage avec format incorrect |Horodatage AAAA-MM-JJ HH:MM:SS|5|Normalisation
Trajets|doublons ligne entière|Unicité des enregistrements |12|Rejet des doublons
|Trajets|unicité de trajet_id|Primary Key|12|Rejet des doublons|









Les 12 doublons de ligne entière correspondent aux 12 doublons sur l'unicité de trajet_id


Les anomalies détectées ont servi à définir les règles de fiabilisation à appliquer avant l'import en base de données

#