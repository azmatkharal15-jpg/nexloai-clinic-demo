import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from clinic_config import load_clinic
from notify import notify_lead

load_dotenv()
BASE = Path(__file__).resolve().parent
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI()
MAX_HISTORY = 20
sessions: dict[str, list[dict]] = {}
TAG_RE = re.compile(r"\[(BOOKING|HANDOFF)\]\s*(.*)")
DEFAULT_CLINIC = "zia-medical-center"

def build_system(clinic_slug: str = DEFAULT_CLINIC) -> str:
    config = load_clinic(clinic_slug)
    prompt_path = (BASE / config["prompt_file"]).resolve()
    kb_path = (BASE / config["knowledge_base_file"]).resolve()
    
    prompt = prompt_path.read_text(encoding="utf-8")
    kb = kb_path.read_text(encoding="utf-8")
    
    # Replace all common placeholders dynamically
    replacements = {
        "{{CLINIC_NAME}}": config["name"],
        "{{MAIN_PHONE}}": config.get("phone", ""),
        "{{WHATSAPP_APPOINTMENTS}}": config.get("phone", ""), # Fallback to main phone
        "{{EMERGENCY_NUMBER}}": "998 or 999",
    }
    
    for key, val in replacements.items():
        prompt = prompt.replace(key, str(val))
        kb = kb.replace(key, str(val))
    
    global_rule = """
    Formatting Rules (Strictly Enforced):
    - Use Markdown Elements: You must use proper Markdown syntax for all your outputs so the Frontend UI can render the design correctly.
    - Bold Text: Always use bold text (**like this**) for Product Names, Doctor Names, Service Titles, Key Metrics, and Important Labels.
    - Bullet Points: Always use bullet points (using -) when listing items, features, options, or steps. Do not write lists in a continuous sentence.
    - Headings: Use clear headings (using ###) to structure the information if the response contains multiple sections or a lot of data.
    - No Paragraph Blocks: NEVER write the entire response in one single paragraph. Break down text into short sentences and separate them with double line breaks.
    """
    
    return f"{prompt}\n\n{global_rule}\n\n===== KNOWLEDGE BASE START =====\n{kb}\n===== KNOWLEDGE BASE END ====="

def reload_system(clinic_slug: str = DEFAULT_CLINIC) -> int:
    return len(build_system(clinic_slug))

def ask(session_id: str, user_text: str, channel: str = "web", clinic_slug: str = DEFAULT_CLINIC) -> str:
    config = load_clinic(clinic_slug)
    system = build_system(clinic_slug)
    key = f"{clinic_slug}:{session_id}"
    hist = sessions.setdefault(key, [])
    hist.append({"role": "user", "content": user_text})
    try:
        resp = client.chat.completions.create(
            model=MODEL, max_completion_tokens=1500,
            messages=[{"role": "system", "content": system}] + hist[-MAX_HISTORY:],
        )
        full = (resp.choices[0].message.content or "").strip()
    except Exception:
        if hist and hist[-1].get("role") == "user":
            hist.pop()
        raise
    hist.append({"role": "assistant", "content": full})
    for kind, details in TAG_RE.findall(full):
        notify_lead(kind, details.strip(), channel, key, clinic_id=clinic_slug)
    clean = TAG_RE.sub("", full).strip()
    return clean or "Sorry, could you please rephrase that?"