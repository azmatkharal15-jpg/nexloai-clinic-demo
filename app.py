import os
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from openai import OpenAI

import bot
import whatsapp
from clinic_config import ClinicNotFound, load_clinic, public_config

BASE = Path(__file__).resolve().parent
app = FastAPI(title="NexloAI Multi-Clinic Demo Platform")

# AI Client for Quick Replies
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class ChatIn(BaseModel):
    session_id: str = Field(min_length=8, max_length=100)
    message: str = Field(min_length=1, max_length=4000)
    clinic_slug: str = "zia-medical-center"

def get_clinic(slug: str):
    try:
        return load_clinic(slug)
    except ClinicNotFound:
        raise HTTPException(status_code=404, detail="This clinic demo is not available.") from None
    except ValueError:
        raise HTTPException(status_code=500, detail="Clinic configuration needs administrator review.") from None

@app.get("/")
def home():
    return FileResponse(BASE / "static" / "directory.html")

@app.get("/demo/{clinic_slug}")
def clinic_demo(clinic_slug: str):
    get_clinic(clinic_slug)
    return FileResponse(BASE / "static" / "index.html")

@app.get("/api/clinic/{clinic_slug}")
def clinic_details(clinic_slug: str):
    return public_config(get_clinic(clinic_slug))

# ==========================================
# NEW: Smart Auto Quick Replies Endpoint
# ==========================================
@app.get("/api/clinic/{clinic_slug}/quick-replies")
def get_quick_replies(clinic_slug: str):
    config = get_clinic(clinic_slug)
    kb_path = (BASE / config["knowledge_base_file"]).resolve()
    
    try:
        kb_text = kb_path.read_text(encoding="utf-8")
        prompt = f"""
        Read this clinic knowledge base and generate exactly 3 short, relevant quick-reply button labels for patients.
        - Keep them 2 to 4 words long.
        - Include emojis at the start.
        - Return ONLY a comma-separated list. Example: 🕒 Opening hours, 🦷 Dental braces, 💳 Insurance
        
        Knowledge Base:
        {kb_text[:1500]} 
        """
        
        resp = client.chat.completions.create(
            model=MODEL, 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        text = resp.choices[0].message.content.strip()
        chips = [c.strip() for c in text.split(",") if c.strip()]
        return {"chips": chips[:3]}
    except Exception:
        # Fallback if AI fails
        return {"chips": ["🕒 Opening hours", "📅 Book appointment", "💳 Insurance"]}

@app.post("/chat")
def chat(body: ChatIn):
    print(f"DEBUG: Received request for clinic: {body.clinic_slug}")
    try:
        get_clinic(body.clinic_slug)
        print("DEBUG: Clinic loaded successfully")
        
        reply = bot.ask(f"web-{body.session_id}", body.message, channel="web", clinic_slug=body.clinic_slug)
        print("DEBUG: Bot replied successfully")
        
        return {"reply": reply}
    except Exception as e:
        import traceback
        print("========================================")
        print("🚨 CHAT ERROR OCCURRED 🚨")
        traceback.print_exc() # Yeh poori detail print karega
        print("========================================")
        raise HTTPException(status_code=503, detail=f"Error: {str(e)}") from None
@app.post("/reload")
def reload_prompt(request: Request, clinic_slug: str = "zia-medical-center"):
    expected = os.getenv("ADMIN_TOKEN")
    supplied = request.headers.get("x-admin-token", "")
    if not expected or supplied != expected:
        raise HTTPException(status_code=403, detail="Admin authentication required.")
    return {"ok": True, "chars": bot.reload_system(clinic_slug)}

@app.get("/webhook")
def wa_verify(request: Request):
    challenge = whatsapp.verify(request.query_params)
    if challenge is None:
        return Response(status_code=403)
    return Response(content=challenge, media_type="text/plain")

@app.post("/webhook")
async def wa_incoming(request: Request, background: BackgroundTasks):
    payload = await request.json()
    background.add_task(whatsapp.handle, payload)
    return {"ok": True}