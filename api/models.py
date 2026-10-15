"""Modèles ORM SQLAlchemy : Station, Trajet, Incident, Utilisateur.

À compléter : déclarer les quatre tables conformément à sql/schema.sql.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base

class Station(Base):
    __tablename__ = "station"

    station_id: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
    )

    nom: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    commune: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    capacite: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(
        Numeric(8, 5),
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Numeric(8, 5),
        nullable=False,
    )

    date_mise_en_service: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )


class Trajet(Base):
    __tablename__ = "trajet"

    trajet_id: Mapped[str] = mapped_column(
        String(12),
        primary_key=True,
    )

    velo_id: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
    )

    depart_horodatage: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    station_depart: Mapped[str] = mapped_column(
        ForeignKey("station.station_id"),
        nullable=False,
    )

    station_arrivee: Mapped[str | None] = mapped_column(
        ForeignKey("station.station_id"),
        nullable=True,
    )

    duree_secondes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    type_usager: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    usager_ref: Mapped[str | None] = mapped_column(
        String(9),
        nullable=True,
    )


class Incident(Base):
    __tablename__ = "incident"

    incident_id: Mapped[str] = mapped_column(
        String(12),
        primary_key=True,
    )

    date_signalement: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    cible: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    velo_id: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
    )

    station_id: Mapped[str | None] = mapped_column(
        ForeignKey("station.station_id"),
        nullable=True,
    )

    type_incident: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    statut: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    date_resolution: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    technicien: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id_utilisateur: Mapped[int] = mapped_column(
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    mot_de_passe_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )