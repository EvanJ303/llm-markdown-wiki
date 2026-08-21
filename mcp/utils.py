import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

from storage import Vault

def ensure_wiki_path(path: Path, vault: Vault) -> Path:
    if path.is_absolute():
        resolved_path = path.resolve()
    else:
        resolved_path = (vault.root / path).resolve()

    wiki_root = vault.wiki_path.resolve()
    try:
        resolved_path.relative_to(wiki_root)
    except ValueError as exc:
        raise ValueError(f'document path must be inside the wiki directory: {path}') from exc

    return resolved_path

def ensure_valid_extension(path: Path) -> Path:
    target = Path(path)
    if target.suffix.lower() not in {'.md', '.markdown', '.csv', '.json', '.svg', '.txt'}:
        return target.with_suffix('.md')
    
    return target
