# app.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="CWC AI Agent")

# Allow requests from your Elementor site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your domain like "https://www.chinawestconnector.com"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set!")

# Simple chat endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    
    if not user_message:
        return JSONResponse(content={"reply": "Please provide a message."})

    # Call OpenAI API
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            json_data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": user_message}],
            }
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
            result = response.json()
            reply_text = result["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            content={"reply": f"OpenAI API error: {e.response.status_code}"},
            status_code=500,
        )
    except Exception as e:
        return JSONResponse(
            content={"reply": f"Unexpected error: {str(e)}"},
            status_code=500,
        )

    return JSONResponse(content={"reply": reply_text})



