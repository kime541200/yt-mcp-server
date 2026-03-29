import shutil
from pathlib import Path

from policy_mcp_server._path_utils import _get_workspace_root
from policy_mcp_server.exceptions import SearchError, WorkspaceError
from policy_mcp_server.tools import indexing as indexing_tools


def cleanup_task_data(
    task_id: str,
    *,
    delete_workspace: bool = True,
    delete_vector_index: bool = True,
) -> dict[str, object]:
    """Delete task workspace data and, optionally, its Milvus collection."""
    workspace_result = _skip_result("Workspace cleanup skipped")
    vector_index_result = _skip_result("Vector index cleanup skipped")

    if delete_workspace:
        workspace_result = _cleanup_workspace(task_id)
    if delete_vector_index:
        vector_index_result = _cleanup_vector_index(task_id)

    completed = (
        workspace_result["status"] in {"deleted", "not_found", "skipped"}
        and vector_index_result["status"] in {"deleted", "not_found", "skipped"}
    )
    return {
        "task_id": task_id,
        "workspace": workspace_result,
        "vector_index": vector_index_result,
        "completed": completed,
    }


def _cleanup_workspace(task_id: str) -> dict[str, str]:
    try:
        task_dir = _resolve_task_dir(task_id)
        if not task_dir.exists():
            return {"status": "not_found", "detail": f"Task workspace '{task_id}' does not exist"}
        shutil.rmtree(task_dir)
        return {"status": "deleted", "detail": f"Task workspace '{task_id}' deleted"}
    except WorkspaceError as exc:
        return {"status": "failed", "detail": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive
        return {"status": "failed", "detail": f"Workspace cleanup failed: {exc}"}


def _cleanup_vector_index(task_id: str) -> dict[str, str]:
    try:
        return indexing_tools.delete_index(task_id)
    except SearchError as exc:
        return {"status": "failed", "detail": str(exc)}


def _resolve_task_dir(task_id: str) -> Path:
    root = _get_workspace_root()
    return root / task_id


def _skip_result(detail: str) -> dict[str, str]:
    return {"status": "skipped", "detail": detail}
