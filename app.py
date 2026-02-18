# app.py
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

# Simple chat endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    # Here is where your AI agent logic goes
    # For now, we just echo the message
    response_text = f"AI Agent received: {user_message}"

    return JSONResponse(content={"reply": response_text})

