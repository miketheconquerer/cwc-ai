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
        user_message = data.get("message", "")
        if not user_message:
            return JSONResponse(content={"reply": "Please send a message."})
    except Exception as e:
        return JSONResponse(content={"reply": f"Invalid request: {str(e)}"})

    print(f"Received message: {user_message}")  # <-- Logging for debug

    # Default reply in case OpenAI fails
    real_reply = "AI is thinking..."

    # Async call to OpenAI with simple retry for rate limits
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
            )
            real_reply = response.choices[0].message.content
            print(f"AI reply: {real_reply}")  # <-- Logging
            break
        except RateLimitError:
            print(f"RateLimitError on attempt {attempt+1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
        except OpenAIError as e:
            real_reply = f"AI error: {str(e)}"
            print(f"OpenAIError: {str(e)}")
            break
        except Exception as e:
            real_reply = f"Unexpected error: {str(e)}"
            print(f"Unexpected error: {str(e)}")
            break

    return JSONResponse(content={"reply": real_reply})





