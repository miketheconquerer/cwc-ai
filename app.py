from agent import router as agent_router
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline

# Initialize app
app = FastAPI(title="CWC AI API")

# Allow CORS for embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load lightweight model
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-small")

# Serve index.html
@app.get("/", response_class=HTMLResponse)
def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# API endpoint
class Message(BaseModel):
    message: str
    history: list = []

@app.post("/respond")
def respond(data: Message):
    message = data.message
    history = data.history

    # Detect language
    language = "Chinese" if any(u'\u4e00' <= c <= u'\u9fff' for c in message) else "English"

    system_prompt = f"""
You are a senior advisor from China West Connector.
Language: {language}
You help with China business, manufacturing, energy, investment, and partnerships.
Be concise, professional, and high-trust.
"""

    # First-time message
    if len(history) == 0:
        reply = "Welcome to CWC AI Advisor! Are you an investor, company, or government entity?"
        history.append({"user": message, "ai": reply})
        return {"reply": reply, "history": history}

    prompt = f"{system_prompt}\nUser: {message}\nAI:"
    output = chatbot(prompt, max_length=200, do_sample=True)[0]["generated_text"]
    reply = output.split("AI:")[-1].strip()

    # Append to history
    history.append({"user": message, "ai": reply})

    return {"reply": reply, "history": history}
app.include_router(agent_router)



