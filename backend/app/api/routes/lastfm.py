from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

LASTFM_API_BASE = "https://ws.audioscrobbler.com/2.0/"
LASTFM_API_KEY_ENV = "LASTFM_API_KEY"

app = FastAPI(title="Last.fm Proxy")

@app.get("/api/lastfm/{method}")
async def lastfm_proxy(method: str, request: Request) -> JSONResponse:
    api_key = os.getenv(LASTFM_API_KEY_ENV)
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=f"Missing environment variable {LASTFM_API_KEY_ENV}",
        )

    params = dict(request.query_params)

    params["method"] = method
    params["api_key"] = api_key
    params["format"] = "json"

    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.get(LASTFM_API_BASE, params=params)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Upstream request failed: {e!s}")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Last.fm returned HTTP {resp.status_code}")

    try:
        data: Any = resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Last.fm returned non-JSON response")

    if isinstance(data, dict) and "error" in data:
        return JSONResponse(status_code=400, content=data)

    return JSONResponse(content=data)
