# app.py
import os
import asyncio
import openai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai.error import RateLimitError, OpenAIError

# Load OpenAI API key from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = FastAPI(title="CWC AI Agent")

# Allow requests from your Elementor site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(content={"reply": "Invalid request."})

    user_message = data.get("message", "")
    if not user_message:
        return JSONResponse(content={"reply": "Please send a message."})

    # Placeholder reply for immediate UI feedback
    reply_text = "AI is thinking..."

    # Generate the real AI response with async retry
    real_reply = reply_text  # default if OpenAI fails
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
            )
            real_reply = response.choices[0].message.content
            break
        except RateLimitError:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # <-- async sleep
        except OpenAIError as e:
            real_reply = f"AI error: {str(e)}"
            break

    return JSONResponse(content={"reply": real_reply})





