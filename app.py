# app.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="CWC AI Agent")

# Allow requests from your Elementor site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Must be set on Railway

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

async def query_openai(message: str) -> str:
    """Send user message to OpenAI and return the response"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, headers=headers, json=json_data)
        if resp.status_code == 429:
            return "OpenAI: Too many requests, please try again later."
        if resp.status_code != 200:
            return f"OpenAI error {resp.status_code}: {resp.text}"
        data = resp.json()
        return data["choices"][0]["message"]["content"]

@app.api_route("/chat", methods=["POST", "OPTIONS"])
async def chat(request: Request):
    if request.method == "OPTIONS":
        # Handle preflight CORS request
        return JSONResponse(status_code=200, content={})

    data = await request.json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return JSONResponse(content={"reply": "Please send a message."})

    # Query OpenAI asynchronously
    reply_text = await query_openai(user_message)
    return JSONResponse(content={"reply": reply_text})







