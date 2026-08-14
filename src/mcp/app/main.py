from __future__ import annotations

from app.config import get_settings
from app.server import mcp


def main() -> None:
    settings = get_settings()
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = settings.mcp_port
    mcp.run(transport="streamable-http", mount_path="/mcp")


if __name__ == "__main__":
    main()
