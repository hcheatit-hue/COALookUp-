# ⚡ LaunchPad — Setup Guide

## First-time setup (do this once)

Open PowerShell and run:

```
pip install flask flask-cors
```

---

## How to start LaunchPad

1. Open PowerShell
2. Navigate to this folder:
   ```
   cd "C:\path\to\launchpad"
   ```
3. Start the server:
   ```
   python server.py
   ```
4. Open your browser and go to:
   ```
   http://localhost:5000
   ```

---

## How to use

- Click **"Register a New App"** to add an app
- Fill in: Name, Type (Node/Python), Folder Path, and Start Command
- Click **▶ Launch** — a new PowerShell window will open and start your app automatically!
- Click **Running** on a card to mark it as stopped

---

## Files

| File | Purpose |
|------|---------|
| `server.py` | The backend — must be running |
| `index.html` | The UI — opens in your browser |
| `apps.json` | Where your apps are saved (auto-created) |
| `requirements.txt` | Python dependencies |