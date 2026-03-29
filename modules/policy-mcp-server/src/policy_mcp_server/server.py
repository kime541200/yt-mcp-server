import json
import logging
import os

from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from policy_mcp_server.exceptions import (
    EntityListError,
    FindingError,
    SearchError,
    SectionError,
)
from policy_mcp_server.tools import document as doc_tools
from policy_mcp_server.tools import cleanup as cleanup_tools
from policy_mcp_server.tools import entity as entity_tools
from policy_mcp_server.tools import findings as findings_tools
from policy_mcp_server.tools import indexing as indexing_tools
from policy_mcp_server.tools import search as search_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("policy-mcp-server")

_INTERNAL_TOKEN_ENV = "POLICY_INTERNAL_TOKEN"
_INTERNAL_TOKEN_HEADER = "x-policy-internal-token"

mcp = FastMCP(
    name="Policy MCP Server",
    instructions=(
        "Provides tools for navigating and analyzing privacy regulation documents "
        "within task-based workspaces. Use task_id to scope all operations to a "
        "specific regulation analysis task. Start by calling read_index to understand "
        "the document structure, then use read_section, search_content, and "
        "save_finding to systematically extract privacy categories."
    ),
)


class CleanupTaskRequest(BaseModel):
    delete_workspace: bool = True
    delete_vector_index: bool = True


# ── Health check ─────────────────────────────────────────────────────────────

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "policy-mcp-server"})


def _get_internal_token() -> str | None:
    token = os.environ.get(_INTERNAL_TOKEN_ENV)
    return token.strip() if token else None


def _is_internal_request_authorized(request: Request) -> bool:
    configured_token = _get_internal_token()
    if not configured_token:
        return False
    request_token = request.headers.get(_INTERNAL_TOKEN_HEADER)
    return bool(request_token) and request_token == configured_token


@mcp.custom_route("/internal/tasks/{task_id}/cleanup", methods=["POST"])
async def a_cleanup_task_internal(request: Request) -> JSONResponse:
    if not _get_internal_token():
        return JSONResponse(
            {"detail": "POLICY_INTERNAL_TOKEN is not configured"},
            status_code=503,
        )
    if not _is_internal_request_authorized(request):
        return JSONResponse(
            {"detail": "Unauthorized internal cleanup request"},
            status_code=401,
        )

    try:
        raw_body = await request.body()
        payload = CleanupTaskRequest.model_validate(
            json.loads(raw_body.decode("utf-8")) if raw_body else {}
        )
    except json.JSONDecodeError:
        return JSONResponse({"detail": "Invalid JSON body"}, status_code=400)
    except ValidationError as exc:
        return JSONResponse(
            {
                "detail": "Invalid cleanup request",
                "errors": exc.errors(),
            },
            status_code=422,
        )

    task_id = request.path_params.get("task_id")
    if not task_id:
        return JSONResponse({"detail": "Missing task_id"}, status_code=400)

    result = cleanup_tools.cleanup_task_data(
        task_id,
        delete_workspace=payload.delete_workspace,
        delete_vector_index=payload.delete_vector_index,
    )
    return JSONResponse(result)


# ── Document tools ───────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True, "title": "Read Document Index"})
def read_index(task_id: str) -> str:
    """讀取任務的文件結構目錄摘要。

    回傳文件中所有章節的 ID、標題與段落數概覽。
    Agent 應在分析開始時先呼叫此工具了解文件全貌。

    Args:
        task_id: 任務的唯一識別碼。
    """
    try:
        return doc_tools.read_index(task_id)
    except SectionError as e:
        return f"Error: {e}"


@mcp.tool(annotations={"readOnlyHint": True, "title": "Read Section"})
def read_section(task_id: str, section_id: str) -> str:
    """讀取指定章節的完整 Markdown 內容。

    Agent 可按需讀取特定章節，不需要一次讀取所有內容。
    若 section_id 無效，會回傳可用的章節 ID 列表。

    Args:
        task_id: 任務的唯一識別碼。
        section_id: 章節 ID（不含 .md 副檔名）。
    """
    try:
        return doc_tools.read_section(task_id, section_id)
    except SectionError as e:
        return f"Error: {e}"


@mcp.tool(annotations={"destructiveHint": True, "title": "Save Section"})
def save_section(task_id: str, section_id: str, title: str, content: str) -> str:
    """將一個章節的 Markdown 內容儲存到任務的工作區。

    Ingestion Agent 在拆分文件後，應為每個章節呼叫此工具進行儲存。
    章節會儲存為 {task_id}/sections/{section_id}.md。

    Args:
        task_id: 任務的唯一識別碼。
        section_id: 章節 ID（僅限英數字、連字號、底線，如 section_001）。
        title: 章節標題。
        content: 章節的完整 Markdown 內容。
    """
    try:
        return doc_tools.save_section(task_id, section_id, title, content)
    except SectionError as e:
        return f"Error: {e}"


