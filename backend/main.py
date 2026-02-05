from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
from hybrid_rag2 import HybridRAG

app = FastAPI(title="Enterprise Chatbot API")

# 1. CORS (Allow React to talk to Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SERVE PDF FILES (UPDATED FIX)
# We now point explicitly to the 'data/pdf' subfolder
# URL will be: http://localhost:8000/static/filename.pdf
# Maps to: backend/data/pdf/filename.pdf
current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_directory = os.path.join(current_dir, "data", "pdf")

# Safety check: Create folder if it doesn't exist (prevents crash)
os.makedirs(pdf_directory, exist_ok=True)

# Mount the specific PDF folder to /static
app.mount("/static", StaticFiles(directory=pdf_directory), name="static")

class QuestionRequest(BaseModel):
    query: str

print("⏳ Booting up AI Engine...")
try:
    bot = HybridRAG()
    print("🚀 AI Engine Online!")
except Exception as e:
    print(f"❌ Failed to start AI Engine: {e}")
    bot = None

@app.post("/api/chat")
async def chat_endpoint(request: QuestionRequest):
    if not bot:
        raise HTTPException(status_code=500, detail="AI Engine is offline")
    try:
        response = bot.ask(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)