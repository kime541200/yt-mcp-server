# AGENTS.md 各技術棧範例

## Node.js / TypeScript（Next.js + pnpm）

```markdown
# AGENTS.md

## Setup
```bash
pnpm install
cp .env.example .env.local
```

**Prerequisites**: Node.js 20+, pnpm 9+

## Development
```bash
pnpm dev          # 啟動開發伺服器 (localhost:3000)
pnpm build        # 建構生產版本
pnpm start        # 執行生產伺服器
```

## Testing
```bash
pnpm test                           # 執行所有測試
pnpm test -- --watch                 # 監看模式
pnpm test -- --testPathPattern=auth  # 執行特定模組測試
pnpm e2e                            # 執行 Playwright E2E 測試（需先 pnpm dev）
```

測試文件放在 `__tests__/` 或與源碼同目錄的 `*.test.ts` 文件中。

## Code Style
```bash
pnpm lint         # ESLint 檢查
pnpm format       # Prettier 格式化
pnpm typecheck    # TypeScript 型別檢查
```

命名慣例：元件用 PascalCase，hook 以 `use` 為前綴，工具函數 camelCase。
不要在 Server Component 中使用 `useState`/`useEffect`。

## Project Structure
```
src/app/           # Next.js App Router 路由（僅路由邏輯）
src/components/    # 共用 UI 元件
src/features/      # Feature-based 業務模組
src/lib/           # 第三方庫封裝
src/types/         # 全域 TypeScript 類型
```

## PR & Commit Guidelines
提交格式（Conventional Commits）：`feat(scope): 描述`
提交前執行：`pnpm lint && pnpm typecheck && pnpm test`
```

---

## Python（FastAPI + uv）

```markdown
# AGENTS.md

## Setup
```bash
uv sync                    # 安裝所有依賴（含 dev）
cp .env.example .env
```

**Prerequisites**: Python 3.12+, uv

## Development
```bash
uv run uvicorn src.main:app --reload   # 啟動開發伺服器 (localhost:8000)
```

API 文件自動生成於 http://localhost:8000/docs

## Testing
```bash
uv run pytest                          # 執行所有測試
uv run pytest tests/unit/ -x -v       # 只跑單元測試，遇到錯誤立即停止
uv run pytest -k "test_user_login"    # 執行特定測試（依名稱篩選）
uv run pytest --cov=src               # 含覆蓋率報告
```

整合測試需要 Docker（PostgreSQL + Redis）：
```bash
docker compose up -d
uv run pytest tests/integration/
```

## Code Style
```bash
uv run ruff check .        # Lint
uv run ruff format .       # 格式化
uv run mypy src/           # 型別檢查
```

命名慣例（遵循用戶規則）：
- 公開非同步函數：前綴 `a_`（例如 `a_get_user`）
- 內部同步函數：前綴 `_`（例如 `_parse_token`）
- 內部非同步函數：前綴 `_a_`（例如 `_a_fetch_data`）

禁止全域安裝套件。缺少套件時，使用 `uv add <package>` 新增。

## Project Structure
```
src/
├── api/           # FastAPI 路由（只做請求解析與回應格式化）
├── services/      # 業務邏輯層
├── repositories/  # 資料存取層（只有這層可以操作資料庫）
├── models/        # SQLAlchemy 模型
└── schemas/       # Pydantic 模型（請求/回應格式）
```

## PR & Commit Guidelines
提交前執行：`uv run ruff check . && uv run mypy src/ && uv run pytest`
PR 標題格式：`[feat/fix/docs]: 簡短描述`
```

---

## Rust（Cargo）

