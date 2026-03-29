FROM python:3.13-slim

WORKDIR /app

# 安裝 uv（從官方 image 複製二進位檔，比 pip install 更快且更穩定）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 複製依賴檔案
COPY pyproject.toml README.md ./

# 安裝相依套件 (透過 --system 安裝在 container 的 global 環境)
RUN uv pip install --system --no-cache "fastmcp>=2.0.0" "google-api-python-client>=2.0.0" "youtube-transcript-api>=0.6.0" "python-dotenv>=1.0.0" "pyyaml>=6.0.0"

# 複製核心程式碼與設定檔
COPY src/ ./src/
COPY config.yaml ./

# 安裝專案本身
RUN uv pip install --system --no-cache .

EXPOSE 8088

# 預設行為
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8088
ENV MCP_TRANSPORT=http

CMD ["python", "-m", "yt_mcp_server", "--host", "0.0.0.0", "--port", "8088", "--transport", "http"]
