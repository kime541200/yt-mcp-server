## Context

我們希望統一團隊內的 MCP Server 技術生態。目前團隊已有使用 FastMCP 與 docker-compose 的 `policy-mcp-server`，而網路上開源的 `youtube-mcp-server` 是用 TypeScript 開發的。為了使用相同的語言和配置並遵循我們自訂的 `python-src-layout` 規範，我們決定重寫此服務為 Python 版本。

## Goals / Non-Goals

**Goals:**
- 提供原 TypeScript 版本 100% 相同功能涵蓋率的 Python 版本 (影片、頻道、字幕、播放清單)。
- 建立具備容錯機制的 YouTube API Key Pool (Quota Exceeded 時自動切換)。
- 專案目錄結構必須嚴格遵守 `python-src-layout` 規範放置於 `src/`。

**Non-Goals:**
- 實作 OAuth2 使用者授權 (User Authorization)，目前僅依賴 API Key 讀取公開資料。
- 開發前端 UI，僅專注於提供 MCP tools 介面。

## Decisions

- **框架選型**: `FastMCP` 作為 MCP Server 核心，因為它對 Python 的支援極佳，並透過 Pydantic 使得 Tool 參數校驗變得簡單。
- **目錄架構**: 嚴格遵守 `python-src-layout`，套件將命名為 `yt_mcp_server`，核心代碼放於 `src/yt_mcp_server`。這樣確保測試隔離與打包穩定。
- **配置與環境變數管理**: 採用 `python-dotenv` 來管理機敏的 `.env` 檔案，並且將其他頻繁變動的系統配置放在 `config.yaml` 用 `pyyaml` 讀取，以增加架構靈活性。
- **YouTube API Client**: 採用官方推薦的 `google-api-python-client`，用以操作基礎資料查詢。
- **免 Quote 字幕庫**: 採用社群開發的 `youtube-transcript-api`，不消耗 Google API 的每日額度，便於長期穩定運行。
- **Key Pool 實作**: 將在初始化時載入多把 API Keys，透過裝飾器或包裝函式捕獲 `HttpError 403 (quotaExceeded)`，並自動重試下個可用的金鑰。

## Risks / Trade-offs

- **[Risk] 非官方字幕 API 套件被 Google 封鎖。**
  → Mitigation: `youtube-transcript-api` 是目前最穩健的開源方案之一，若被封檔會快速有熱心更新；真的不行我們再退回官方要求 OAuth 的取字幕 API。
- **[Risk] FastMCP SSE 的 Docker 支援可能會影響 Port 配置。**
  → Mitigation: 預先規劃好 `Dockerfile` 暴露指定的 port 並正確設置 `HOST=0.0.0.0`。