```markdown
# AGENTS.md

## Setup
```bash
cargo build
```

**Prerequisites**: Rust 1.80+ (使用 `rustup update` 更新)

## Development
```bash
cargo build          # 建構
cargo run            # 執行
cargo run -- --help  # 查看 CLI 選項
```

## Testing
```bash
cargo test                              # 執行所有測試
cargo test -p codex-core                # 執行特定 crate 的測試
cargo test -- --test-thread=1           # 序列執行（整合測試）
cargo test -- user_login                # 執行符合名稱的測試
```

快照測試（使用 `insta`）：
```bash
cargo test
cargo insta review                      # 互動式審查快照變更
cargo insta accept -p <crate-name>      # 接受所有新快照
```

若改動影響可視化輸出，必須更新快照並在 PR 中包含 `.snap` 文件變更。

## Code Style
```bash
cargo fmt                               # 格式化（提交前必跑）
cargo clippy -- -D warnings             # Lint（視警告為錯誤）
```

慣例：
- 有變數可以直接內嵌到 `format!` 時，優先使用內嵌格式
- `match` 語句盡量窮舉，避免使用 wildcard `_`
- 測試使用 `pretty_assertions::assert_eq!`，對整個物件做比對而非逐欄位
- 不要建立只被引用一次的小型輔助方法

## PR & Commit Guidelines
提交前執行：`cargo fmt && cargo clippy -- -D warnings && cargo test`
改動 `Cargo.toml` 後，執行 `cargo update` 更新 `Cargo.lock`。
```

---

## Go

```markdown
# AGENTS.md

## Setup
```bash
go mod download
cp config.example.yaml config.yaml
```

**Prerequisites**: Go 1.22+

## Development
```bash
go run ./cmd/server/            # 啟動伺服器
go run ./cmd/server/ --port=8080
```

## Testing
```bash
go test ./...                   # 執行所有測試
go test ./internal/auth/...     # 執行特定包的測試
go test -run TestUserLogin ./... # 執行特定測試
go test -race ./...             # 執行競態條件測試
go test -cover ./...            # 含覆蓋率
```

整合測試標記為 `//go:build integration`，需要 Docker 才能執行：
```bash
go test -tags integration ./...
```

## Code Style
```bash
gofmt -w .                      # 格式化
go vet ./...                    # 靜態分析
golangci-lint run               # 完整 lint（需安裝）
```

慣例：
- 錯誤必須顯式處理，禁止使用 `_` 忽略錯誤
- 使用 `context.Context` 作為第一個參數（非 struct method 例外）
- 介面定義在使用方（consumer），不在實作方

## PR & Commit Guidelines
提交前：`gofmt -w . && go vet ./... && go test ./...`
提交消息格式：`type(scope): 描述`（例如 `feat(auth): add JWT refresh`）
```

---

## Monorepo（Turborepo + pnpm workspace）

```markdown
# AGENTS.md

## Workspace 說明
這是使用 Turborepo 的 pnpm workspace monorepo。
宇宙真理：從根目錄執行，除非在特定包目錄內工作。

## Setup
```bash
pnpm install                           # 安裝所有包的依賴
```

## 定位特定套件
```bash
pnpm dlx turbo run where <package-name>   # 找到包的路徑
# 每個包的 name 在其 package.json 的 name 字段中定義
```

## Testing
```bash
pnpm turbo run test                    # 執行所有包的測試
pnpm turbo run test --filter=web       # 只執行 web 包的測試
pnpm turbo run test --filter=api...    # 執行 api 及其所有依賴的測試

# 在特定包目錄內：
cd packages/web && pnpm test
```

## Code Style
```bash
pnpm lint                              # 所有包
pnpm turbo run lint --filter=web       # 特定包
```

## 新增套件到 Workspace
```bash
pnpm add <package> --filter web        # 加入 web 包
pnpm add -D <package> -w              # 加入根目錄（工具類）
```

## PR & Commit Guidelines
PR 標題格式：`[<package-name>] 描述`
提交前：`pnpm lint && pnpm turbo run test`
```

---

## Ruby on Rails

```markdown
# AGENTS.md

## Setup
```bash
bundle install
bin/rails db:setup          # 建立資料庫並執行 migrations + seeds
cp config/database.yml.example config/database.yml
```

**Prerequisites**: Ruby 3.3+, PostgreSQL

## Development
```bash
bin/rails server             # localhost:3000
bin/rails console            # Rails REPL
```

## Testing
```bash
bundle exec rspec                       # 執行所有測試
bundle exec rspec spec/models/          # 只跑 model 測試
bundle exec rspec spec/models/user_spec.rb:42   # 執行特定行的測試
```

執行測試前確保測試資料庫是最新的：
```bash
bin/rails db:test:prepare
```

## Code Style
```bash
bundle exec rubocop                    # Lint
bundle exec rubocop -A                 # 自動修復
```

命名慣例：遵循 Rails 慣例，Service Object 放在 `app/services/`，以 `...Service` 命名。

## PR & Commit Guidelines
提交前：`bundle exec rubocop && bundle exec rspec`
```
