# NexloAI - Multi-Clinic AI Receptionist (SaaS Ready)

A production-ready, multi-tenant AI receptionist platform designed for clinics and hospitals. Built with FastAPI, OpenAI, and a modern bilingual (English/Arabic) chat UI.

## 🚀 Key Features
- **Multi-Clinic Support:** Serve multiple clinics from a single deployment using unique slugs (e.g., `/demo/zia-medical-center`).
- **Smart Lead Capture:** Automatically detects booking and handoff requests. Saves data to `leads.csv` and sends real-time Telegram alerts.
- **Auto Quick-Replies:** AI automatically reads the clinic's Knowledge Base and generates smart reply chips for the UI.
- **Admin Control:** Secure `/reload` endpoint to update clinic prompts and knowledge bases without restarting the server.
- **Omnichannel Ready:** Web Chat UI included. WhatsApp Cloud API webhook is pre-configured for Phase 2.
- **Bilingual UI:** Seamless English + Arabic support with RTL text rendering.
- **Markdown Support:** AI responses are beautifully formatted with headings, bullet points, and bold text.

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, Uvicorn
- **AI Engine:** OpenAI API (GPT-4o / GPT-4o-mini)
- **Frontend:** Vanilla HTML/CSS/JS (No build step required)
- **Database:** CSV-based (Easily upgradeable to SQLite/PostgreSQL for production)

## ⚙️ Quick Setup

### 1. Prerequisites
- Python 3.11+ installed on your system.
- An OpenAI API Key.

### 2. Installation
1. Extract the project folder.
2. Open Terminal / Command Prompt in the project folder.
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate