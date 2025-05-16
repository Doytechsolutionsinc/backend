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

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
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