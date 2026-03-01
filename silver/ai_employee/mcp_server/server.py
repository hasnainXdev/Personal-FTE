"""
MCP Server Entry Point

Run with: uv run python -m ai_employee.mcp_server.server
"""

import uvicorn
from . import app

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8765)
