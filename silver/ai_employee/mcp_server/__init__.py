"""
MCP Server - Centralized External Action Boundary

This server provides a single point of access for all external actions
(email, LinkedIn, webhooks) with comprehensive logging and audit trails.

Runs on localhost:8765 by default.
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Server",
    description="Centralized External Action Boundary for AI Employee Silver Tier",
    version="1.0.0"
)

# Configuration
MCP_PORT = int(os.getenv("MCP_PORT", "8765"))
MCP_HOST = os.getenv("MCP_HOST", "localhost")
DEFAULT_TIMEOUT_MS = 30000

# Paths
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
MCP_ACTIONS_LOG = LOGS_DIR / "mcp_actions.md"

# Action handlers registry
action_handlers = {}


class ExecuteRequest(BaseModel):
    """Request model for /execute endpoint"""
    action: str
    parameters: dict[str, Any]
    timeout_ms: int = DEFAULT_TIMEOUT_MS
    plan_reference: str | None = None
    approval_reference: str | None = None


class ExecuteResponse(BaseModel):
    """Response model for /execute endpoint"""
    success: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    error_code: str | None = None
    duration_ms: int
    request_id: str


class HealthResponse(BaseModel):
    """Response model for /health endpoint"""
    status: str
    uptime_seconds: int
    version: str


# Server start time for uptime calculation
START_TIME = time.time()


def register_action_handler(action_name: str, handler_func):
    """Register an action handler"""
    action_handlers[action_name] = handler_func
    logger.info(f"Registered action handler: {action_name}")


def log_mcp_action(
    timestamp: str,
    action_type: str,
    request_payload: dict,
    response_payload: dict,
    status: str,
    error_context: str | None,
    duration_ms: int,
    plan_reference: str | None,
    approval_reference: str | None,
):
    """Append action log entry to mcp_actions.md (append-only)"""
    log_entry = f"""
## MCP Action Log Entry

**Timestamp**: {timestamp}
**Action**: {action_type}
**Request**:
```json
{json.dumps(request_payload, indent=2)}
```
**Response**:
```json
{json.dumps(response_payload, indent=2)}
```
**Status**: {status}
**Duration**: {duration_ms}ms
**Plan Reference**: {plan_reference or "N/A"}
**Approval Reference**: {approval_reference or "N/A"}
"""
    if error_context:
        log_entry += f"\n**Error Context**: {error_context}\n"

    with open(MCP_ACTIONS_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)
        f.write("\n---\n")


async def execute_action_with_timeout(
    handler_func,
    parameters: dict,
    timeout_ms: int
) -> dict:
    """Execute action with timeout protection"""
    try:
        result = await asyncio.wait_for(
            handler_func(**parameters),
            timeout=timeout_ms / 1000.0
        )
        return {"success": True, "result": result}
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": f"Action timed out after {timeout_ms}ms",
            "error_code": "TIMEOUT"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "ACTION_FAILED"
        }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = int(time.time() - START_TIME)
    return HealthResponse(
        status="healthy",
        uptime_seconds=uptime,
        version="1.0.0"
    )


@app.post("/execute", response_model=ExecuteResponse)
async def execute_action(request: ExecuteRequest):
    """
    Execute an external action via MCP server.
    
    All external actions (email, LinkedIn, webhooks) MUST go through this endpoint.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    logger.info(f"Executing action: {request.action} (request_id: {request_id})")
    
    # Validate action exists
    if request.action not in action_handlers:
        available_actions = list(action_handlers.keys())
        error_msg = f"Action '{request.action}' not found. Available: {available_actions}"
        log_mcp_action(
            timestamp=timestamp,
            action_type=request.action,
            request_payload=request.model_dump(),
            response_payload={"error": error_msg},
            status="failure",
            error_context="Action not found",
            duration_ms=int((time.time() - start_time) * 1000),
            plan_reference=request.plan_reference,
            approval_reference=request.approval_reference,
        )
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Execute action with timeout
    handler_func = action_handlers[request.action]
    result = await execute_action_with_timeout(
        handler_func,
        request.parameters,
        request.timeout_ms
    )
    
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Log action
    log_mcp_action(
        timestamp=timestamp,
        action_type=request.action,
        request_payload=request.model_dump(),
        response_payload=result,
        status="success" if result["success"] else "failure",
        error_context=result.get("error"),
        duration_ms=duration_ms,
        plan_reference=request.plan_reference,
        approval_reference=request.approval_reference,
    )
    
    # Build response
    response_data = ExecuteResponse(
        success=result["success"],
        result=result.get("result"),
        error=result.get("error"),
        error_code=result.get("error_code"),
        duration_ms=duration_ms,
        request_id=request_id,
    )
    
    if result["success"]:
        logger.info(f"Action {request.action} completed successfully in {duration_ms}ms")
    else:
        logger.warning(f"Action {request.action} failed: {result.get('error')}")
    
    return response_data


@app.get("/actions")
async def list_actions():
    """List available action handlers"""
    return {"actions": list(action_handlers.keys())}


def load_action_handlers():
    """Load and register all action handlers (called after server is fully initialized)"""
    from .actions import register_all_handlers
    register_all_handlers(register_action_handler)


# Load handlers after server is fully initialized
load_action_handlers()


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting MCP Server on {MCP_HOST}:{MCP_PORT}")
    uvicorn.run(app, host=MCP_HOST, port=MCP_PORT)
