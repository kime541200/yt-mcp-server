# Policy MCP Server

Privacy regulation analysis tools via Model Context Protocol (MCP).

Provides tools for navigating, searching, and extracting privacy categories from regulation documents within a task-based workspace.

## Tools

| Tool | Description |
|------|-------------|
| `read_index` | Read the document structure index for a task |
| `read_section` | Read a specific section's Markdown content |
| `search_content` | Full-text and vector search across document sections |
| `get_entity_list` | Get the list of supported iDox entities |
| `save_finding` | Save an analysis finding to disk |
| `get_findings` | Retrieve all saved findings for a task |

## Running

```bash
# HTTP mode (Docker)
python -m policy_mcp_server --host 0.0.0.0 --port 8002 --transport http

# stdio mode (local/IDE)
python -m policy_mcp_server --transport stdio

# Docker
docker-compose up --build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POLICY_WORKSPACE_PATH` | `/app/workspace` | Base directory for task workspaces |
| `ENTITY_LISTS_PATH` | `/app/entity_lists` | Directory containing entity list JSON files |
| `MILVUS_URI` | `http://localhost:19530` | Milvus vector database connection URI |
| `MCP_HOST` | `127.0.0.1` | Host to listen on |
| `MCP_PORT` | `8002` | Port to listen on |
