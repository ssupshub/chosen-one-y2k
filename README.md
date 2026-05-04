# chosen-one-y2k

A retro early-2000s multi-page hero website with a Python/Flask backend and SQLite database.
No frameworks on the frontend. No external services. Open a terminal and go.

---

## File Structure

```
chosen-one-y2k/
|
|-- index.html          Home page - visitor counter, world status, mission intro
|-- mission.html        Interactive mission checklist with persistent XP tracking
|-- prophecy.html       Prophecy scrolls with a working oracle
|-- enemies.html        Enemy database with battle system and live leaderboard
|-- weapons.html        Armory with equippable loadout slots
|-- alliances.html      Ally roster with real-time chat and typing indicators
|-- world.html          ASCII world map with clickable regions and live events
|-- guestbook.html      Paginated guestbook backed by the database
|-- contact.html        Contact form saved to the database
|-- style.css           Shared stylesheet for all pages
|-- api.js              Frontend API client used by all pages
|-- sounds.js           Web Audio sound engine - no audio files required
|-- hero-setup.js       Hero name setup screen and light/dark mode toggle
|-- start.bat           Windows one-click launcher
|-- start.sh            Mac/Linux one-click launcher
|-- README.md           This file
|
|-- backend/
    |-- app.py          Flask application, all API routes
    |-- requirements.txt
    |-- chosen.db       SQLite database (auto-created on first run)
```

---

## How to Run

Step 1 - Start the backend

On Windows:

    Double-click start.bat

On Mac or Linux:

    bash start.sh

Or manually:

    cd backend
    pip install -r requirements.txt
    python app.py

The backend runs at http://localhost:5000

Step 2 - Open the frontend

Open index.html in any browser. All pages connect to localhost:5000 automatically.

The site works without the backend too. Every page falls back to local behaviour
if the API is unreachable, so you can browse the HTML files offline at any time.

---

## Features

Frontend
- 9 fully linked pages with shared navigation
- Animated CRT scanline overlay and screen flicker
- Light/dark mode toggle (CRT green vs early-web beige) on every page
- Hero name setup screen on first visit, persisted in localStorage
- Hero name shown in the navbar on every page, click to rename
- SFX on/off toggle button in the navbar

Sound effects (Web Audio API, no files needed)
- Dial-up modem handshake plays on every page load
- Retro blip on every button and nav click
- Victory jingle when a mission is completed
- Crash sound when an enemy is defeated
- Equip chime when a weapon is added to your loadout
- Submit tone when the guestbook or contact form is sent
- Chat ping when an ally message arrives
- Typing indicator with sound before ally replies appear

Backend (Flask + SQLite)
- Visitor counter - real persistent count
- Guestbook - entries saved to database, paginated
- Contact form - messages saved to database
- Global alliance chat - stored and polled every 4 seconds
- Mission progress - saved per session ID in localStorage
- Score and kill tracking - synced to leaderboard
- World events - live feed updated by battles and deployments

---

## API Endpoints

    GET  /api/health                     Backend health check
    GET  /api/visitors                   Get visitor count
    POST /api/visitors/increment         Increment and return count

    GET  /api/guestbook                  List entries (page, per_page params)
    POST /api/guestbook                  Submit a new entry

    POST /api/contact                    Save a contact message
    GET  /api/contact                    List all contact messages

    GET  /api/chat                       Get messages (channel, since_id params)
    POST /api/chat                       Post a message, triggers auto ally reply

    GET  /api/missions/<session_id>      Get mission state for a session
    POST /api/missions/<session_id>/<n>  Toggle mission n complete/incomplete

    GET  /api/scores                     Top 20 leaderboard
    GET  /api/scores/<session_id>        Score for one session
    POST /api/scores/<session_id>        Create or update score

    GET  /api/events                     Recent world events (limit param)
    POST /api/events                     Post a new world event

    GET  /api/session/new                Generate a fresh session ID

---

## Stack

    Frontend   Vanilla HTML, CSS, JavaScript. No build step.
    Backend    Python 3, Flask, flask-cors
    Database   SQLite via the Python standard library (sqlite3)
    Audio      Web Audio API - all sounds generated procedurally

---

## Notes

- The SQLite database is created automatically at backend/chosen.db on first run.
- Session IDs are stored in localStorage so missions and scores persist across reloads.
- Hero name and theme preference are also stored in localStorage.
- Chat channels: global (alliance page), dm-wizard, dm-dragon, dm-hero (private messages).
- All data resets if you delete chosen.db.
- The backend seeds the guestbook and chat with starter entries on first run.
- SFX requires a browser that supports the Web Audio API (all modern browsers do).

---

(C) 2001 THE COUNCIL OF ELDERS. DO NOT STEAL THIS HTML.
