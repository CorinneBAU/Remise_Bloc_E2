"""Tests unitaires des règles de fiabilisation.

À compléter : un test par règle, cas nominal et cas de rejet.
"""
from api.services.fiabilisation import (
    duree_valide,
    capacite_valide,
    date_coherente,
    station_referencee,
    statut_valide,
    normaliser_horodatage,
    normaliser_statut,
    normaliser_velo_id,
)

from datetime import datetime


def test_duree_valide_acceptee():
    resultat, motif = duree_valide(120)

    assert resultat is True
    assert motif is None


def test_duree_valide_rejetee():
    resultat, motif = duree_valide(0)

    assert resultat is False
    assert motif == "duree_secondes <= 0"


def test_statut_valide_accepte():
    resultat, motif = statut_valide("ouvert")

    assert resultat is True
    assert motif is None


def test_statut_valide_rejete():
    resultat, motif = statut_valide("ferme")

    assert resultat is False
    assert motif == "statut invalide"


def test_capacite_valide_acceptee():
    resultat, motif = capacite_valide(20)

    assert resultat is True
    assert motif is None


def test_capacite_valide_rejetee():
    resultat, motif = capacite_valide(0)

    assert resultat is False
    assert motif == "capacite station <= 0"


def test_date_coherente_acceptee():
    date_signalement = datetime(2026, 1, 1, 10, 0, 0)
    date_resolution = datetime(2026, 1, 2, 10, 0, 0)

    resultat, motif = date_coherente(
        date_signalement,
        date_resolution,
    )

    assert resultat is True
    assert motif is None


def test_date_coherente_rejetee():
    date_signalement = datetime(2026, 1, 2, 10, 0, 0)
    date_resolution = datetime(2026, 1, 1, 10, 0, 0)

    resultat, motif = date_coherente(
        date_signalement,
        date_resolution,
    )

    assert resultat is False
    assert motif == "date_resolution < date_signalement"


def test_station_referencee_acceptee():
    stations = {
        "S001",
        "S002",
        "S003",
    }

    resultat, motif = station_referencee(
        "S001",
        stations,
    )

    assert resultat is True
    assert motif is None


def test_station_referencee_rejetee():
    stations = {
        "S001",
        "S002",
        "S003",
    }

    resultat, motif = station_referencee(
        "S999",
        stations,
    )

    assert resultat is False
    assert motif == "station inexistante dans stations.csv"

def test_normaliser_statut():
    assert normaliser_statut("En cours") == "en_cours"

def test_normaliser_velo_id():
    assert normaliser_velo_id("v1458") == "V1458"

def test_normaliser_horodatage():
    resultat = normaliser_horodatage(
        "2026-01-01 10:00:00"
    )

    assert resultat is not None