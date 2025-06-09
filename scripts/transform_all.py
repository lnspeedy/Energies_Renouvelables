# ==============================================================================
# SCRIPT DE TRANSFORMATION FINAL ET COMPLET (VERSION PRO)
# ==============================================================================
#
# Rôle : Ce script transforme TOUTES les données brutes valides en "Data Assets"
# propres, fiables et prêts à l'analyse, en appliquant une logique de nettoyage
# qui préserve les valeurs nulles.
#
# ==============================================================================

import pandas as pd
from pathlib import Path
from schemas import SCHEMAS

# --- 1. Configuration des Chemins ---
RAW_DATA_PATH = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DATA_PATH = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)


# --- 2. Fonctions Utilitaires (inchangées) ---
def log_data_quality_report(
    df_before: pd.DataFrame, df_after: pd.DataFrame, source_name: str, key_columns: list
):
    print(f"--- Rapport de Qualité pour '{source_name}' ---")
    rows_before = len(df_before)
    rows_after = len(df_after)
    duplicates_before = (
        df_before.duplicated(subset=key_columns).sum()
        if all(c in df_before.columns for c in key_columns)
        else "N/A"
    )
    print(f"Lignes initiales : {rows_before}")
    if duplicates_before != "N/A" and duplicates_before > 0:
        print(
            f"  - Doublons logiques détectés (basés sur {key_columns}) : {duplicates_before}"
        )
    print(
        f"Lignes finales : {rows_after} ({rows_before - rows_after} lignes supprimées)"
    )
    print("--- Fin du Rapport ---")


def save_as_partitioned_parquet(
    df: pd.DataFrame, source_name: str, partition_cols: list
):
    schema = SCHEMAS.get(source_name)
    if not schema:
        raise ValueError(f"Pas de schéma défini pour '{source_name}'")
    output_path = PROCESSED_DATA_PATH / source_name
    print(f"Sauvegarde de '{source_name}' dans {output_path}...")
    df = df.reindex(columns=schema.keys())
    try:
        df = df.astype(schema)
    except Exception as e:
        print(
            f"AVERTISSEMENT: Impossible d'appliquer le schéma complet pour {source_name}. Erreur: {e}"
        )
    df.to_parquet(
        output_path,
        engine="pyarrow",
        index=False,
        partition_cols=partition_cols,
        existing_data_behavior="overwrite_or_ignore",
    )
    print(f"-> Succès. {len(df)} lignes sauvegardées.")


# --- 3. Fonctions de Traitement pour TOUTES les sources ---


def process_rte(file_path: Path):
    df = pd.read_csv(file_path, delimiter=";", low_memory=False)
    df_raw = df.copy()
    df["event_datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Heure"], format="%Y-%m-%d %H:%M", errors="coerce"
    )
    df.dropna(subset=["event_datetime"], inplace=True)
    df.drop_duplicates(subset=["event_datetime"], keep="first", inplace=True)
    df["annee"] = df["event_datetime"].dt.year
    df["mois"] = df["event_datetime"].dt.month
    energy_cols = [col for col in df.columns if "(MW)" in col]
    for col in energy_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    log_data_quality_report(df_raw, df, "rte", ["Date", "Heure"])
    save_as_partitioned_parquet(df, "rte", ["annee", "mois"])


def process_world_bank(file_path: Path):
    df = pd.read_excel(file_path, sheet_name="Data", skiprows=3, engine="xlrd")
    df_raw = df.copy()
    df_melted = df.melt(
        id_vars=["Country Name", "Country Code"],
        var_name="annee",
        value_name="part_renouvelable_hors_hydro_pct",
    )
    df = df_melted.rename(columns={"Country Name": "pays", "Country Code": "code_pays"})
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
    df.dropna(subset=["annee"], inplace=True)
    df["annee"] = df["annee"].astype(int)
    df.drop_duplicates(subset=["pays", "annee"], keep="first", inplace=True)
    log_data_quality_report(df_raw, df, "world_bank", ["Country Name", "Country Code"])
    save_as_partitioned_parquet(df, "world_bank", ["annee"])


def process_stock_prices(file_path: Path):
    df = pd.read_csv(file_path)
    df_raw = df.copy()
    df = df.rename(
        columns={
            "Date": "date",
            "Open": "ouverture",
            "High": "max_jour",
            "Low": "min_jour",
            "Close": "cloture",
            "Volume": "volume",
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df.dropna(subset=["date", "symbole_action"], inplace=True)
    key_cols = ["date", "symbole_action"]
    df.drop_duplicates(subset=key_cols, keep="first", inplace=True)
    price_cols = ["ouverture", "max_jour", "min_jour", "cloture", "volume"]
    for col in price_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["annee"] = df["date"].dt.year
    log_data_quality_report(df_raw, df, "stock_prices", ["Date", "symbole_action"])
    save_as_partitioned_parquet(df, "stock_prices", ["symbole_action", "annee"])


# --- 4. Orchestrateur Principal ---
def main():
    print("--- DÉMARRAGE DU SCRIPT DE TRANSFORMATION FINAL ---")

    # On active TOUTES les sources qui ont été téléchargées avec succès
    processors = {
        "rte": (RAW_DATA_PATH / "rte_eco2mix.csv", process_rte),
        "world_bank": (RAW_DATA_PATH / "world_bank_renewable.xls", process_world_bank),
        "stock_prices": (RAW_DATA_PATH / "stock_prices.csv", process_stock_prices),
    }

    for source_name, (file_path, process_func) in processors.items():
        print("=" * 60)
        if file_path.exists():
            try:
                process_func(file_path)
            except Exception as e:
                print(
                    f"!!!!!!!! ERREUR FATALE lors du traitement de '{source_name}' !!!!!!!!"
                )
                print(f"Erreur: {e}")
        else:
            print(f"Fichier brut pour '{source_name}' non trouvé. Source ignorée.")

    print("=" * 60)
    print("--- TRANSFORMATION DE TOUTES LES SOURCES TERMINÉE ---")


if __name__ == "__main__":
    main()
