# app.py
import os
import time
import openai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai.error import RateLimitError, OpenAIError

# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = FastAPI(title="CWC AI Agent")

# Allow requests from your Elementor site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your domain like "https://www.chinawestconnector.com"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    if not user_message:
        return JSONResponse(content={"reply": "Please send a message."})

    max_retries = 2  # Number of retries on 429
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
            )
            reply_text = response.choices[0].message.content
            break  # Success, exit the retry loop

        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second and retry
                continue
            reply_text = "AI is receiving too many requests. Please try again in a few seconds."

        except OpenAIError as e:
            reply_text = f"AI encountered an error: {str(e)}"
            break

    return JSONResponse(content={"reply": reply_text})



