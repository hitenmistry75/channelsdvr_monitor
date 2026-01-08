import os
import re
import httpx
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional

app = FastAPI(title="Channels DVR Monitor API")

# Configuration from Environment Variables
DVR_IP = os.getenv("DVR_IP", "127.0.0.1")
DVR_URL = f"http://{DVR_IP}:8089"
LOG_PATTERN = re.compile(r'(?P<date>\d{4}/\d{2}/\d{2}) (?P<time>\d{2}:\d{2}:\d{2}\.\d+) \[(?P<category>[^\]]+)\] (?P<message>.*)')

@app.get("/api/status")
async def get_status():
    """Fetches real-time activity from the DVR server."""
    async with httpx.AsyncClient() as client:
        try:
            # Combined status from /dvr and /dvr/files for a richer view
            resp = await client.get(f"{DVR_URL}/dvr")
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

@app.get("/api/logs")
async def get_logs(limit: int = 500, search: Optional[str] = None):
    """Fetches and parses the raw text logs into structured JSON."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{DVR_URL}/log")
            lines = resp.text.splitlines()
            
            parsed = []
            for line in lines:
                match = LOG_PATTERN.match(line)
                if match:
                    data = match.groupdict()
                    # Server-side filtering
                    if search and search.lower() not in data['message'].lower() and search.lower() not in data['category'].lower():
                        continue
                    parsed.append(data)
            
            # Return newest first, limited to user preference
            return parsed[::-1][:limit]
        except Exception as e:
            return [{"category": "ERROR", "message": f"Could not reach DVR: {str(e)}", "date": "-", "time": "-"}]

# Serve the Frontend
app.mount("/assets", StaticFiles(directory="dist"), name="static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("dist/index.html")
