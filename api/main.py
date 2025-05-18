import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")
if not CURRENCY_API_KEY:
    raise RuntimeError("Missing CURRENCY_API_KEY environment variable")

currency_pattern = re.compile(
    r'(?i)(?:convert|what is|how much is)?\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(?:in|to)\s+([a-zA-Z]+)'
)

currency_aliases = {
    "cedis": "GHS", "ghana": "GHS", "ghs": "GHS",
    "usd": "USD", "dollars": "USD", "dollar": "USD",
    "eur": "EUR", "euro": "EUR", "euros": "EUR",
    "gbp": "GBP", "pounds": "GBP", "pound": "GBP",
    "ngn": "NGN", "naira": "NGN",
    "jpy": "JPY", "yen": "JPY",
    "inr": "INR", "rupees": "INR",
    "cad": "CAD", "canadian": "CAD",
    # Add more aliases as needed
}

async def convert_currency(amount, from_code, to_code):
    # Sample API: CurrencyAPI.com, change URL as per your provider
    url = f"https://api.apilayer.com/exchangerates_data/convert?to={to_code}&from={from_code}&amount={amount}"
    headers = {
        "apikey": CURRENCY_API_KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Currency conversion failed")
        data = response.json()
        return data.get("result")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "").strip()

    if not message:
        raise HTTPException(status_code=400, detail="No message provided")

    match = currency_pattern.search(message)
    if match:
        amount, from_cur, to_cur = match.groups()
        from_code = currency_aliases.get(from_cur.lower(), from_cur.upper())
        to_code = currency_aliases.get(to_cur.lower(), to_cur.upper())
        try:
            result = await convert_currency(float(amount), from_code, to_code)
            if result is not None:
                return {
                    "reply": f"{amount} {from_code} is approximately {result:.2f} {to_code}."
                }
            else:
                return {"reply": "Sorry, I couldn't get the exchange rate right now."}
        except Exception:
            return {"reply": "Currency conversion failed. Please try again later."}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/chatgpt-4o-mini",
                "messages": [{"role": "user", "content": message}]
            },
        )
        if response.status_code != 200:
            return {"error": f"API call failed: {response.text}"}

        data = response.json()
        return {"reply": data["choices"][0]["message"]["content"]}
