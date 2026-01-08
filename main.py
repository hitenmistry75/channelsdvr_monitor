import os
import httpx
import re
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Config
DVR_IP = os.getenv("DVR_IP", "127.0.0.1")
DVR_URL = f"http://{DVR_IP}:8089"
LOG_PATTERN = re.compile(r'(?P<date>\d{4}/\d{2}/\d{2}) (?P<time>\d{2}:\d{2}:\d{2}\.\d+) \[(?P<category>[^\]]+)\] (?P<message>.*)')

@app.get("/api/logs")
async def get_logs():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DVR_URL}/log", timeout=5)
            lines = resp.text.splitlines()[-100:]
            parsed = []
            for line in lines:
                match = LOG_PATTERN.match(line)
                if match: parsed.append(match.groupdict())
            return parsed[::-1]
    except Exception as e:
        return [{"category": "ERROR", "message": f"Connect failed: {e}", "date": "", "time": ""}]

@app.get("/api/status")
async def get_status():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DVR_URL}/dvr", timeout=5)
            return resp.json()
    except:
        return {"Activities": []}

# Serve Frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

if os.path.exists(DIST_DIR):
    app.mount("/static", StaticFiles(directory=DIST_DIR), name="static")

@app.get("/{full_path:path}")
async def serve_index(full_path: str):
    return FileResponse(os.path.join(DIST_DIR, "index.html"))
