
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="CWC AI Agent - Bilingual LLaMA via Groq (Full Answers + Continuation)")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your site domain
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
    return {
        "message": "CWC AI Agent (Bilingual, Full Answers + Continuation) is running. Use /chat to send messages."
    }

# Helper: query Groq LLaMA
async def query_llama(message: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    # Short system prompt to save tokens
    system_prompt = (
        "You are the AI advisor of China West Connector (CWC). "
        "Answer only about China business, suppliers, trade, and regulations. "
        "Respond in the same language as the user."
    )

    async def send_request(prompt_message: str) -> str:
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_message}
            ],
            "temperature": 0.7,
            "max_tokens": 2048  # longer answers
        }

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code != 200:
                        return f"Groq error {resp.status_code}: {resp.text}"
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
            except Exception:
                await asyncio.sleep(1)
                continue
        return "Groq: Unable to get response, please try again later."

    # First response
    answer = await send_request(message)

    # Auto-continuation for truncated answers (check if ends abruptly)
    if answer.endswith(("…", ".", "?", "！", "？")) is False:
        # Ask model to continue
        continuation_prompt = "Please continue your previous answer in the same language."
        extra = await send_request(continuation_prompt)
        answer += " " + extra

    return answer

# Chat endpoint
@app.api_route("/chat", methods=["POST", "OPTIONS"])
async def chat(request: Request):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content={})

    data = await request.json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return JSONResponse(content={"reply": "Please send a message."})

