#!/usr/bin/env python3
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
app = FastAPI()
@app.get("/")
async def root(): return HTMLResponse("<h2>Guardian X-1 Active</h2>")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
