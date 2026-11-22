import json
from pathlib import Path

from platformdirs import user_config_path


DEFAULT_CONFIG = {
	'min_chunk_tokens': 80,
	'max_chunk_tokens': 600,
	'chunk_overlap': 50,
	'vault_location': 'C:\\Vault',
	'writeable_extensions': ['.md', '.markdown', '.csv', '.json', '.svg', '.txt'],
	'appendable_extensions': ['.md', '.markdown', '.txt'],
}


def get_config_path() -> Path:
	return Path(user_config_path('llm-markdown-wiki', appauthor=False)) / 'config.json'


def load_config() -> dict:
	config_path = get_config_path()
	config_path.parent.mkdir(parents=True, exist_ok=True)
	if not config_path.exists():
		with config_path.open('w', encoding='utf-8') as config_file:
			json.dump(DEFAULT_CONFIG, config_file, indent=4)
			config_file.write('\n')

	with config_path.open(encoding='utf-8') as config_file:
		return json.load(config_file)


def save_config(config: dict) -> None:
	config_path = get_config_path()
	config_path.parent.mkdir(parents=True, exist_ok=True)
	with config_path.open('w', encoding='utf-8') as config_file:
		json.dump(config, config_file, indent=4)
		config_file.write('\n')