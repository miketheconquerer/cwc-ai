# app.py
import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CWC AI Agent")

# Allow requests from your Elementor site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your domain like "https://www.chinawestconnector.com"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your AI API key (can also use Railway environment variable)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    if not user_message:
        return JSONResponse(content={"reply": "No message received."})

    # Call OpenAI API
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(OPENAI_URL, headers=headers, json=payload)
            resp.raise_for_status()
            result = resp.json()
            ai_reply = result["choices"][0]["message"]["content"]
        except Exception as e:
            ai_reply = f"AI error: {str(e)}"

    return JSONResponse(content={"reply": ai_reply})


