from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# Allow frontend to access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the API key securely from the environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    if not OPENROUTER_API_KEY:
        return {"error": "API key not configured in environment"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openchat/openchat-3.5-0106",
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
        )

    if response.status_code != 200:
        return {"error": f"API call failed: {response.text}"}

    data = response.json()
    return {"reply": data["choices"][0]["message"]["content"]}
