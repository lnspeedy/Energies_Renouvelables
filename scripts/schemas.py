# scripts/schemas.py (Version 4 - Enrichie)
SCHEMAS = {
    # --- Sources existantes ---
    
    "rte": {
        "event_datetime": "datetime64[ns]", "annee": "int32", "mois": "int32", "jour": "int32", "Consommation (MW)": "float64",
        "Solaire (MW)": "float64", "Eolien (MW)": "float64", "Hydraulique (MW)": "float64", "Bioénergies (MW)": "float64"
    },
    "world_bank": {
        "pays": "string", "code_pays": "string", "annee": "int32", "part_renouvelable_hors_hydro_pct": "float64"
    },

    "stock_prices": {
        "date": "datetime64[ns]", "nom_entreprise": "string", "symbole_action": "string", "ouverture": "float64",
        "max_jour": "float64", "annee": "int32" , "min_jour": "float64", "cloture": "float64", "volume": "float64"
    },
}