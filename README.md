# 🧠 Friday - Your Personal AI Assistant

This is a Python-based AI assistant inspired by *Jarvis*, capable of:

- 🔍 Searching the web
- 🌤️ Weather checking
- 📨 Sending Emails
- 🗣️ Speech
- 📝 Chat-style interaction

This project uses LiveKit and Google Gemini services for the full voice experience.

---

## 🚀 Quick start

### 1) Create and activate the virtual environment

PowerShell:

```powershell
cd C:\projetos\jarvis
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3) Configure environment variables

Edit [.env](.env) and replace the placeholder values with real ones.

Required for the full runtime:
- LIVEKIT_URL
- LIVEKIT_API_KEY
- LIVEKIT_API_SECRET
- GOOGLE_API_KEY

Optional for email support:
- GMAIL_USER
- GMAIL_APP_PASSWORD

### 4) Run locally without real credentials

If you want to test the project immediately before configuring API keys, run:

```powershell
python agent.py local
```

This starts a simple local fallback chat loop.

### 5) Run the full agent

Once the credentials are configured:

```powershell
python agent.py dev
```

For the console-based microphone mode:

```powershell
python agent.py console
```

---

## 📽️ Tutorial Video

Before you start with the full voice experience, make sure to follow the setup tutorial:
🎥 [Watch here](https://youtu.be/An4NwL8QSQ4?si=v1dNDDonmpCG1Els)

