# CareCloud Voice AI Agent — Patient Registration System

A fully functional voice AI agent that registers patients over the phone through natural
conversation, persists records to a database, and exposes them via a REST API.

---

## Live Demo

| Resource        | Value                                      |
|-----------------|--------------------------------------------|
| 📞 Phone Number | `+1 (802) 636 9603|
| 🌐 API Base URL | `https://YOUR-APP.railway.app`             |

---

## Architecture

```
Caller (PSTN)
    │
    ▼
Vapi Telephony (STT → LLM → TTS)
    │  Tool calls (HTTP POST)
    ▼
FastAPI Backend (Railway)
    │
    ├── POST /vapi/webhook   ← tool handler (check_existing_patient, save_patient)
    ├── GET  /patients       ← list + filter
    ├── GET  /patients/:id   ← single record
    ├── POST /patients       ← create
    ├── PUT  /patients/:id   ← update
    └── DELETE /patients/:id ← soft delete
    │
    ▼
SQLite Database (carecloud.db — persistent on Railway volume)
```

---

## Tech Stack

| Layer            | Choice              | Justification                                                  |
|------------------|---------------------|----------------------------------------------------------------|
| Telephony + Voice | Vapi               | Handles STT/TTS/telephony in one platform; fastest integration |
| LLM              | Groq + Llama 3.3 70B | Free tier, ultra-low latency (critical for voice UX)          |
| Backend          | FastAPI (Python)    | Fast to write, async, auto-generates OpenAPI docs              |
| Database         | SQLite + SQLAlchemy | Zero-config, survives restarts, trivially swappable to Postgres|
| Hosting          | Railway             | One-command Python deploys, free tier, instant HTTPS           |

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- A [Vapi](https://vapi.ai) account
- A [Groq](https://console.groq.com) API key
- A [Railway](https://railway.app) account

### Local Development

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/carecloud-voice-agent
cd carecloud-voice-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and VAPI_API_KEY

# 5. Run the server
uvicorn app.main:app --reload --port 8000

# API is now live at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Deploy to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard or via CLI:
railway variables set GROQ_API_KEY=your_key_here
```

### Vapi Configuration

1. Create a new Assistant in the Vapi dashboard
2. Set **Model Provider** to `Groq`, model `llama-3.3-70b-versatile`
3. Paste the contents of `VAPI_SYSTEM_PROMPT.md` into the System Prompt field
4. Set **Voice** to any ElevenLabs or PlayHT voice (recommended: Rachel or Joanna)
5. Add two custom tools from `VAPI_TOOLS.md`:
   - `check_existing_patient` → Server URL: `https://YOUR-APP.railway.app/vapi/webhook`
   - `save_patient` → Server URL: `https://YOUR-APP.railway.app/vapi/webhook`
6. Purchase/assign a U.S. phone number and link it to the assistant

---

## Environment Variables

| Variable       | Required | Description                        |
|----------------|----------|------------------------------------|
| `DATABASE_URL` | No       | Defaults to `sqlite:///./carecloud.db` |
| `GROQ_API_KEY` | Yes      | Your Groq API key                  |
| `VAPI_API_KEY` | No       | Your Vapi API key (for reference)  |

---

## API Reference

All responses follow the envelope: `{ "data": {...}, "error": null }`

| Method | Endpoint             | Description                                      |
|--------|----------------------|--------------------------------------------------|
| GET    | `/health`            | Health check                                     |
| GET    | `/patients`          | List all patients. Query: `?last_name=`, `?date_of_birth=`, `?phone_number=` |
| GET    | `/patients/:id`      | Get patient by UUID                              |
| POST   | `/patients`          | Create patient (full validation)                 |
| PUT    | `/patients/:id`      | Partial update                                   |
| DELETE | `/patients/:id`      | Soft delete (sets `deleted_at`)                  |
| POST   | `/vapi/webhook`      | Vapi tool-call handler (internal use)            |

---

## Conversational Flow

```
Aria greets caller
    │
    ├── Asks for phone number
    │       └── check_existing_patient tool call
    │               ├── Found → offer to update
    │               └── Not found → begin registration
    │
    ├── Collects required fields (name, DOB, sex, address, phone)
    │
    ├── Offers optional fields (insurance, emergency contact, language)
    │
    ├── Reads back ALL collected information
    │       └── Caller confirms or corrects
    │
    └── save_patient tool call → confirms patient_id to caller
```

---

## Prompt Engineering Notes

The system prompt (`VAPI_SYSTEM_PROMPT.md`) is designed around three principles:

1. **Brevity for voice** — all responses capped at 2-3 sentences; no lists or long explanations
2. **Graceful error recovery** — every field has a specific re-prompt strategy rather than a
   generic "I didn't understand"
3. **Confirmation before persistence** — data is never saved without explicit caller confirmation,
   preventing partial or incorrect records

---

## Known Limitations & Trade-offs

- **SQLite in production**: Chosen for zero-setup convenience. For production, swap `DATABASE_URL`
  to a PostgreSQL connection string — SQLAlchemy abstracts the difference entirely.
- **No authentication on the API**: The REST API is open. In production, add API key middleware or
  OAuth2.
- **No call recording**: Vapi supports recording but was not wired up within the time constraint.
  The `end-of-call-report` webhook is in place to extend this.
- **Phone number from Vapi**: The caller's phone number is passed in call metadata. In the current
  implementation the agent asks for it conversationally as a fallback for reliability.

---

## Next Steps (Given More Time)

- [ ] PostgreSQL on Railway with proper migrations (Alembic)
- [ ] Store full call transcript linked to `patient_id`
- [ ] Simple web dashboard (React or plain HTML) showing registered patients
- [ ] Appointment scheduling flow after registration
- [ ] API key authentication middleware
- [ ] Unit tests for all API endpoints (pytest)
- [ ] Automated tests for the Vapi webhook handler

---

## Project Structure

```
carecloud-voice-agent/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app, all REST routes, seed data
│   ├── models.py         # SQLAlchemy Patient model
│   ├── schemas.py        # Pydantic validation schemas
│   ├── database.py       # DB engine, session, Base
│   └── vapi_webhook.py   # Vapi tool-call handler
├── VAPI_SYSTEM_PROMPT.md # Full LLM system prompt (documented)
├── VAPI_TOOLS.md         # Tool definitions for Vapi dashboard
├── requirements.txt
├── railway.json
├── Procfile
├── .env.example
├── .gitignore
└── README.md
```
