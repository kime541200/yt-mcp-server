# YouTube Data API v3 獲取與設定指南

本文件說明如何透過 Google Cloud Console 建立並設定 YouTube Data API 金鑰，專用於 **yt-mcp-server** 或相關開發專案。

## 1. 建立 Google Cloud 專案
1. 登入 [Google Cloud Console](https://console.cloud.google.com/)。
2. 點擊左上角專案下拉選單，選擇 **「新專案」**。
3. 設定專案名稱（例如：`shorts-upload`）並點擊 **「建立」**。

## 2. 啟用 YouTube Data API v3
1. 進入 [API 程式庫](https://console.cloud.google.com/apis/library)。
2. 搜尋 **「YouTube Data API v3」**。
3. 點擊進入後，按下藍色的 **「啟用」** 按鈕。



## 3. 建立並限制 API 金鑰 (API Key)
為了確保帳號安全與額度管理，請務必按照以下步驟設定限制：

### A. 產生金鑰
1. 前往 **「API 和服務」 > 「憑證」**。
2. 點擊 **「+ 建立憑證」** 並選擇 **「API 金鑰」**。

### B. 設定安全限制
在「建立 API 金鑰」設定頁面中：
* **名稱**：建議設定為 `yt-mcp-server`。
* **API 限制**：勾選 **「限制金鑰」**，並從下拉選單選擇 **「YouTube Data API v3」**。
    > *註：這可防止此金鑰被用於存取您帳號下的其他 Google 服務。*
* **應用程式限制**：
    * **開發階段**：選擇 **「無」** 以方便在本地環境測試。
    * **生產階段**：建議改為 **「IP 位址」** 並填入伺服器 IP。



## 4. 驗證金鑰是否有效
取得金鑰後（格式通常為 `AIza...`），可以使用瀏覽器貼上以下網址進行快速測試：

```text
https://www.googleapis.com/youtube/v3/videos?part=snippet&id=Ks-_Mh1QhMc&key=您的API金鑰
```

* **成功**：頁面會回傳該影片的 JSON 資訊（標題、描述等）。
* **失敗**：會回傳 `403 Forbidden` 或 `API key not valid` 錯誤訊息。

---

## 5. 常見問題與限制
* **每日額度**：預設為每日 **10,000 點**。
* **成本計算**：
    * `list` (讀取)：1 點
    * `search` (搜尋)：100 點
    * `insert` (上傳/寫入)：50 點
* **安全性**：**切勿**將 API 金鑰直接上傳至 GitHub 等公開版本控制系統。建議使用 `.env` 檔案管理。