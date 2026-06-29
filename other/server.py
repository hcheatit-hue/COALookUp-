"""
LaunchPad - Backend Server
Run this first: python server.py
Then open http://localhost:3111 in your browser
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys

app = Flask(__name__, static_folder=".")
CORS(app)

DATA_FILE = "apps.json"

# ── helpers ──────────────────────────────────────────────────────────────────

def load_apps():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_apps(apps):
    with open(DATA_FILE, "w") as f:
        json.dump(apps, f, indent=2)

# ── routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "start.html")

@app.route("/api/apps", methods=["GET"])
def get_apps():
    return jsonify(load_apps())

@app.route("/api/apps", methods=["POST"])
def add_app():
    apps = load_apps()
    app_data = request.json
    app_data["id"] = str(max([int(a["id"]) for a in apps], default=0) + 1)
    app_data["running"] = False
    apps.append(app_data)
    save_apps(apps)
    return jsonify(app_data), 201

@app.route("/api/apps/<app_id>", methods=["PUT"])
def update_app(app_id):
    apps = load_apps()
    for i, a in enumerate(apps):
        if a["id"] == app_id:
            updated = {**a, **request.json, "id": app_id}
            apps[i] = updated
            save_apps(apps)
            return jsonify(updated)
    return jsonify({"error": "Not found"}), 404

@app.route("/api/apps/<app_id>", methods=["DELETE"])
def delete_app(app_id):
    apps = load_apps()
    apps = [a for a in apps if a["id"] != app_id]
    save_apps(apps)
    return jsonify({"ok": True})

@app.route("/api/launch/<app_id>", methods=["POST"])
def launch_app(app_id):
    apps = load_apps()
    app_data = next((a for a in apps if a["id"] == app_id), None)
    if not app_data:
        return jsonify({"error": "App not found"}), 404

    path = app_data["path"]
    cmd  = app_data["cmd"]

    try:
        if sys.platform == "win32":
            # Use cwd= to set the working directory — avoids all quoting/space issues
            # cmd /k keeps the window open so you can see output
            subprocess.Popen(
                ["cmd", "/k", cmd],
                cwd=path,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux / macOS — try common terminals
            full_cmd = f'cd "{path}" && {cmd}'
            terminals = [
                ["gnome-terminal", "--", "bash", "-c", f'{full_cmd}; exec bash'],
                ["xterm", "-e", f'{full_cmd}; bash'],
                ["x-terminal-emulator", "-e", f'bash -c "{full_cmd}; bash"'],
            ]
            launched = False
            for t in terminals:
                try:
                    subprocess.Popen(t)
                    launched = True
                    break
                except FileNotFoundError:
                    continue
            if not launched:
                return jsonify({"error": "No terminal emulator found"}), 500

        # Mark as running
        for a in apps:
            if a["id"] == app_id:
                a["running"] = True
        save_apps(apps)
        return jsonify({"ok": True, "message": f"Launched {app_data['name']}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stop/<app_id>", methods=["POST"])
def stop_app(app_id):
    """Mark app as stopped (actual process management is handled by the terminal window)"""
    apps = load_apps()
    for a in apps:
        if a["id"] == app_id:
            a["running"] = False
    save_apps(apps)
    return jsonify({"ok": True})

# ── startup ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Seed example apps if first run
    if not os.path.exists(DATA_FILE):
        save_apps([
            {
                "id": "1",
                "name": "Example Node API",
                "type": "node",
                "path": "C:\\Users\\user\\projects\\my-api",
                "cmd": "npm run start",
                "icon": "⚡",
                "running": False
            },
            {
                "id": "2",
                "name": "Reports Dashboard",
                "type": "python",
                "path": "C:\\Users\\motebejanec\\OneDrive - HC Heat Exchangers\\Documents\\Code\\HC\\ReportsDashboard",
                "cmd": "python app.py",
                "icon": "🐍",
                "running": False
            }
        ])

    print("\n  ⚡ LaunchPad is running!")
    print("  👉 Open http://localhost:3111 in your browser\n")
    app.run(host='0.0.0.0', port=3111, debug=False)