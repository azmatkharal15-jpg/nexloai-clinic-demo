import os

import httpx

from bot import ask

_seen: set[str] = set()  # duplicate webhook messages se bachne ke liye


def verify(params) -> str | None:
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == os.getenv("WA_VERIFY_TOKEN"):
        return params.get("hub.challenge")
    return None


def send_text(to: str, body: str) -> None:
    url = f"https://graph.facebook.com/v21.0/{os.getenv('WA_PHONE_ID')}/messages"
    r = httpx.post(
        url,
        headers={"Authorization": f"Bearer {os.getenv('WA_TOKEN')}"},
        json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}},
        timeout=20,
    )
    if r.status_code >= 300:
        print("WhatsApp send error:", r.status_code, r.text)


def handle(payload: dict) -> None:
    try:
        value = payload["entry"][0]["changes"][0]["value"]
        messages = value.get("messages")
        if not messages:
            return  # delivery/read status events
        msg = messages[0]
        if msg["id"] in _seen:
            return
        _seen.add(msg["id"])

        sender = msg["from"]
        if msg.get("type") != "text":
            send_text(sender, "Thanks! I can only read text messages at the moment. Please type your question.")
            return

        reply = ask(f"wa-{sender}", msg["text"]["body"], channel="whatsapp")
        send_text(sender, reply)
    except Exception as e:
        print("WhatsApp handler error:", e)