import json
from pathlib import Path

from policy_mcp_server._path_utils import _resolve_task_path, _ensure_task_dir
from policy_mcp_server.exceptions import FindingError, WorkspaceError


def save_finding(
    task_id: str,
    entity: str,
    overlay_text: str,
    redaction_reason: str,
    source_references: list[str],
    idox_support: bool,
) -> str:
    """Save an analysis finding to disk.

    Appends or updates the finding in {task_id}/findings/results.json.
    If an entry with the same entity already exists, it is replaced.
    """
    try:
        findings_dir = _resolve_task_path(task_id, "findings")
    except WorkspaceError:
        task_dir = _ensure_task_dir(task_id)
        findings_dir = task_dir / "findings"

    findings_dir.mkdir(parents=True, exist_ok=True)
    results_path = findings_dir / "results.json"

    existing = _load_findings_list(results_path)

    new_entry = {
        "entity": entity,
        "overlay_text": overlay_text,
        "redaction_reason": redaction_reason,
        "source_references": source_references,
        "idox_support": idox_support,
    }

    updated = False
    for i, entry in enumerate(existing):
        if entry.get("entity") == entity:
            existing[i] = new_entry
            updated = True
            break

    if not updated:
        existing.append(new_entry)

    try:
        results_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        raise FindingError(f"Failed to save finding: {e}") from e

    action = "Updated" if updated else "Saved"
    return f"{action} finding for entity '{entity}'. Total findings: {len(existing)}"


def get_findings(task_id: str) -> str:
    """Retrieve all saved findings for a task.

    Returns a formatted string of all findings, or indicates none exist.
    """
    try:
        results_path = _resolve_task_path(task_id, "findings", "results.json")
    except WorkspaceError:
        return "No findings yet. The task workspace has not been created."

    findings = _load_findings_list(results_path)
    if not findings:
        return "No findings saved yet for this task."

    lines = [f"## Current Findings ({len(findings)} total)\n"]
    for i, entry in enumerate(findings, 1):
        entity = entry.get("entity", "Unknown")
        reason = entry.get("redaction_reason", "N/A")
        refs = ", ".join(entry.get("source_references", []))
        support = "Yes" if entry.get("idox_support") else "No"
        overlay = entry.get("overlay_text", "")

        lines.append(f"### {i}. {entity}")
        lines.append(f"- **Overlay text**: {overlay}")
        lines.append(f"- **Reason**: {reason}")
        lines.append(f"- **References**: {refs}")
        lines.append(f"- **iDox supported**: {support}\n")

    return "\n".join(lines)


def _load_findings_list(results_path: Path) -> list[dict]:
    if not results_path.is_file():
        return []
    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []
