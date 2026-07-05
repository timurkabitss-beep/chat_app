from fastapi import FastAPI
from backend.routers.auth import router as auth_router
import uvicorn

app = FastAPI(
    title="Chat Application API",
    version="1.0.0"
)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Chat App API!"}