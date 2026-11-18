"""Tests des fonctions de calcul des indicateurs.

À compléter : vérifier les agrégats sur un jeu de données connu.
"""

from datetime import datetime

from api.models import Incident
from api.services.indicateurs import incidents_par_statut

def test_sante(client):
    response = client.get("/sante")

    assert response.status_code == 200
    assert response.json() == {
        "statut": "ok"
    }
# Test de départ pour vérifier la connextion avec la base de test veloville_test
def test_base_de_test_est_vide(db_session):
    assert db_session.query(Incident).count() == 0


def test_incidents_par_statut_calcule_delai_moyen(
    db_session,
):

    print(
    db_session.query(Incident).count()
)
    # Arrange
    incident_resolu = Incident(
        incident_id="TEST_I001",
        date_signalement=datetime(
            2026, 1, 1, 10, 0, 0
        ),
        cible="velo",
        velo_id="V001",
        station_id=None,
        type_incident="chaine deraillee",
        statut="resolu",
        date_resolution=datetime(
            2026, 1, 2, 10, 0, 0
        ),
        technicien="TECH1",
    )

    incident_ouvert = Incident(
        incident_id="TEST_I002",
        date_signalement=datetime(
            2026, 1, 3, 10, 0, 0
        ),
        cible="velo",
        velo_id="V002",
        station_id=None,
        type_incident="eclairage HS",
        statut="ouvert",
        date_resolution=None,
        technicien=None,
    )

    db_session.add(incident_resolu)
    db_session.add(incident_ouvert)
    db_session.flush()

    # Act
    resultat = incidents_par_statut(
        db_session
    )
    print(resultat)

    # Assert
    assert (
        resultat[
            "delai_moyen_resolution_heures"
        ]
        == 24.0
    )

    statuts = [
        ligne["statut"]
        for ligne in resultat["donnees"]
    ]

    assert "resolu" in statuts
    assert "ouvert" in statuts



def test_incidents_par_statut_sans_resolution(
    db_session,
):
    # Arrange
    incident = Incident(
        incident_id="TEST_I003",
        date_signalement=datetime(
            2026, 1, 1, 10, 0, 0
        ),
        cible="velo",
        velo_id="V003",
        station_id=None,
        type_incident="vandalisme",
        statut="ouvert",
        date_resolution=None,
        technicien=None,
    )

    db_session.add(incident)
    db_session.flush()

    # Act
    resultat = incidents_par_statut(
        db_session
    )
    print(resultat)

    # Assert
    assert (
        resultat[
            "delai_moyen_resolution_heures"
        ]
        is None
    )