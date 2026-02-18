import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="CWC AI Agent - LLaMA via Groq")

# CORS settings for your Elementor site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your site domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set.")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "CWC AI Agent (LLaMA via Groq) is running. Use /chat to send messages."}

# Helper: send message to Groq API
async def query_llama(message: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.1-8b-instant",  # Free-tier model
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are the official AI advisor of China West Connector, "
                    "expert in China business. Answer professionally and clearly."
                )
            },
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }

    for attempt in range(3):  # retry logic
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    return f"Groq error {resp.status_code}: {resp.text}"
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            await asyncio.sleep(1)
            continue

    return "Groq: Unable to get response, please try again later."

# Chat endpoint
@app.api_route("/chat", methods=["POST", "OPTIONS"])
async def chat(request: Request):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content={})

    data = await request.json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return JSONResponse(content={"reply": "Please send a message."})

    reply_text = await query_llama(user_message)
    return JSONResponse(content={"reply": reply_text})

