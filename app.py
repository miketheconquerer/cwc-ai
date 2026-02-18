import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="CWC AI Agent")

# CORS settings: allow your Elementor site to send requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your site domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read OpenRouter API key from environment variable
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable is not set.")

# Root endpoint (for testing in browser)
@app.get("/")
async def root():
    return {"message": "CWC AI Agent is running. Use /chat to send messages."}

# Helper: send message to Qwen via OpenRouter
async def query_qwen(message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "qwen/qwen-2.5-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are the official AI advisor of China West Connector, expert in China business and cross-border deals."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }

    for attempt in range(3):  # retry up to 3 times
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=json_data)
            if resp.status_code == 429:
                await asyncio.sleep(2)
                continue
            if resp.status_code != 200:
                return f"Qwen error {resp.status_code}: {resp.text}"
            data = resp.json()
            # OpenRouter returns slightly different structure
            return data["choices"][0]["message"]["content"]
    return "Qwen: Too many requests, please try again later."

# Chat endpoint
@app.api_route("/chat", methods=["POST", "OPTIONS"])
async def chat(request: Request):
    if request.method == "OPTIONS":
        # Preflight CORS request
        return JSONResponse(status_code=200, content={})

    data = await request.json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return JSONResponse(content={"reply": "Please send a message."})

    reply_text = await query_qwen(user_message)
    return JSONResponse(content={"reply": reply_text})
