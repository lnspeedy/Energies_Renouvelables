# scripts/extract_all.py (Version 5 - Robuste et Enrichie)
import requests
from pathlib import Path
import yfinance as yf
import pandas as pd
import zipfile
import io

# --- Configuration ---
RAW_DATA_PATH = Path(__file__).parent.parent / "data" / "raw"
RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

SOURCES = {
    "rte_eco2mix": {
        "url": "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-cons-def/exports/csv?lang=fr&timezone=Europe/Berlin&use_labels=true&delimiter=%3B",
        "filename": "rte_eco2mix.csv",
    },
    "world_bank_renewable": {
        "url": "https://api.worldbank.org/v2/en/indicator/EG.ELC.RNWX.ZS?downloadformat=excel",
        "filename": "world_bank_renewable.xls",
    },
}


# --- Fonctions d'Extraction (avec gestion des ZIP) ---
def download_source(source_name, details):
    try:
        print(f"Téléchargement de '{source_name}'...")
        with requests.get(
            details["url"], headers=HEADERS, timeout=90, stream=True
        ) as response:
            response.raise_for_status()

            output_path = RAW_DATA_PATH / details["filename"]

            if details["filename"].endswith(".zip"):
                print(f"  -> Extraction du fichier ZIP '{details['filename']}'...")
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    csv_files = [
                        f
                        for f in z.infolist()
                        if f.filename.lower().endswith(".csv") and not f.is_dir()
                    ]
                    if not csv_files:
                        raise FileNotFoundError("Aucun fichier CSV trouvé dans le ZIP.")
                    main_csv = max(csv_files, key=lambda f: f.file_size)
                    print(f"     -> Fichier principal détecté : '{main_csv.filename}'")
                    with z.open(main_csv) as source, open(
                        RAW_DATA_PATH / f"{source_name}.csv", "wb"
                    ) as target:
                        target.write(source.read())
            else:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

        print(f"-> Succès pour '{source_name}'.")
    except Exception as e:
        print(f"-> ÉCHEC pour '{source_name}': {e}")


def extract_financial_data():
    print("Téléchargement des données financières...")
    COMPANIES = {
        "VWS.CO": "Vestas Wind Systems",  # CORRIGÉ : Ticker mis à jour
        "FSLR": "First Solar",
        "ORA.PA": "Orsted",
        "ENPH": "Enphase Energy",
    }
    try:
        hist = yf.download(list(COMPANIES.keys()), period="5y", group_by="ticker")
        all_stocks_df = []
        for symbol, name in COMPANIES.items():
            if not hist[symbol].dropna().empty:
                stock_df = hist[symbol].copy()
                stock_df["symbole_action"] = symbol
                stock_df["nom_entreprise"] = name
                all_stocks_df.append(stock_df)

        if all_stocks_df:
            final_df = pd.concat(all_stocks_df).reset_index()
            output_path = RAW_DATA_PATH / "stock_prices.csv"
            final_df.to_csv(output_path, index=False)
            print(f"-> Succès. Données boursières sauvegardées.")
        else:
            print("-> Aucune donnée boursière valide trouvée.")
    except Exception as e:
        print(f"-> ÉCHEC pour les données financières : {e}")


def main():
    print("--- Démarrage de l'extraction des données (Version 5) ---")
    for name, details in SOURCES.items():
        download_source(name, details)
    extract_financial_data()
    print("--- Extraction terminée ---")


if __name__ == "__main__":
    main()
