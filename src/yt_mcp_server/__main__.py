"""CLI entrypoint for yt-mcp-server.

Usage:
    # HTTP mode (default)
    python -m yt_mcp_server

    # stdio mode
    python -m yt_mcp_server --transport stdio

    # Custom host/port
    python -m yt_mcp_server --host 0.0.0.0 --port 9090
"""

from __future__ import annotations

import argparse
import os

from yt_mcp_server._config import config
from yt_mcp_server.server import mcp


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="yt-mcp-server",
        description="YouTube MCP Server — YouTube data retrieval tools via Model Context Protocol",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=config.mcp_host,
        help=f"Host IP to listen on (default: {config.mcp_host}, env: MCP_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.mcp_port,
        help=f"Port to listen on (default: {config.mcp_port}, env: MCP_PORT)",
    )
    parser.add_argument(
        "--transport",
        type=str,
        default=config.mcp_transport,
        choices=["http", "stdio"],
        help=f"Transport protocol (default: {config.mcp_transport}, env: MCP_TRANSPORT)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
