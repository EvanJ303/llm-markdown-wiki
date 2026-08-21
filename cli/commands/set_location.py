import json
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_dir))


def set_location(location: Path) -> None:
	try:
		config_path = project_dir / 'config.json'
		with open(config_path, 'r', encoding='utf-8') as f:
			config = json.load(f)

		location_path = Path(location).expanduser().resolve()
		config['vault_location'] = str(location_path)

		with open(config_path, 'w', encoding='utf-8') as f:
			json.dump(config, f, indent=4)
			f.write('\n')

		print(f"Vault location set to '{location_path}'.")
	except Exception as e:
		print(f'Error setting vault location: {e}')
