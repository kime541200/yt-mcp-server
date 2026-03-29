---
name: agents-md
description: >
  為任意專案自動生成或更新 AGENTS.md 文件的技能。AGENTS.md 是一種開放格式，讓 AI coding agent（如 Gemini CLI、Claude Code、Cursor、Codex、Jules、Copilot 等）能理解專案的建構方式、測試流程、代碼風格與貢獻規範。
  當用戶說「幫我建立 AGENTS.md」、「生成 agent 規則」、「用 AGENTS.md 設定 AI 規則」、「我的 AI agent 不知道怎麼跑測試」、「幫我寫專案的 AI 指引」，或是提到 agents.md、AGENT.md、.cursorrules、CLAUDE.md、想要設定 AI coding agent 的行為時，請立刻啟用此技能。即使用戶只說「幫 AI 設定規則」也應該觸發。
---

# AGENTS.md 生成技能

## 什麼是 AGENTS.md？

AGENTS.md 是 AI coding agent 的「README」——一個開放標準格式，用來告訴 Gemini CLI、Claude Code、Cursor、OpenAI Codex、Jules、GitHub Copilot 等 AI 助手如何在此專案中工作。它已被超過 60,000 個開源專案採用，並由 Linux Foundation 下的 Agentic AI Foundation 管治。

**核心價值**：AI agent 會讀取此文件，了解如何安裝依賴、執行測試、遵守代碼風格，以及提交 PR——讓每次互動都更精準、更少錯誤。

**作用域規則**：AGENTS.md 適用於其所在目錄及所有子目錄。子目錄的 AGENTS.md 會疊加或覆蓋父目錄的指引。

---

## 工作流程

### 第一步：探索專案結構

在生成任何內容之前，先全面了解這個專案。並行執行以下探索工作：

1. **識別主要語言與框架**
   - 尋找：`package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、`pom.xml`、`*.gemspec`、`composer.json`
   - 讀取這些文件，了解依賴、腳本、語言版本

2. **了解建構與測試系統**
   - 尋找 CI 設定：`.github/workflows/*.yml`、`.gitlab-ci.yml`、`Makefile`、`Justfile`
   - 讀取 `package.json` 的 `scripts`、`pyproject.toml` 的 `[tool.taskipy]`、`Cargo.toml` 的 `[[test]]`

3. **偵測代碼風格規範**
   - 尋找：`.eslintrc*`、`.prettierrc*`、`pyproject.toml [tool.ruff]`、`mypy.ini`、`.clippy.toml`、`rustfmt.toml`
   - 若有 `CONTRIBUTING.md`、`.github/CONTRIBUTING.md`，也一併讀取

4. **讀取現有文件**
   - 讀取 `README.md` 以了解專案概述
   - 若已有 `AGENTS.md`，讀取並計劃做增量更新

5. **分析目錄結構**
   - 使用 `list_dir` 了解主要模組分布
   - 找出 `src/`、`tests/`、`docs/` 等核心目錄

### 第二步：萃取關鍵資訊

讀取文件後，整理以下資訊（這些是 AGENTS.md 的骨幹）：

| 類別 | 需要回答的問題 |
|------|--------------|
| **環境設置** | 如何安裝依賴？需要哪些系統工具？ |
| **開發工作流** | 如何啟動開發伺服器？如何建構？ |
| **測試** | 如何執行所有測試？如何執行單一測試？如何更新快照？ |
| **代碼風格** | 有哪些 linter？格式化工具？命名慣例？ |
| **架構原則** | 有哪些模組？各自職責？有哪些不能違反的設計決策？ |
| **安全考量** | 有無敏感代碼區域？有無沙箱限制？ |
| **PR 規範** | 提交消息格式？PR 標題格式？提交前必做的事？ |

若有任何不確定的資訊（例如找不到測試命令），主動詢問用戶而非猜測。

### 第三步：生成 AGENTS.md

根據研究結果，在專案根目錄生成 `AGENTS.md`。應包含哪些章節取決於專案的實際情況——**只寫有實質內容的章節，不要寫空殼或佔位符**。

請參考 `references/format-guide.md` 了解完整格式規範與各章節範本。
請參考 `references/examples.md` 了解不同技術棧的實際範例。

#### 寫作原則

- **行為導向**：告訴 AI agent「做什麼」和「怎麼做」，而不是解釋背景給人類看
- **命令優先**：使用可以直接複製貼上執行的命令，不要用「你可以用...」這樣的語氣
- **具體而非模糊**：寫「執行 `pytest tests/ -x -v`」而非「執行測試」
- **包含反例**：若有常見的錯誤做法或禁止操作，明確列出（例如「不要用 `sudo pip install`」）
- **Markdown 格式**：使用清晰的標題層級，代碼塊使用反引號並標注語言
- **精簡**：只寫 AI agent 實際需要的資訊，不要複製貼上 README 的所有內容

#### 必須包含的核心章節（若資訊存在）

```markdown
# AGENTS.md

## Project Overview
（可選——只在架構特殊或有重要約束時才寫，1-3 句話）

## Setup
（安裝命令，必須精確可執行）

## Development
（啟動、建構命令）

## Testing
（完整的測試執行方式，包含如何跑單一測試）

## Code Style
（linter、formatter、命名規則、架構慣例）

## Project Structure
（可選——描述重要目錄與模組，幫助 agent 定位代碼）

## Security Notes
（可選——敏感代碼、沙箱限制、禁止操作）

## PR & Commit Guidelines
（提交消息格式、PR 標題、提交前清單）
```

### 第四步：確認與精煉

生成後：
1. 向用戶展示生成的 AGENTS.md
2. 說明每個章節包含什麼，以及為什麼這樣寫
3. 詢問是否有需要補充的專案特有規則或慣例
4. 若有子目錄有不同規範（例如 `packages/frontend/` 有自己的規則），詢問是否需要生成子目錄的 AGENTS.md

### 第五步：設定 Gemini CLI（若用戶使用 Gemini CLI）

Gemini CLI 需要明確設定才能讀取 AGENTS.md。有兩種設定方式：

**全域設定**（對所有專案生效，推薦）：

```json
// ~/.gemini/settings.json
{
  "context": {
    "fileName": [
      "./AGENTS.md"
    ]
  }
}
```

**專案層級設定**（只對當前專案生效）：

```json
// <project-root>/.gemini/settings.json
{
  "context": {
    "fileName": [
      "./AGENTS.md"
    ]
  }
}
```

設定完成後，Gemini CLI 每次啟動時會自動讀取 AGENTS.md 並顯示在 `/memory show` 中。

---

## 特殊場景處理

### 場景：子目錄有不同規範

若專案是 monorepo，在根目錄和各子包目錄分別生成 AGENTS.md：
- 根目錄：全域規則（workspace 命令、整體架構）
- 子目錄：該包特有的規則（覆蓋或補充父目錄）

### 場景：已有 AGENTS.md

讀取現有文件，採用增量更新方式：
- 保留用戶已寫好的內容
- 只補充缺失的章節
- 若發現有過時的命令（例如用 `npm` 但現在是 `pnpm` 專案），詢問用戶是否要更新

### 場景：遷移其他 AI 規則文件

若用戶有 `.cursorrules`、`CLAUDE.md`、`.aider.conf.yml`、`GEMINI.md` 等文件，讀取這些文件的內容，將其整合到 AGENTS.md 中，同時保持格式符合標準。

---

## 參考資源

- `references/format-guide.md`：AGENTS.md 格式規範、章節說明、最佳實踐
- `references/examples.md`：Node.js、Python、Rust、Go 等主流技術棧的完整範例
