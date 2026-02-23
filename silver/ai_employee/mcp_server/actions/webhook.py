"""
Webhook Action Handler - HTTP requests and webhook triggers

Handles external HTTP calls through MCP server.
"""

import logging
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


async def fetch_url(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    json_body: dict | None = None,
    timeout_ms: int = 30000,
) -> dict:
    """
    Fetch a URL with specified method and parameters.
    
    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        headers: Optional HTTP headers
        json_body: Optional JSON body for POST/PUT requests
        timeout_ms: Request timeout in milliseconds
    
    Returns:
        dict with status_code, headers, and body
    """
    try:
        logger.info(f"{method} {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=json_body,
                timeout=timeout_ms / 1000.0
            )
            
            # Try to parse JSON response
            try:
                body = response.json()
            except Exception:
                body = response.text
            
            logger.info(f"Response from {url}: {response.status_code}")
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body,
                "url": url,
                "method": method,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code}")
        return {
            "status_code": e.response.status_code,
            "error": str(e),
            "url": url,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}")
        raise ValueError(f"Request to {url} failed: {e}")


async def trigger_webhook(
    webhook_url: str,
    payload: dict,
    method: str = "POST",
    headers: dict | None = None,
    timeout_ms: int = 30000,
) -> dict:
    """
    Trigger a webhook with a payload.
    
    Args:
        webhook_url: Webhook endpoint URL
        payload: Data to send
        method: HTTP method (default: POST)
        headers: Optional additional headers
        timeout_ms: Request timeout in milliseconds
    
    Returns:
        dict with response details
    """
    # Add JSON content-type header by default
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    
    result = await fetch_url(
        url=webhook_url,
        method=method,
        headers=request_headers,
        json_body=payload,
        timeout_ms=timeout_ms
    )
    
    logger.info(f"Webhook triggered: {webhook_url}")
    
    return {
        "webhook_url": webhook_url,
        "payload_sent": payload,
        "response": result,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
