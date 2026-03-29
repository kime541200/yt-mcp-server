import os
from pathlib import Path

from policy_mcp_server.exceptions import WorkspaceError


def _get_workspace_root() -> Path:
    workspace_path = os.environ.get("POLICY_WORKSPACE_PATH")
    if not workspace_path:
        raise WorkspaceError("POLICY_WORKSPACE_PATH environment variable is not set")
    return Path(workspace_path)


def _get_entity_lists_root() -> Path:
    entity_path = os.environ.get("ENTITY_LISTS_PATH")
    if not entity_path:
        raise WorkspaceError("ENTITY_LISTS_PATH environment variable is not set")
    return Path(entity_path)


def _resolve_task_path(task_id: str, *sub_paths: str) -> Path:
    """Resolve a path within a task's workspace directory.

    Returns POLICY_WORKSPACE_PATH / {task_id} / {sub_paths...}
    Raises WorkspaceError if the task directory does not exist.
    """
    root = _get_workspace_root()
    task_dir = root / task_id
    if not task_dir.is_dir():
        raise WorkspaceError(f"Task workspace not found: {task_id}")
    return task_dir.joinpath(*sub_paths)


def _ensure_task_dir(task_id: str) -> Path:
    """Ensure the task workspace directory exists, creating it if needed."""
    root = _get_workspace_root()
    task_dir = root / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    return task_dir
