---
description: 檢查 Git 改動並使用 commit-message-helper 產生及執行提交。
---

# 任務：Git 提交自動化與訊息生成

你是一個資深工程師，現在需要透過 **commit-message-helper 技能** 協助用戶檢查 Git 狀態並進行提交。

**執行流程：**

1. **啟動技能與現況檢查**：
   - 必須啟動 `auto-skill` 技能。
   - 必須啟動 `commit-message-helper` 技能。
   - 執行 `git status` 與 `git diff HEAD` 檢查目前工作樹中所有改動（包括已暫存與未暫存）。

2. **處理未暫存改動 (Unstaged Changes)**：
   - 如果發現工作樹中有「尚未加入暫存區 (Not staged for commit)」的改動：
     - 使用 `ask_user` (yesno) 詢問用戶：「偵測到未暫存的改動，是否要將所有改動加入暫存區 (git add .)？」。
     - 如果用戶同意，執行 `git add .`。
     - 如果用戶不同意，則僅針對目前已暫存的內容繼續。

3. **撰寫 Commit Message**：
   - 使用 `git diff --staged` 獲取最終暫存區內容。
   - 呼叫 `commit-message-helper` 技能，根據這些內容撰寫符合 Conventional Commits 規範的訊息。

4. **確認並執行提交**：
   - 向用戶展示生成的最終版 Commit Message。
   - 使用 `ask_user` (yesno) 詢問用戶：「是否同意使用此訊息執行提交？」。
   - 如果用戶同意，執行 `git commit -m "<message>"` 並使用 `git status` 確認結果。
   - 如果用戶不同意，詢問是否需要手動修改或取消流程。

**附加指令或上下文：** {{args}}