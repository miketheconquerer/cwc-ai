from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from textgenrnn import textgenrnn

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

# Initialize lightweight AI model
chatbot = textgenrnn.TextgenRnn()

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

    # Simple language detection (Chinese / English)
    language = "Chinese" if any(u'\u4e00' <= c <= u'\u9fff' for c in message) else "English"

    system_prompt = f"""
You are a senior advisor from China West Connector.
Language: {language}
You help with China business, manufacturing, energy, investment, and partnerships.
Be concise, professional, and high-trust.
"""

    if len(history) == 0:
        return {"reply": "Welcome to CWC AI Advisor! Are you an investor, company, or government entity?"}

    prompt = f"{system_prompt}\nUser: {message}\nAI:"

    # Generate AI response (lightweight)
    output = chatbot.generate(
        return_as_list=True,
        prefix=message,
        max_gen_length=50
    )[0]

    return {"reply": output}

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
