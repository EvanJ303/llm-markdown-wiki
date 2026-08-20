import sys
import json
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_dir))

from storage import Vault

def init() -> None:
    try:
        config_path = Path(__file__).resolve().parent.parent.parent / 'config.json'
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Try to load vault location from config
        location = config['vault_location']
        vault_path = Path(location).resolve()

        # Initialize the vault
        vault = Vault(vault_path)
        vault.close()

        print(f"Vault initialized at '{vault_path}'.")
    except Exception as e:
        print(f"Error initializing vault: {e}")