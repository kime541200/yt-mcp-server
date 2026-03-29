import json

from policy_mcp_server._path_utils import _get_entity_lists_root
from policy_mcp_server.exceptions import EntityListError


def get_entity_list(list_name: str = "default") -> str:
    """Load and return the supported iDox entity list.

    Reads from {ENTITY_LISTS_PATH}/{list_name}.json and formats
    the result as a human-readable string for the Agent.
    """
    root = _get_entity_lists_root()
    list_path = root / f"{list_name}.json"

    if not list_path.is_file():
        raise EntityListError(
            f"Entity list '{list_name}' not found at {list_path}"
        )

    try:
        data = json.loads(list_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise EntityListError(f"Failed to load entity list '{list_name}': {e}") from e

    entities = data.get("entities", [])
    if not entities:
        return "No entities defined in the entity list."

    grouped: dict[str, list[dict]] = {}
    for ent in entities:
        cat = ent.get("category", "OTHER")
        grouped.setdefault(cat, []).append(ent)

    categories = data.get("categories", {})
    lines = [f"## Supported iDox Entities ({len(entities)} total)\n"]
    for cat, members in grouped.items():
        cat_label = categories.get(cat, cat)
        lines.append(f"### {cat} — {cat_label} ({len(members)})\n")
        for ent in members:
            lines.append(f"- **{ent.get('name', 'Unknown')}**: {ent.get('description', '')}")
        lines.append("")
    return "\n".join(lines)


def load_entity_names(list_name: str = "default") -> set[str]:
    """Load entity names as a set for programmatic matching."""
    root = _get_entity_lists_root()
    list_path = root / f"{list_name}.json"

    if not list_path.is_file():
        return set()

    try:
        data = json.loads(list_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()

    return {ent["name"] for ent in data.get("entities", []) if "name" in ent}
