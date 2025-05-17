import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MetroTex Backend is Live!"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openchat/openchat-3.5-0106",
        "messages": [{"role": "user", "content": message}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )

    result = response.json()
    return {"reply": result["choices"][0]["message"]["content"]}
