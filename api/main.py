import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Allow frontend to access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    # Debug print to check if env variable is loaded correctly
    print("OPENROUTER_API_KEY:", OPENROUTER_API_KEY)

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
    data = response.json()
    return {"reply": data["choices"][0]["message"]["content"]}
