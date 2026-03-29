# Policy MCP Server — AGENTS.md

> 本文件提供給 AI 編碼代理（Cursor、Claude Code、Codex 等）閱讀，
> 用於快速理解本專案架構、約定與開發方式。

---

## 專案概覽

**Policy MCP Server** 是基於 [FastMCP](https://gofastmcp.com) 的 MCP（Model Context Protocol）服務，
提供法規文件導覽、章節讀取、搜尋、Entity 清單查詢，以及 findings 寫入與讀取工具。

服務支援：
- `stdio`（本機 IDE / agent 連線）
- `http`（Docker 或遠端部署）

FastMCP 官方文件：<https://gofastmcp.com/llms.txt>

---

## 技術選型

| 項目 | 選擇 | 說明 |
|------|------|------|
| MCP 框架 | `fastmcp` | 使用獨立套件（非舊版 `mcp.server.fastmcp`） |
| 語言 | Python 3.13+ | `requires-python = ">=3.13"` |
| 向量搜尋 | `pymilvus` | `search_content` 可選用 Milvus |
| 套件管理 | `uv` | 本地環境與依賴同步 |
| 打包 | `hatchling` | `pyproject.toml` 定義 |
| 容器化 | Docker + compose | 預設 `http://localhost:8002` |

### FastMCP 使用規範

```python
# ✅ 正確
from fastmcp import FastMCP

# ❌ 錯誤（舊版路徑）
from mcp.server.fastmcp import FastMCP
```

HTTP 啟動方式：

```python
mcp.run(transport="http", host=args.host, port=args.port)
```

---

## 目錄結構

```text
policy-mcp-server/
├── src/policy_mcp_server/
│   ├── __main__.py              # 入口點（CLI）
│   ├── server.py                # FastMCP 實例、tool/resource/route 註冊
│   ├── _path_utils.py           # workspace / entity_lists 路徑處理
│   ├── exceptions.py            # 自訂例外
│   └── tools/
│       ├── document.py          # read_index, read_section
│       ├── search.py            # fulltext + (optional) Milvus search
│       ├── entity.py            # get_entity_list
│       └── findings.py          # save_finding, get_findings
├── entity_lists/default.json    # 預設 entity 清單
├── workspace/                   # 任務資料（runtime）
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── AGENTS.md
```

---

## 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `POLICY_WORKSPACE_PATH` | `/app/workspace` | 任務工作目錄根路徑 |
| `ENTITY_LISTS_PATH` | `/app/entity_lists` | Entity JSON 清單目錄 |
| `MILVUS_URI` | `http://localhost:19530` | Milvus 連線位址（可選） |
| `MCP_HOST` | `127.0.0.1` | HTTP host |
| `MCP_PORT` | `8002` | HTTP port |

---

## 啟動方式

### 本地（uv）

```bash
uv sync --dev
uv run python -m policy_mcp_server --transport stdio
```

或 HTTP：

```bash
uv run python -m policy_mcp_server --transport http --host 127.0.0.1 --port 8002
```

### Docker

```bash
docker-compose up --build
```

健康檢查：

```bash
curl http://127.0.0.1:8002/health
```

---

## MCP Tools 與 Resource

### Tools

| 名稱 | 說明 |
|------|------|
| `read_index(task_id)` | 讀取 `sections/_index.md` |
| `read_section(task_id, section_id)` | 讀取指定章節 Markdown |
| `search_content(task_id, query)` | 全文搜尋 + 可選向量搜尋 |
| `get_entity_list()` | 讀取支援的 iDox Entity 清單 |
| `save_finding(...)` | 儲存或覆蓋某 entity 的 finding |
| `get_findings(task_id)` | 讀取 task 目前 findings |

### Resources

| URI | 說明 |
|-----|------|
| `policy://entity-list` | 以 JSON 回傳預設 entity list |

### Custom Route

| Path | 方法 | 說明 |
|------|------|------|
| `/health` | `GET` | 服務健康檢查 |

---

## Task 資料格式約定

每個 `task_id` 對應 `POLICY_WORKSPACE_PATH/{task_id}` 目錄，主要結構：

```text
{task_id}/
├── sections/
│   ├── _index.md
│   └── {section_id}.md
└── findings/
    └── results.json
```

注意事項：
- `read_*` / `search_*` 依賴 `sections/` 已存在。
- `save_finding` 若 task 不存在會自動建立 task 與 `findings/`。
- `save_finding` 以 `entity` 當唯一鍵，重複寫入會覆蓋。

---

## 開發慣例

- 新增功能時，優先在 `src/policy_mcp_server/tools/` 建立對應模組函式，再於 `server.py` 用 `@mcp.tool` 註冊。
- 工具層（`tools/*.py`）丟出領域例外（如 `SectionError`、`FindingError`），`server.py` 統一轉成可回傳字串。
- 任何路徑存取應透過 `_path_utils.py`，不要在工具內硬編碼根路徑。
- 優先維持同步工具函式（目前專案皆為同步），除非有明確 I/O 並發需求再改 async。

---

## 測試建議

最小整合測試建議覆蓋：
- `list_tools` / `list_resources`
- 每個 tool 的成功與失敗分支
- `policy://entity-list` 可解析為 JSON
- HTTP `/health` 回應 `status=ok`

可使用 FastMCP 官方 `Client` 做 in-memory 測試，避免外部網路依賴。
