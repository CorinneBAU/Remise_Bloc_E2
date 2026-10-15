"""Point d'entrée de l'API VéloVille (FastAPI).

À compléter : créer l'application, inclure les routeurs (auth, stations, trajets,
incidents, indicateurs) et exposer GET /sante -> {"statut": "ok"}.

Lancement : uvicorn api.main:app --reload
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.stations import router as stations_router
from api.routers.trajets import router as trajets_router
from api.routers.incidents import router as incidents_router


app = FastAPI(
    title="API VéloVille",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# # Routes CRUD pour stations
app.include_router(stations_router)

# # Routes CRUD pour trajets
app.include_router(trajets_router)

# # Routes CRUD pour incidents
app.include_router(incidents_router)

# # Routes d'analyse 
# app.include_router(analyses_router)


@app.get(
    "/sante",
    tags=["sante"],
)
def sante() -> dict[str, str]:
    return {
        "statut": "ok",
    }