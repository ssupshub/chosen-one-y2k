# chosen-one-y2k

A retro early-2000s multi-page hero website with a Python/Flask backend and SQLite database.
Deployable to Vercel with both frontend and backend running together.

---

## Project Structure

```
chosen-one-y2k/
|
|-- frontend/
|   |-- pages/
|   |   |-- index.html          Home page
|   |   |-- mission.html        Mission checklist with XP tracking
|   |   |-- prophecy.html       Prophecy scrolls and oracle
|   |   |-- enemies.html        Enemy database with battle system
|   |   |-- weapons.html        Armory with loadout builder
|   |   |-- alliances.html      Ally roster with real-time chat
|   |   |-- world.html          ASCII world map with live events
|   |   |-- guestbook.html      Paginated guestbook
|   |   `-- contact.html        Contact form
|   |
|   `-- assets/
|       |-- css/
|       |   `-- style.css       Shared stylesheet
|       `-- js/
|           |-- api.js          API client - auto-detects localhost vs Vercel
|           |-- sounds.js       Web Audio sound engine
|           `-- hero-setup.js   Hero name setup and light/dark mode toggle
|
|-- api/
|   `-- index.py                Vercel serverless Flask function (all API routes)
|
|-- backend/
|   |-- app.py                  Local dev Flask server
|   `-- requirements.txt        Local dev Python dependencies
|
|-- vercel.json                 Vercel routing and build config
|-- requirements.txt            Vercel Python dependencies (root level)
|-- start.bat                   Windows local dev launcher
|-- start.sh                    Mac/Linux local dev launcher
|-- .gitignore
`-- README.md
```

---

## Deploy to Vercel

### Step 1 - Push to GitHub

Make sure your repo is pushed to GitHub.

### Step 2 - Import on Vercel

1. Go to vercel.com and sign in
2. Click New Project
3. Import your chosen-one-y2k GitHub repository
4. Leave all settings as default - vercel.json handles everything
5. Click Deploy

Vercel will:
- Serve frontend/pages/ as static files at clean URLs (/, /mission, /guestbook etc.)
- Run api/index.py as a Python serverless function at /api/*
- Install flask and flask-cors from requirements.txt automatically

### Step 3 - Done

Your site is live. The frontend auto-detects Vercel and calls /api/* instead of localhost:5000.

---

## Run Locally

### Start the backend

On Windows:

    double-click start.bat

On Mac or Linux:

    bash start.sh

Or manually:

    cd backend
    pip install -r requirements.txt
    python app.py

Backend runs at http://localhost:5000

### Open the frontend

Open frontend/pages/index.html in your browser.
api.js detects localhost and routes calls to http://localhost:5000/api automatically.

---

## How the API URL works

api.js contains this logic:

    const isLocal = hostname is localhost or 127.0.0.1 or file://
    const BASE = isLocal ? "http://localhost:5000/api" : "/api"

On Vercel, BASE becomes /api which hits the serverless function.
On localhost, BASE becomes http://localhost:5000/api which hits the local Flask server.
No environment variables or config changes needed.

---

## API Endpoints

    GET  /api/health                     Health check
    GET  /api/visitors                   Visitor count
    POST /api/visitors/increment         Increment visitor count

    GET  /api/guestbook                  List entries (page, per_page)
    POST /api/guestbook                  Submit entry

    POST /api/contact                    Save contact message
    GET  /api/contact                    List contact messages

    GET  /api/chat                       Get messages (channel, since_id)
    POST /api/chat                       Post message, triggers ally reply

    GET  /api/missions/<session_id>      Get mission state
    POST /api/missions/<session_id>/<n>  Toggle mission complete

    GET  /api/scores                     Top 20 leaderboard
    POST /api/scores/<session_id>        Update score

    GET  /api/events                     Recent world events
    POST /api/events                     Post world event

    GET  /api/session/new                Generate session ID

---

## Stack

    Frontend    Vanilla HTML, CSS, JavaScript. No build step.
    Backend     Python 3, Flask, flask-cors
    Database    SQLite - /tmp/chosen.db on Vercel, backend/chosen.db locally
    Audio       Web Audio API - procedurally generated, no audio files
    Hosting     Vercel (frontend static + Python serverless)

---

## Note on Vercel SQLite

Vercel serverless functions write to /tmp which is ephemeral - it resets between
cold starts. This means data (guestbook, chat, scores) does not persist permanently
on Vercel. For a demo or portfolio project this is fine.

For persistent data on Vercel, replace SQLite with a hosted database:
- Supabase (Postgres, free tier)
- PlanetScale (MySQL, free tier)
- Vercel KV (Redis, free tier)

---

(C) 2001 THE COUNCIL OF ELDERS. DO NOT STEAL THIS HTML.
