"""Tests d'intégration de l'API avec TestClient.

À compléter : au moins /sante, /auth/login (OK et KO), une route protégée sans jeton
(401), PUT /incidents/{id}/statut avec le rôle direction (403).
"""
def test_sante(client):
    response = client.get("/sante")

    assert response.status_code == 200

    assert response.json() == {
        "statut": "ok"
    }

def test_stations(client):
    response = client.get("/stations")

    assert response.status_code == 200

def test_trajets(client):
    response = client.get("/trajets")

    assert response.status_code == 200

def test_incidents(client):
    response = client.get("/incidents")

    assert response.status_code == 200