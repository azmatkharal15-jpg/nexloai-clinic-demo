import os
import csv
from datetime import datetime, timezone
from pathlib import Path

import httpx

LEADS_FILE = Path(__file__).resolve().parent / "leads.csv"

def save_csv(kind: str, details: str, channel: str, session_id: str, clinic_id: str = "dr-fathi-emara") -> None:
    new_file = not LEADS_FILE.exists()
    with open(LEADS_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["time_utc", "clinic_id", "type", "channel", "session", "details"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), clinic_id, kind, channel, session_id, details])

def telegram(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        httpx.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", type(e).__name__)

def notify_lead(kind: str, details: str, channel: str, session_id: str, clinic_id: str = "dr-fathi-emara") -> None:
    save_csv(kind, details, channel, session_id, clinic_id=clinic_id)
    label = "New booking request" if kind == "BOOKING" else "Needs human follow-up"
    telegram(f"{label} | clinic={clinic_id} | channel={channel}\n{details}")
