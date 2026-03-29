import re
from pathlib import Path

from policy_mcp_server._path_utils import _ensure_task_dir, _resolve_task_path
from policy_mcp_server.exceptions import SectionError, WorkspaceError


def read_index(task_id: str) -> str:
    """Read the document structure index for a task.

    Returns the content of {task_id}/sections/_index.md which contains
    a summary of all available sections with their IDs and titles.
    """
    try:
        index_path = _resolve_task_path(task_id, "sections", "_index.md")
    except WorkspaceError as e:
        raise SectionError(str(e)) from e

    if not index_path.is_file():
        raise SectionError(
            f"Index file not found for task '{task_id}'. "
            "The document may not have been ingested yet."
        )
    return index_path.read_text(encoding="utf-8")


def read_section(task_id: str, section_id: str) -> str:
    """Read the full Markdown content of a specific section.

    The section file is located at {task_id}/sections/{section_id}.md.
    """
    try:
        sections_dir = _resolve_task_path(task_id, "sections")
    except WorkspaceError as e:
        raise SectionError(str(e)) from e

    section_path = sections_dir / f"{section_id}.md"
    if not section_path.is_file():
        available = _list_available_sections(sections_dir)
        hint = f" Available sections: {', '.join(available)}" if available else ""
        raise SectionError(
            f"Section '{section_id}' not found for task '{task_id}'.{hint}"
        )
    return section_path.read_text(encoding="utf-8")


_SECTION_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def save_section(task_id: str, section_id: str, title: str, content: str) -> str:
    """Save a section Markdown file to the task workspace.

    Creates {task_id}/sections/{section_id}.md with a YAML-like header
    containing section metadata followed by the content body.
    """
    if not _SECTION_ID_RE.match(section_id):
        raise SectionError(
            f"Invalid section_id '{section_id}'. "
            "Use only alphanumerics, hyphens, and underscores."
        )

    task_dir = _ensure_task_dir(task_id)
    sections_dir = task_dir / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    header = f"---\nsection_id: {section_id}\ntitle: {title}\n---\n\n"
    section_path = sections_dir / f"{section_id}.md"
    section_path.write_text(header + content, encoding="utf-8")

    return f"Section '{section_id}' saved ({len(content)} chars)."


def save_index(task_id: str, content: str) -> str:
    """Save the document structure index for a task.

    Creates {task_id}/sections/_index.md with the provided content.
    """
    task_dir = _ensure_task_dir(task_id)
    sections_dir = task_dir / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    index_path = sections_dir / "_index.md"
    index_path.write_text(content, encoding="utf-8")

    return f"Index saved ({len(content)} chars)."


def _list_available_sections(sections_dir: Path) -> list[str]:
    """List section IDs available in the sections directory."""
    if not sections_dir.is_dir():
        return []
    return sorted(
        p.stem for p in sections_dir.glob("*.md") if p.stem != "_index"
    )