@mcp.tool(annotations={"destructiveHint": True, "title": "Save Index"})
def save_index(task_id: str, content: str) -> str:
    """儲存文件結構索引到任務的工作區。

    Ingestion Agent 在拆分完所有章節後，應呼叫此工具建立目錄索引。
    索引會儲存為 {task_id}/sections/_index.md。

    Args:
        task_id: 任務的唯一識別碼。
        content: 索引的 Markdown 內容（包含所有章節的 ID、標題與摘要）。
    """
    try:
        return doc_tools.save_index(task_id, content)
    except SectionError as e:
        return f"Error: {e}"


# ── Search tools ─────────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True, "title": "Search Content"})
def search_content(task_id: str, query: str) -> str:
    """在法規文件中搜尋相關內容（全文搜尋 + 向量語義搜尋）。

    結合關鍵字比對與語義相似度搜尋，回傳匹配的文字片段及其所在章節。
    適合用於查找跨章節引用、尋找相關條文定義等場景。

    Args:
        task_id: 任務的唯一識別碼。
        query: 搜尋查詢字串。
    """
    try:
        return search_tools.search_content(task_id, query)
    except SearchError as e:
        return f"Error: {e}"


# ── Indexing tools ────────────────────────────────────────────────────────────

@mcp.tool(annotations={"destructiveHint": True, "title": "Index Sections"})
def index_sections(task_id: str) -> str:
    """將任務的所有章節內容向量化並索引到 Milvus 向量資料庫。

    在 Ingestion 完成後呼叫此工具，為後續的語義搜尋建立向量索引。
    若已存在索引會先刪除再重建。需要 Embedding API 和 Milvus 都已配置。

    Args:
        task_id: 任務的唯一識別碼。
    """
    try:
        return indexing_tools.index_sections(task_id)
    except SearchError as e:
        return f"Error: {e}"


# ── Entity tools ─────────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True, "title": "Get Entity List"})
def get_entity_list() -> str:
    """取得 iDox 目前支援的隱私類別（Entity）清單。

    回傳所有支援的 Entity 名稱與描述。Agent 在分析法規時應參考此清單，
    將法規中的隱私類別對應到 iDox Entity，並標記不支援的類別。
    """
    try:
        return entity_tools.get_entity_list()
    except EntityListError as e:
        return f"Error: {e}"


# ── Entity list as MCP Resource ──────────────────────────────────────────────

@mcp.resource("policy://entity-list")
def entity_list_resource() -> str:
    """iDox 支援的隱私類別（Entity）清單 — 以 JSON 格式提供。"""
    from policy_mcp_server._path_utils import _get_entity_lists_root

    root = _get_entity_lists_root()
    list_path = root / "default.json"
    if list_path.is_file():
        return list_path.read_text(encoding="utf-8")
    return json.dumps({"entities": []})


# ── Findings tools ───────────────────────────────────────────────────────────

@mcp.tool(annotations={"destructiveHint": True, "title": "Save Finding"})
def save_finding(
    task_id: str,
    entity: str,
    overlay_text: str,
    redaction_reason: str,
    source_references: list[str],
    idox_support: bool,
) -> str:
    """儲存一個隱私類別分析結果。

    每發現一個需要遮蔽的隱私類別時呼叫此工具。若已存在相同 entity 的結果，
    會以新的內容覆蓋。這樣可以避免 Agent 需要在上下文中記住所有已發現的結果。

    Args:
        task_id: 任務的唯一識別碼。
        entity: 隱私類別名稱（應盡量對應 iDox Entity 清單中的名稱）。
        overlay_text: 遮蔽後顯示的替代文字（如 "Person name"）。
        redaction_reason: 遮蔽理由，應引用具體法規條文。
        source_references: 引用的法規條號列表（如 ["Article 9(1)", "Recital 51"]）。
        idox_support: 此 Entity 是否為 iDox 目前支援的類別。
    """
    try:
        return findings_tools.save_finding(
            task_id, entity, overlay_text, redaction_reason,
            source_references, idox_support,
        )
    except FindingError as e:
        return f"Error: {e}"


@mcp.tool(annotations={"readOnlyHint": True, "title": "Get Findings"})
def get_findings(task_id: str) -> str:
    """取得目前所有已儲存的分析結果。

    回傳此任務中已經透過 save_finding 儲存的所有隱私類別結果。
    Agent 可在彙總階段或檢查進度時使用。

    Args:
        task_id: 任務的唯一識別碼。
    """
    try:
        return findings_tools.get_findings(task_id)
    except FindingError as e:
        return f"Error: {e}"
