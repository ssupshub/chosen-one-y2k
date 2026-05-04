# chosen-one-y2k — Installation Guide

**Windows | macOS | Linux**

Flask + SQLite Backend | Vanilla HTML Frontend | v1.0 — May 2026

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Windows Installation](#2-windows-installation)
- [3. macOS Installation](#3-macos-installation)
- [4. Linux Installation](#4-linux-installation)
- [5. Verifying the Installation](#5-verifying-the-installation)
- [6. Troubleshooting](#6-troubleshooting)
- [7. Resetting the Database](#7-resetting-the-database)
- [8. Running in Production](#8-running-in-production-optional)
- [9. File Structure Reference](#9-file-structure-reference)
- [10. Quick Reference](#10-quick-reference)

---

## 1. Overview

chosen-one-y2k is a retro early-2000s multi-page hero website with a Python/Flask backend and SQLite database. The frontend is plain HTML, CSS and JavaScript with no build step. The backend exposes a REST API on port 5000.

### What you will install

- Python 3.8 or newer
- pip packages: `flask` and `flask-cors`
- A modern browser (Chrome, Firefox, Edge or Safari)
- Git (optional, for cloning the repository)

### Compatibility

| OS               | Status    | Notes                            |
| ---------------- | --------- | -------------------------------- |
| Windows 10 / 11  | Supported | Use `start.bat` or manual steps  |
| macOS 12+        | Supported | Use `start.sh` or manual steps   |
| Ubuntu 20.04+    | Supported | Use `start.sh` or manual steps   |
| Debian / Fedora  | Supported | Same as Ubuntu                   |
| WSL2 on Windows  | Supported | Follow Linux steps inside WSL    |

> The frontend works offline. You only need the backend running if you want the guestbook, chat, missions, scores or contact form to persist.

---

## 2. Windows Installation

### 2.1 Install Python

1. Open your browser and go to `python.org/downloads`
2. Click **Download Python 3.x.x** (the latest stable release).
3. Run the installer. On the first screen, tick **Add Python to PATH**, then click **Install Now**.
4. When complete, click **Close**.

> If the installer does not show the PATH checkbox, select **Customize installation** and check it on the Advanced Options screen.

**Verify the installation**

Open Command Prompt (`Win + R`, type `cmd`, press Enter) and run:

```
python --version
pip --version
```

Both commands should print version numbers. If `python` is not found, restart your computer and try again.

### 2.2 Get the project files

**Option A — Clone with Git (recommended)**

```bash
git clone https://github.com/your-username/chosen-one-y2k.git
cd chosen-one-y2k
```

**Option B — Download ZIP from GitHub**

1. Go to the repository page on GitHub.
2. Click **Code** then **Download ZIP**.
3. Right-click the downloaded ZIP and choose **Extract All**. Pick a folder and click **Extract**.
4. Open Command Prompt and navigate to the extracted folder:

```bash
cd C:\Users\YourName\Desktop\chosen-one-y2k
```

### 2.3 Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

You should see Flask and flask-cors download and install. This takes about 30 seconds on a normal connection.

### 2.4 Start the backend

**Option A — One-click launcher**

Double-click `start.bat` in the project root. A Command Prompt window opens and shows:

```
 chosen-one-y2k backend running
 API: http://localhost:5000/api
 Press Ctrl+C to stop
```

**Option B — Manual**

```bash
cd backend
python app.py
```

> Keep this window open. The backend must stay running while you use the site. Closing the window stops the server.

### 2.5 Open the frontend

1. Open File Explorer and navigate to the project folder.
2. Double-click `index.html`. It opens in your default browser.
3. The site connects to the backend automatically. The visitor counter and guestbook load from the database.

> If your browser blocks localhost connections, type the path directly into the address bar:
> `file:///C:/Users/YourName/Desktop/chosen-one-y2k/index.html`

---

## 3. macOS Installation

### 3.1 Install Python

macOS ships with Python 2 on older versions and no Python on newer ones. Install Python 3 using one of these methods.

**Option A — Official installer (easiest)**

1. Go to `python.org/downloads` and download the macOS installer.
2. Open the downloaded `.pkg` file and follow the prompts.
3. Open Terminal (`Cmd + Space`, type Terminal, press Enter) and verify:

```bash
python3 --version
pip3 --version
```

**Option B — Homebrew (recommended for developers)**

If you do not have Homebrew, install it first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:

```bash
brew install python
python3 --version
```

### 3.2 Get the project files

**Option A — Clone with Git**

```bash
git clone https://github.com/your-username/chosen-one-y2k.git
cd chosen-one-y2k
```

**Option B — Download ZIP**

1. Download the ZIP from GitHub (**Code** > **Download ZIP**).
2. Double-click to extract. Open Terminal and navigate to the folder:

```bash
cd ~/Downloads/chosen-one-y2k
```

### 3.3 Install Python dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

If pip3 complains about system packages, add the flag:

```bash
pip3 install -r requirements.txt --break-system-packages
```

### 3.4 Start the backend

**Option A — One-click launcher**

```bash
bash start.sh
```

**Option B — Manual**

```bash
cd backend
python3 app.py
```

> macOS may show a Gatekeeper dialog the first time you run a downloaded script. If so, go to **System Settings > Privacy and Security** and click **Allow Anyway**.

### 3.5 Open the frontend

1. In a new Terminal tab, navigate to the project folder.
2. Open `index.html` directly:

```bash
open index.html
```

Or drag `index.html` onto your browser icon in the Dock.

---

## 4. Linux Installation

These steps work on Ubuntu, Debian, Fedora, Arch and most other distributions. Commands that differ per distro are noted.

### 4.1 Install Python

**Ubuntu / Debian**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

**Fedora / RHEL / CentOS**

```bash
sudo dnf install python3 python3-pip -y
```

**Arch Linux**

```bash
sudo pacman -S python python-pip
```

**Verify**

```bash
python3 --version
pip3 --version
```

### 4.2 Get the project files

**Option A — Clone with Git**

```bash
git clone https://github.com/your-username/chosen-one-y2k.git
cd chosen-one-y2k
```

**Option B — Download and extract ZIP**

```bash
wget https://github.com/your-username/chosen-one-y2k/archive/refs/heads/main.zip
unzip main.zip
cd chosen-one-y2k-main
```

### 4.3 Install Python dependencies

**Option A — System-wide (simple)**

```bash
cd backend
pip3 install -r requirements.txt
```

**Option B — Virtual environment (recommended)**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Using a virtual environment keeps these packages isolated from the rest of your system. Run `source venv/bin/activate` each time you open a new terminal before starting the backend.

### 4.4 Start the backend

**Option A — One-click launcher**

```bash
chmod +x start.sh
bash start.sh
```

**Option B — Manual**

```bash
cd backend
python3 app.py
```

The terminal prints:

```
 chosen-one-y2k backend running
 API: http://localhost:5000/api
 DB:  /home/user/chosen-one-y2k/backend/chosen.db
 Press Ctrl+C to stop
```

### 4.5 Open the frontend

**From the terminal**

```bash
xdg-open index.html
```

**Or from a file manager**

Navigate to the project folder and double-click `index.html`. Choose your browser when prompted.

---

## 5. Verifying the Installation

### 5.1 Check the backend is running

Open your browser and go to:

```
http://localhost:5000/api/health
```

You should see a JSON response:

```json
{"status": "ok", "db": "/path/to/chosen.db"}
```

### 5.2 Check all API endpoints

These endpoints should each return a 200 response in the browser or with curl:

| Endpoint                  | Description                      |
| ------------------------- | -------------------------------- |
| `GET /api/health`         | Backend and database status      |
| `GET /api/visitors`       | Current visitor count            |
| `GET /api/guestbook`      | Paginated guestbook entries      |
| `GET /api/chat`           | Global alliance chat messages    |
| `GET /api/missions/{id}`  | Mission progress for a session   |
| `GET /api/scores`         | Top 20 hero leaderboard          |
| `GET /api/events`         | Recent world event log           |
| `GET /api/session/new`    | Generate a new session ID        |

### 5.3 Check the frontend

- Open `index.html`. The visitor counter should show a real number from the database.
- Open `guestbook.html`. The seeded entries (Wizard_42, DragonKid, etc.) should appear.
- Open `alliances.html`. The global chat history should load.
- Open `mission.html`, tick a mission. Reload the page. The tick should persist.

---

## 6. Troubleshooting

### `python` is not recognized (Windows)

- Re-run the Python installer and ensure **Add Python to PATH** is checked.
- Restart Command Prompt or your computer and try again.
- Alternatively, use the Microsoft Store version of Python 3 which sets PATH automatically.

### pip install fails with permissions error

Add `--user` to the command:

```bash
pip3 install -r requirements.txt --user
```

Or on Linux/macOS use a virtual environment (see section 4.3 Option B).

### Port 5000 is already in use

Another process is using port 5000. Find and stop it, or change the port in `backend/app.py`:

```python
# Near the bottom of app.py
app.run(debug=True, port=5001)   # change to any free port
```

Then update the BASE URL in `api.js`:

```javascript
const BASE = "http://localhost:5001/api";
```

### CORS error in the browser console

`flask-cors` may not be installed. Run:

```bash
pip3 install flask-cors
```

Then restart the backend.

### The frontend shows BACKEND OFFLINE

- Make sure the backend terminal window is still open and showing no errors.
- Confirm the backend is on port 5000 by visiting `http://localhost:5000/api/health`.
- Check your browser is not blocking localhost — try a different browser.
- The site still works offline. Only live data (guestbook, chat, scores) requires the backend.

### `chosen.db` permission error on Linux

The database file could not be created. Check that the `backend/` directory is writable:

```bash
chmod 755 backend/
```

### macOS: `python3` command not found after Homebrew install

Homebrew may not have added Python to your PATH. Run:

```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
python3 --version
```

---

## 7. Resetting the Database

All guestbook entries, chat messages, missions, scores and contact messages are stored in `backend/chosen.db`. To reset everything to factory defaults:

```bash
# Stop the backend first (Ctrl+C)
cd backend

rm chosen.db          # Linux/macOS
del chosen.db         # Windows

# Restart the backend — it recreates the database with seed data
python3 app.py
```

> Deleting `chosen.db` is permanent. All user submissions, chat history and score data will be lost.

---

## 8. Running in Production (Optional)

The built-in Flask development server is fine for local use. For a public deployment, use a production WSGI server.

### Gunicorn (Linux/macOS)

```bash
pip3 install gunicorn
cd backend
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Waitress (Windows)

```bash
pip install waitress
cd backend
waitress-serve --port=5000 app:app
```

> Update `api.js` to point to your server's public IP or domain instead of localhost if hosting remotely.

---

## 9. File Structure Reference

```
chosen-one-y2k/
|
|-- index.html          Home page
|-- mission.html        Mission checklist with XP tracking
|-- prophecy.html       Prophecy scrolls and oracle
|-- enemies.html        Enemy database and battle system
|-- weapons.html        Armory and loadout builder
|-- alliances.html      Ally roster and real-time chat
|-- world.html          ASCII world map with live events
|-- guestbook.html      Paginated guestbook
|-- contact.html        Contact form
|-- style.css           Shared stylesheet
|-- api.js              Frontend API client
|-- start.bat           Windows launcher
|-- start.sh            Mac/Linux launcher
|-- README.md
|
|-- backend/
    |-- app.py          Flask app, all API routes
    |-- requirements.txt
    |-- chosen.db       SQLite database (auto-created)
```

---

## 10. Quick Reference

| Task                       | Command                                                   |
| -------------------------- | --------------------------------------------------------- |
| Start backend (Windows)    | Double-click `start.bat`                                  |
| Start backend (Mac/Linux)  | `bash start.sh`                                           |
| Start backend (manual)     | `cd backend && python3 app.py`                            |
| Install dependencies       | `pip3 install -r requirements.txt`                        |
| Check backend is up        | `curl http://localhost:5000/api/health`                   |
| Reset database             | `rm backend/chosen.db` then restart                       |
| Change port                | Edit `port=5000` in `backend/app.py` and `BASE` in `api.js` |
| View leaderboard           | `GET http://localhost:5000/api/scores`                    |

---

(C) 2001 The Council of Elders. Do not steal this HTML.
