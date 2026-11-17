"""Fixtures pytest communes.

À compléter : client TestClient de l'API, jetons pour exploitant01 et direction01,
session de base de données de test. Aucun secret en dur : lire .env.
"""

import os
import pytest

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine_test = create_engine(
    os.environ["TEST_DATABASE_URL"]
)

SessionTest = sessionmaker(
    bind=engine_test,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def db_session():
    connexion = engine_test.connect()

    transaction = connexion.begin()

    session = SessionTest(
        bind=connexion,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session

    finally:
        session.close()
        transaction.rollback()
        connexion.close()