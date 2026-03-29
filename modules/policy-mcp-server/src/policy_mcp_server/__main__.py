import argparse
import os

from policy_mcp_server.server import mcp


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Policy MCP Server — privacy regulation analysis tools via MCP"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCP_HOST", "127.0.0.1"),
        help="Host IP to listen on (default: 127.0.0.1, env: MCP_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8002")),
        help="Port to listen on (default: 8002, env: MCP_PORT)",
    )
    parser.add_argument(
        "--transport",
        type=str,
        default="http",
        choices=["http", "stdio"],
        help="Transport protocol (default: http)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
