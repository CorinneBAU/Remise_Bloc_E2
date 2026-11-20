# Matrice rôles x droits

À compléter : une ligne par route, une colonne par rôle (anonyme, exploitant,
direction), code HTTP attendu en cas de refus.


| Route | Anonyme | Exploitant | Direction
|---|---|---|---|
| `GET /sante`                            | 200      | 200        | 200       |
| `POST /auth/login`                      | 200      | 200        | 200       |
| `GET /stations`                         | 401      | 200        | 200       |
| `GET /stations/{station_id}`            | 401      | 200        | 200       |
| `GET /trajets`                          | 401      | 200        | 200       |
| `GET /incidents`                        | 401      | 200        | 200       |
| `PUT /incidents/{incident_id}/statut`   | 401      | 200        | 403       |
| `GET /indicateurs/activite-par-jour`    | 401      | 200        | 200       |
| `GET /indicateurs/stations-actives`     | 401      | 200        | 200       |
| `GET /indicateurs/incidents-par-statut` | 401      | 200        | 200       |

### Codes de refus : 
- 401 : authentification requise (jeton absent, invalide ou expiré) 
- 403 : utilisateur authentifié mais rôle insuffisant