FROM python:3.13-slim

WORKDIR /app

# 安裝 uv（從官方 image 複製二進位檔，比 pip install 更快且更穩定）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml README.md ./

RUN uv pip install --system --no-cache "fastmcp>=2.0.0" "pymilvus>=2.5.0"

COPY src/ ./src/

RUN uv pip install --system --no-cache .

RUN mkdir -p /app/workspace /app/entity_lists

COPY entity_lists/ ./entity_lists/

EXPOSE 8002

ENV POLICY_WORKSPACE_PATH=/app/workspace
ENV ENTITY_LISTS_PATH=/app/entity_lists
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8002

CMD ["python", "-m", "policy_mcp_server", "--host", "0.0.0.0", "--port", "8002", "--transport", "http"]
