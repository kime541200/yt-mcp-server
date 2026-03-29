# AGENTS.md 格式規範

## 文件位置與作用域

```
my-project/
├── AGENTS.md              ← 適用整個專案
├── packages/
│   ├── frontend/
│   │   └── AGENTS.md      ← 只適用 frontend 子目錄（會覆蓋/補充根目錄規則）
│   └── backend/
│       └── AGENTS.md      ← 只適用 backend 子目錄
```

## 標準章節格式

### 專案概覽（Project Overview）

只在以下情況才寫：
- 架構不尋常（例如混合 monorepo + microservices）
- 有重要的環境限制（例如只能在 Docker 中執行）
- 有必須了解的核心約束

```markdown
## Project Overview
這是一個使用 Turborepo 的 monorepo，包含 3 個主要包：`web`（Next.js）、`api`（Fastify）、`shared`（共用類型）。
所有操作都從根目錄執行，除非特別說明。
```

### 環境設置（Setup）

必須包含可直接執行的命令：

```markdown
## Setup
```bash
# 安裝依賴
pnpm install

# 設定環境變數
cp .env.example .env.local

# 啟動資料庫（需要 Docker）
docker compose up -d postgres
```

**Prerequisites**: Node.js 20+, pnpm 9+, Docker
```

### 開發（Development）

```markdown
## Development
```bash
# 啟動開發伺服器
pnpm dev

# 只啟動特定套件
pnpm dev --filter web
```
```

### 測試（Testing）

這是最重要的章節之一——AI agent 最常需要知道如何執行測試：

```markdown
## Testing
```bash
# 執行所有測試
pnpm test

# 執行特定套件的測試
pnpm test --filter api

# 執行單一測試（依名稱篩選）
pnpm vitest run -t "test name"

# 更新快照測試
pnpm test -u
```

在提交前確保所有測試通過。修改任何代碼後，請補充或更新對應的測試。
```

**測試章節的進階寫法**（當有複雜的測試需求時）：

```markdown
## Testing
### 單元測試
```bash
pytest tests/unit/ -x -v
```

### 整合測試（需要 Docker）
```bash
docker compose -f docker-compose.test.yml up -d
pytest tests/integration/ -x
docker compose -f docker-compose.test.yml down
```

### 快照測試
若快照需要更新：
```bash
pytest --snapshot-update
```
提交前必須將快照變更包含在同一個 PR 中。
```

### 代碼風格（Code Style）

列出 linter、formatter 和命名慣例：

```markdown
## Code Style
```bash
# 格式化
pnpm format

# Lint
pnpm lint

# 型別檢查
pnpm typecheck
```

**命名慣例**：
- 元件：PascalCase（`UserProfile.tsx`）
- Hook：camelCase，以 `use` 開頭（`useUserData`）
- 工具函數：camelCase（`formatDate`）
- 常數：SCREAMING_SNAKE_CASE（`MAX_RETRY_COUNT`）

**架構原則**：
- 不要在 `components/` 中直接調用 API，改用 `hooks/`
- Server component 不能使用 `useState` 或 `useEffect`
```

### 專案結構（Project Structure）

只在目錄結構非顯然易懂時才寫：

```markdown
## Project Structure
```
src/
├── app/          # Next.js App Router 頁面
├── components/   # 共用 UI 元件（純展示層）
├── features/     # 功能模組（每個功能一個目錄，含自己的 components/hooks）
├── hooks/        # 全域共用 React hooks
├── lib/          # 第三方庫的配置與封裝
└── types/        # TypeScript 類型定義
```

新增功能請放在 `features/` 中，使用 feature-based 結構。不要在 `app/` 中放業務邏輯。
```

### 安全注意事項（Security Notes）

只在有真實風險或限制時才寫：

```markdown
## Security Notes
- **不要** 修改 `src/auth/` 中的任何文件，這些需要安全審查
- 所有 API 端點必須通過 `middleware/auth.ts` 的驗證
- 環境變數不得硬編碼在代碼中—使用 `.env.local`（已加入 `.gitignore`）
```

### PR 與提交規範（PR & Commit Guidelines）

```markdown
## PR & Commit Guidelines
**提交消息格式**（Conventional Commits）：
```
feat(scope): 簡短描述
fix(scope): 修正什麼
docs: 更新文件
chore: 非功能性改動
```

**提交前清單**：
1. `pnpm lint` — 必須無錯誤
2. `pnpm typecheck` — 必須無錯誤
3. `pnpm test` — 所有測試通過

**PR 標題格式**：`[scope] 簡短描述`
```

---

## 寫作反模式（避免這些錯誤）

### ❌ 太模糊

```markdown
## Testing
執行測試來確保你的改動沒有破壞任何東西。
```

### ✅ 具體可執行

```markdown
## Testing
```bash
npm test                    # 執行所有測試
npm test -- --watch         # 監看模式
npm test -- --testPathPattern="UserProfile"  # 執行特定測試
```
所有測試必須在提交前通過。若修改了 API，也要更新 `tests/api/` 中對應的整合測試。
```

---

### ❌ 複製 README 內容

```markdown
## About
這個專案是一個現代化的 web 應用，使用最新的技術棧...（5 段介紹文字）
```

### ✅ 只寫 agent 需要的信息

```markdown
## Project Overview
Monorepo 結構，根目錄所有命令都通過 `turborepo` 協調。詳見 `turbo.json`。
```

---

## 各語言環境的關鍵命令參考

| 語言/工具 | 安裝 | 測試 | 格式化 | Lint |
|----------|------|------|--------|------|
| Node.js (npm) | `npm install` | `npm test` | `npm run format` | `npm run lint` |
| Node.js (pnpm) | `pnpm install` | `pnpm test` | `pnpm format` | `pnpm lint` |
| Python (uv) | `uv sync` | `uv run pytest` | `uv run ruff format` | `uv run ruff check` |
| Python (pip) | `pip install -e ".[dev]"` | `pytest` | `black .` | `ruff check .` |
| Rust | `cargo build` | `cargo test` | `cargo fmt` | `cargo clippy` |
| Go | `go mod download` | `go test ./...` | `gofmt -w .` | `golangci-lint run` |
| Ruby | `bundle install` | `bundle exec rspec` | `rubocop -A` | `rubocop` |
