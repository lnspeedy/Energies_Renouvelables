"""Backend API exposing processed renewable energy datasets."""

# api/main.py (Version 2.2 - Simplifiée et Corrigée)
import duckdb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi.responses import JSONResponse

# --- Configuration ---
PROCESSED_DATA_PATH = Path(__file__).parent.parent / "data" / "processed"

app = FastAPI(
    title="API - Moteur de Données sur les Énergies Renouvelables",
    description="Sert les données traitées et partitionnées depuis le Data Lake local.",
    version="2.2.0",
)

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Fonctions Utilitaires ---
def get_available_sources():
    if not PROCESSED_DATA_PATH.exists():
        return []
    return sorted([d.name for d in PROCESSED_DATA_PATH.iterdir() if d.is_dir()])


# --- Catalogue de Métadonnées (inchangé) ---
METADATA_CATALOG = {
    "rte": {
        "ID_Source": "FR-RTE-01",
        "Nom_Source": "Réseau de Transport d'Électricité (RTE)",
        "Producteur": "RTE",
        "Nom_Jeu_Donnees": "eCO2mix - Données nationales temps réel",
        "Description": "Données de production d'électricité par filière en France, à une granularité fine (15-30 minutes). Essentiel pour l'analyse du mix énergétique français.",
        "Unites": "MW",
        "Couverture_Temporelle": "Depuis 2012",
        "Format_Fichier": "CSV",
        "Methode_Recuperation": "Téléchargement direct via portail OpenDataSoft",
        "Lien_Acces": "https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/information/",
        "Acces_API": "Oui (Opendatasoft API v2)",
        "Frequence_Maj": "Temps réel",
        "Date_Derniere_Maj": "Continue",
        "Personnes_En_Charge": "Service Open Data RTE",
    },
    "world_bank": {
        "ID_Source": "INT-WB-01",
        "Nom_Source": "La Banque Mondiale",
        "Producteur": "The World Bank Group",
        "Nom_Jeu_Donnees": "Renewable electricity output (% of total electricity output)",
        "Description": "Indicateur macro-économique sur la part de l'électricité produite par des sources renouvelables (hors hydraulique) par pays.",
        "Unites": "%",
        "Couverture_Temporelle": "Annuelle, depuis 1990",
        "Format_Fichier": "XLS",
        "Methode_Recuperation": "Téléchargement direct via portail de données",
        "Lien_Acces": "https://data.worldbank.org/indicator/EG.ELC.RNWX.ZS",
        "Acces_API": "Oui (World Bank Data API)",
        "Frequence_Maj": "Annuelle",
        "Date_Derniere_Maj": "Annuelle",
        "Personnes_En_Charge": "World Bank Data Group",
    },
    "stock_prices": {
        "ID_Source": "FIN-YFIN-01",
        "Nom_Source": "Yahoo Finance",
        "Producteur": "Yahoo!",
        "Nom_Jeu_Donnees": "Données historiques des actions",
        "Description": "Données boursières (OHLCV) pour des entreprises majeures du secteur des énergies renouvelables.",
        "Unites": "Devise locale de la bourse",
        "Couverture_Temporelle": "Historique sur 5 ans",
        "Format_Fichier": "CSV (via librairie)",
        "Methode_Recuperation": "Librairie Python `yfinance`",
        "Lien_Acces": "https://finance.yahoo.com/",
        "Acces_API": "Non officiel (via `yfinance`)",
        "Frequence_Maj": "Quotidienne",
        "Date_Derniere_Maj": "Continue",
        "Personnes_En_Charge": "N/A",
    },
}


# --- Endpoints de l'API ---
@app.get("/")
def read_root():
    return {"message": "API Analytique des Énergies Renouvelables"}

@app.get("/sources", summary="Lister toutes les sources disponibles")
def list_sources() -> list[str]:
    """Return the list of available dataset names."""
    return get_available_sources()

@app.get(
    "/sources_with_metadata", summary="Lister toutes les sources avec leurs métadonnées"
)
def list_sources_with_metadata():
    available_sources = get_available_sources()
    response_data = {
        source: METADATA_CATALOG.get(
            source,
            {"Nom_Source": source, "Description": "Aucune métadonnée disponible."},
        )
        for source in available_sources
    }
    return response_data


@app.get("/data/{source_name}", summary="Récupérer et filtrer les données d'une source")
def get_data_by_source(
    source_name: str,
    limit: int = 1000,
    annee_debut: Optional[int] = None,
    annee_fin: Optional[int] = None,
    pays: Optional[str] = None,
    q: Optional[str] = None,  # 'q' pour une recherche texte libre
):
    available_sources = get_available_sources()
    if source_name not in available_sources:
        raise HTTPException(
            status_code=404, detail=f"Source '{source_name}' non trouvée."
        )

    source_path = PROCESSED_DATA_PATH / source_name
    parquet_glob_path = str(source_path / "**" / "*.parquet")

    try:
        with duckdb.connect(database=":memory:") as con:

            # Construction dynamique et sécurisée de la clause WHERE
            where_clauses = []
            params = []

            # Filtrage par plage d'années (si la colonne 'annee' existe)
            if annee_debut:
                where_clauses.append("try_cast(annee as integer) >= ?")
                params.append(annee_debut)
            if annee_fin:
                where_clauses.append("try_cast(annee as integer) <= ?")
                params.append(annee_fin)

            # Filtrage par pays (recherche insensible à la casse)
            if pays:
                where_clauses.append("pays ILIKE ?")
                params.append(f"%{pays}%")

            # Recherche texte libre sur des colonnes pertinentes
            if q:
                # Cherche dans des colonnes textuelles probables
                text_search_cols = [
                    "title",
                    "abstract",
                    "nom_politique",
                    "nom_centrale",
                ]
                df_cols = (
                    con.execute(
                        f"DESCRIBE SELECT * FROM read_parquet('{parquet_glob_path}')"
                    )
                    .fetchdf()["column_name"]
                    .tolist()
                )
                searchable_cols = [col for col in text_search_cols if col in df_cols]
                if searchable_cols:
                    clauses = [f"{col} ILIKE ?" for col in searchable_cols]
                    where_clauses.append(f"({' OR '.join(clauses)})")
                    for _ in searchable_cols:
                        params.append(f"%{q}%")

            where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            query = f"SELECT * FROM read_parquet('{parquet_glob_path}', hive_partitioning=1) {where_sql} LIMIT ?"
            params.append(limit)

            df = con.execute(query, params).fetchdf()

            df_cleaned = df.astype(object).where(pd.notna(df), None)

            return {
                "source": source_name,
                "count": len(df_cleaned),
                "data": df_cleaned.to_dict("records"),
            }

    except Exception as e:
        import traceback

        print(f"Erreur pour la source '{source_name}':")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne du serveur pour la source '{source_name}': {e}",
        )
