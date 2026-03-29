---
name: python-src-layout
description: "強制並引導 Python 專案使用標準的 src-layout。包含新專案初始化、現有專案遷移以及相關工具（uv, pytest, setuptools）的配置指引。"
license: "MIT. LICENSE.txt has complete terms"
---

# Python src-layout 規範與遷移指引

## 1. 核心原則 (Principles)

在設計或開發 Python 專案時，**必須優先使用 src-layout**。這種佈局能有效防止「匯入混淆」（Import Confusion），確保測試環境與實際安裝後的行為一致。

### src-layout 的優勢：
- **測試可靠性**：強制執行安裝後測試，避免測試到本機開發目錄下的原始碼。
- **匯入隔離**：防止非專案目錄下的檔案被意外匯入。
- **打包精準**：減少打包工具誤將開發工具（如 `tests/`, `tools/`）封裝進發行版本。

---

## 2. 新專案初始化 (Initialization)

建立新專案時，應遵循以下目錄結構：

```text
.
├── pyproject.toml
├── README.md
├── .venv/
├── src/                <-- 所有可匯入的包都放在這裡
│   └── my_package/     <-- 你的套件
│       ├── __init__.py
│       └── main.py
├── tests/              <-- 測試程式與原始碼分離
│   └── test_main.py
└── tools/
```

**操作指令：**
```bash
mkdir -p src/my_package tests
touch src/my_package/__init__.py
```

---

## 3. 佈局遷移：從 flat 轉為 src (Migration)

若現有專案為 `flat-layout`（套件與 `pyproject.toml` 在同級目錄），請執行以下遷移步驟：

### 步驟 A：搬移代碼
1. 建立 `src` 目錄。
2. 將所有「生產環境用的套件資料夾」搬移至 `src/`。

```bash
mkdir src
mv my_package src/
```

### 步驟 B：更新配置 (pyproject.toml)

若使用 **setuptools**，通常會自動偵測，但顯式宣告更安全：

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

若使用 **Hatch** 或 **Poetry**，請確保指定路徑：

```toml
# Hatch 範例
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

### 步驟 C：重新安裝虛擬環境
遷移佈局後，必須重新安裝專案以更新路徑映射：

```bash
# 使用 uv
uv pip install -e .
```

---

## 4. 進階技巧與注意事項

### 在 src-layout 下直接執行 CLI
由於原始碼位於 `src/` 下，直接執行 `python src/my_package/main.py` 可能會失敗。
**最佳做法：** 使用可編輯模式安裝後，透過 `python -m my_package` 執行。

**Hack (若不想安裝就執行)：**
在 `__main__.py` 中加入以下處理（參考 `references/src-layout-vs-flat-layout.rst`）：

```python
import os
import sys

if not __package__:
    # 讓 CLI 可以直接從源碼樹執行
    package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, package_source_path)
```

### 測試配置 (pytest)
使用 `src-layout` 時，建議在根目錄建立 `pytest.ini` 或在 `pyproject.toml` 中配置 `pythonpath`：

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

---

## 5. 守則 (Guardrails)

- **禁止行為**：嚴禁在 `src/` 之外放置可匯入的 Python 模組（除了 `setup.py` 或 `conftest.py` 等工具配置）。
- **自動檢查**：當 Agent 偵測到 `flat-layout` 且專案規模超過單一檔案時，應主動建議遷移至 `src-layout`。
- **隔離原則**：確保 `tests/` 不包含 `__init__.py`，除非有特定的測試套件需求，以避免 `tests` 本身變成一個可匯入的包。

---

## 6. 參考資料

- `references/src-layout-vs-flat-layout.rst`: 詳細的行為差異與動機說明。
