# Energies Renouvelables

This project provides a small data pipeline and API exposing processed datasets about renewable energy.

## Overview

- **scripts/** contains extraction and transformation scripts:
  - `extract_all.py` downloads raw data files including French electricity statistics,
    World Bank indicators and a few renewable energy stock prices.
  - `transform_all.py` cleans the raw files and saves partitioned Parquet files.
  - `schemas.py` defines Pandas dtypes used during transformations.
- **api/** exposes a FastAPI service to query processed data stored in `data/processed`.

- **ihm/** contains a small React interface to explore the datasets.

- **data/** contains example raw and processed data.

A small helper script `te.py` can create the project folder structure.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. (Optional) Download new raw data by running:

```bash
python scripts/extract_all.py
```

3. Transform the raw files:

```bash
python scripts/transform_all.py
```

4. Launch the API:

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000` and provides routes to list
available data sources and filter records dynamically.


5. Start the React interface:

```bash
cd ihm
npm install
npm start
```

The interface will open on `http://localhost:3000` and allows you to explore the datasets interactively.


## Notes

The repository includes a sample dataset for demonstration purposes. In a real
project you may want to store the `data/` directory outside of version control.

