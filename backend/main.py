from fastapi import FastAPI
import json
import uvicorn

app = FastAPI()
@app.get("/status")
async def get_status():
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    return {"status": "pong"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)