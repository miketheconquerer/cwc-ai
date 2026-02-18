from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random

# Initialize FastAPI
app = FastAPI(title="CWC AI API")

# Allow calls from any website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample responses (lightweight, no heavy AI)
sample_responses = [
    "Hello! How can I help you with China business today?",
    "I can provide guidance on investments, manufacturing, and partnerships in China.",
    "Welcome! Are you an investor, a company, or a government entity?",
    "I’m here to assist with China West Connector services and opportunities."
]

# ---------------------------
# /respond endpoint
# ---------------------------
class Message(BaseModel):
    message: str
    history: list = []

@app.post("/respond")
def respond(data: Message):
    message = data.message
    history = data.history

    if len(history) == 0:
        return {"reply": "Welcome to CWC AI Advisor! Are you an investor, company, or government entity?"}

    # Pick a random response for simplicity
    reply = random.choice(sample_responses)
    return {"reply": reply}

# ---------------------------
# /agent endpoint for Moltbook
# ---------------------------
router = APIRouter()

@router.get("/agent")
def agent_info():
    return {
        "name": "CWC AI Advisor",
        "description": "Senior AI advisor for China West Connector, helping with business, investments, partnerships, and manufacturing in China.",
        "website": "https://www.chinawestconnector.com",
        "tags": ["China", "Business", "Investment", "Manufacturing", "AI"]
    }

app.include_router(router)


   