## Why

為了解決目前缺少一個支援 Python 生態系的 YouTube MCP Server 的問題。現有開源專案 `youtube-mcp-server` 是用 TypeScript 開發，但我們現行的開發架構 (如之前寫的 `policy-mcp-server`) 是建立在 Python 的 FastMCP 框架上。透過 Python `src-layout` 標準重構這個專案，能讓我們統一技術堆疊，並重用熟悉的開發部署流程 (如 `http/SSE` 傳輸與 Docker 部署)。

## What Changes

- 完全重新採用 Python 與 FastMCP 框架實作 YouTube MCP Server。
- 遵循 `python-src-layout` 規範，將核心程式碼放於 `./src/yt_mcp_server`。
- 整合 `google-api-python-client` 提供影片、頻道及播放清單操作工具。
- 整合 `youtube-transcript-api` 免費無 quota 抓取 YouTube 影片字幕。
- 實作多把 YouTube API Key 的自動輪替與額度不足 (quota exceed) 自動切換機制 (Key Pool)。

## Capabilities

### New Capabilities
- `youtube-videos`: 影片基本資訊檢索與進階條件搜尋功能。
- `youtube-transcripts`: 取得指定影片的字幕與逐字稿 (不依賴官方 API quota)。
- `youtube-channels`: 搜尋頻道、取得頻道詳細資訊以及尋找創作者。
- `youtube-playlists`: 取得播放清單內的各項影片與清單細節。

### Modified Capabilities
- (None)

## Impact

- 這是一個全新的獨立專案和新服務。
- 需要 Python 的虛擬環境管理與對應依賴項 (如 `google-api-python-client`, `mcp`, `fastmcp`, `youtube-transcript-api`, `python-dotenv`, `pyyaml` 等)。
- 環境變數 (如 `YOUTUBE_API_KEY`) 統一使用 `.env` 文件與 `python-dotenv` 管理，專案內會提供 `.env.example`。
- 其他頻繁變動之參數與配置抽離至 `config.yaml` 並用 `pyyaml` 載入以利管理。
