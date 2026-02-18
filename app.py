
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="CWC AI Agent - Bilingual LLaMA via Groq")

# CORS settings for Elementor site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your site domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set.")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CWC AI Agent (Bilingual EN/中文) is running. Use /chat to send messages."
    }

# Helper: send message to Groq API
async def query_llama_bilingual(message: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    # Bilingual system prompt with few-shot examples
    system_prompt = (
        "You are the official AI advisor of China West Connector (CWC), expert in China business, trade, suppliers, and regulations. "
        "Answer professionally and clearly, staying on-topic. Always respond in the same language as the user (English or Chinese). "
        "Here are examples:\n\n"
        "Q: How can I find a reliable supplier for electronics in China?\n"
        "A: Use CWC to research verified factories in Shenzhen, Guangzhou, and Chengdu. Check certifications and past clients.\n\n"
        "Q: 我如何找到可靠的中国医疗器械供应商？\n"
        "A: 您可以使用CWC来查找经过验证的供应商，查看资质和历史客户记录，并联系工厂确认生产能力。\n\n"
        "Q: What are the import duties for medical devices from China to the EU?\n"
        "A: Import duties vary by device type, typically 5-10%. Check CE compliance and EU regulations.\n\n"
        "Q: 我可以得到出口物流的协助吗？\n"
        "A: 可以，CWC可以协助安排物流、运输公司和海关文件。"
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    return f"Groq error {resp.status_code}: {resp.text}"
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            await asyncio.sleep(1)
            continue

    return "Groq: Unable to get response, please try again later."

# Chat endpoint
@app.api_route("/chat", methods=["POST", "OPTIONS"])
async def chat(request: Request):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content={})

    data = await request.json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return JSONResponse(content={"reply": "Please send a message."})

    reply_text = await query_llama_bilingual(user_message)
    return JSONResponse(content={"reply": reply_text})

