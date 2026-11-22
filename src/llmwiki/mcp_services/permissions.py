from pathlib import Path

from llmwiki.config import load_config
from llmwiki.vault_storage import Vault


def ensure_wiki_path(path: Path, vault: Vault) -> None:
    if path.is_absolute():
        resolved_path = path.resolve()
    else:
        resolved_path = (vault.root / path).resolve()

    wiki_root = vault.wiki_path.resolve()
    try:
        resolved_path.relative_to(wiki_root)
    except ValueError as exc:
        raise ValueError(f'document path must be inside the wiki directory: {path}') from exc


def ensure_valid_extension(path: Path, operation: str) -> None:
    target = Path(path)

    config = load_config()

    extensions_by_operation = {
        'write': config.get('writeable_extensions', []),
        'append': config.get('appendable_extensions', []),
    }
    try:
        approved_extensions = extensions_by_operation[operation]
    except KeyError as exc:
        raise ValueError(f'unsupported operation: {operation}') from exc

    suffix = target.suffix.lower()
    approved_extensions = {extension.lower() for extension in approved_extensions}
    if suffix not in approved_extensions:
        raise ValueError(
            f'file extension {suffix or "<none>"} is not valid for {operation}: {target}'
        )
