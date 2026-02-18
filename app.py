# app.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Create FastAPI app
app = FastAPI(title="CWC AI Agent")

# CORS middleware: allow your Elementor site to send requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.chinawestconnector.com"],  # replace with your Elementor site
    allow_credentials=True,
    allow_methods=["*"],  # allows OPTIONS, POST, GET, etc.
    allow_headers=["*"],
)

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    # Read OpenAI key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return JSONResponse(content={"reply": "Error: OpenAI API key not set."}, status_code=500)

    # Call OpenAI API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": user_message}],
                    "max_tokens": 500,
                },
                timeout=15.0
            )
        result = response.json()
        reply_text = result["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        reply_text = f"OpenAI API error: {e.response.status_code}"
    except Exception as e:
        reply_text = f"Error: {str(e)}"

    return JSONResponse(content={"reply": reply_text})







