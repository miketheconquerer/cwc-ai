# app.py
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

# Read OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

# Root endpoint (for testing in browser)
@app.get("/")
async def root():
    return {"message": "CWC AI Agent is running. Use /chat to send messages."}

# Helper: send message to OpenAI
async def query_openai(message: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7
    }

    for attempt in range(3):  # retry up to 3 times for 429 errors
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, headers=headers, json=json_data)
            if resp.status_code == 429:
                await asyncio.sleep(2)  # wait 2 seconds and retry
                continue
            if resp.status_code != 200:
                return f"OpenAI error {resp.status_code}: {resp.text}"
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    return "OpenAI: Too many requests, please try again later."

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

    reply_text = await query_openai(user_message)
    return JSONResponse(content={"reply": reply_text})








