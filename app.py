# app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="CWC AI Agent")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    # Temporary echo logic only
    return JSONResponse(content={"reply": f"AI Agent received: {user_message}"})






