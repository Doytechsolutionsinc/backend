# api/chat.py
import json
import os
import httpx

from fastapi import Request
from fastapi.responses import JSONResponse

async def handler(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "")

        api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            return JSONResponse(status_code=500, content={"error": "API key not found"})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
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
            return JSONResponse(status_code=response.status_code, content={"error": response.text})

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

        return JSONResponse(content={"reply": reply})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Required by Vercel to expose the function
handler = handler
