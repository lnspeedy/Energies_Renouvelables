import os

# Définition de l'arborescence
structure = {
    "data": ["raw/", "processed/"],
    "api": ["main.py"],
    "scripts": ["extract_all.py", "transform_all.py", "schemas.py"],
    "": ["requirements.txt"]
}

def create_structure(base_path, structure):
    for key, value in structure.items():
        path = os.path.join(base_path, key)
        if isinstance(value, dict):  # Cas du dossier "ihm"
            os.makedirs(path, exist_ok=True)
            create_structure(path, value)
        elif isinstance(value, list):
            os.makedirs(path, exist_ok=True)
            for item in value:
                item_path = os.path.join(path, item)
                if item.endswith("/"):
                    os.makedirs(item_path, exist_ok=True)
                else:
                    open(item_path, 'a').close()
        else:
            raise ValueError("Structure inattendue")

if __name__ == "__main__":
    base_dir = "."  # ou change vers un chemin spécifique
    create_structure(base_dir, structure)
    print("✅ Arborescence créée avec succès.")
