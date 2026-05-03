"""
chosen-one-y2k — Flask Backend
Powered by SQLite. No external services required.
Run: python app.py
API base: http://localhost:5000/api
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import time
import random
import string
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow frontend on any port to talk to this backend

DB_PATH = os.path.join(os.path.dirname(__file__), "chosen.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS guestbook (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                location  TEXT    DEFAULT 'Unknown Location',
                message   TEXT    NOT NULL,
                stars     INTEGER DEFAULT 5,
                created_at TEXT   DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS contact_messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                codename  TEXT NOT NULL,
                email     TEXT NOT NULL,
                subject   TEXT NOT NULL,
                threat    TEXT DEFAULT 'low',
                message   TEXT NOT NULL,
                encrypted INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                sender    TEXT NOT NULL,
                message   TEXT NOT NULL,
                channel   TEXT DEFAULT 'global',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS missions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                mission_idx INTEGER NOT NULL,
                completed   INTEGER DEFAULT 0,
                completed_at TEXT,
                UNIQUE(session_id, mission_idx)
            );

            CREATE TABLE IF NOT EXISTS scores (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                hero_name  TEXT NOT NULL,
                xp         INTEGER DEFAULT 0,
                kills      INTEGER DEFAULT 0,
                session_id TEXT NOT NULL UNIQUE,
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS world_events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                region     TEXT NOT NULL,
                event_text TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

        # Seed guestbook if empty
        count = conn.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0]
        if count == 0:
            seed = [
                ("Wizard_42",    "Server Room Alpha, Sector 3",  "I have been waiting for the Chosen One for SEVEN YEARS. You are finally here. Do not fail us. The password is almost cracked.", 5),
                ("DragonKid",    "Asia Region, Fighting Zone",    "CHOSEN ONE. COME TO ASIA. WE ARE LOSING THE SERVERS. BRING THE AD-BLOCK CANNON. MY DRAGON IS TIRED.", 5),
                ("xXHero99Xx",   "CLASSIFIED",                    "n1c3 w3bs1t3 ch0s3n 0n3. th3 pr0ph3cy 1s r34l. s33 u 0n th3 b4ttl3f13ld.", 4),
                ("ElderByte",    "Council Chambers, Moon Base",   "Child. You have found the page. The algorithm does not lie. Welcome to your destiny.", 5),
                ("GeoCity_Gary", "GeoCities, USA",                "wow cool site!! i made my own site too its about my cat mr whiskers. good luck with the whole saving the world thing lol", 3),
                ("DialUp_Dana",  "56k Connection, Suburb",        "this page took 45 minutes to load on my modem but it was WORTH IT. bookmarked.", 5),
            ]
            conn.executemany(
                "INSERT INTO guestbook (name, location, message, stars) VALUES (?,?,?,?)",
                seed
            )

        # Seed chat if empty
        chat_count = conn.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]
        if chat_count == 0:
            seed_chat = [
                ("Council",    "THE CHOSEN HAS ARRIVED",                          "global"),
                ("Wizard_42",  "about time lol",                                  "global"),
                ("Wizard_42",  "I've almost cracked the ZIP password! Stay ready.","global"),
                ("DragonKid",  "NEED BACKUP IN ASIA SECTOR NOW",                  "global"),
                ("xXHero99Xx", "h4v3 1nf1ltr4t3d th3 s3rv3r",                    "global"),
            ]
            conn.executemany(
                "INSERT INTO chat_messages (sender, message, channel) VALUES (?,?,?)",
                seed_chat
            )

        # Seed world events if empty
        ev_count = conn.execute("SELECT COUNT(*) FROM world_events").fetchone()[0]
        if ev_count == 0:
            seed_events = [
                ("ASIA",          "POPUP attack on ASIA-7"),
                ("EUROPE",        "EUROPE firewall holding"),
                ("ANTARCTICA",    "ANTARCTICA OFFLINE confirmed"),
                ("MOON",          "MOON BASE laser fired"),
                ("NORTH AMERICA", "N. AMERICA patrol normal"),
            ]
            conn.executemany(
                "INSERT INTO world_events (region, event_text) VALUES (?,?)",
                seed_events
            )

        conn.commit()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def make_session_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=16))


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_list(rows):
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# GUESTBOOK  /api/guestbook
# ---------------------------------------------------------------------------

@app.route("/api/guestbook", methods=["GET"])
def guestbook_list():
    page     = max(1, int(request.args.get("page", 1)))
    per_page = int(request.args.get("per_page", 4))
    offset   = (page - 1) * per_page

    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0]
        rows  = conn.execute(
            "SELECT * FROM guestbook ORDER BY id DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        ).fetchall()

    return jsonify({
        "entries": rows_to_list(rows),
        "total":   total,
        "page":    page,
        "pages":   max(1, -(-total // per_page))   # ceiling div
    })


@app.route("/api/guestbook", methods=["POST"])
def guestbook_post():
    data = request.get_json(force=True)
    name     = (data.get("name") or "").strip()
    location = (data.get("location") or "Unknown Location").strip()
    message  = (data.get("message") or "").strip()
    stars    = int(data.get("stars") or 5)

    if not name or not message:
        return jsonify({"error": "name and message are required"}), 400
    if stars < 1 or stars > 5:
        stars = 5

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO guestbook (name, location, message, stars) VALUES (?,?,?,?)",
            (name, location, message, stars)
        )
        new_id = cur.lastrowid
        conn.commit()
        row = conn.execute("SELECT * FROM guestbook WHERE id=?", (new_id,)).fetchone()

    return jsonify({"entry": row_to_dict(row), "xp_awarded": 50}), 201


# ---------------------------------------------------------------------------
# CONTACT  /api/contact
# ---------------------------------------------------------------------------

@app.route("/api/contact", methods=["POST"])
def contact_send():
    data      = request.get_json(force=True)
    codename  = (data.get("codename") or "").strip()
    email     = (data.get("email") or "").strip()
    subject   = (data.get("subject") or "").strip()
    threat    = (data.get("threat") or "low").strip()
    message   = (data.get("message") or "").strip()
    encrypted = 1 if data.get("encrypted") else 0

    if not codename or not email or not subject or not message:
        return jsonify({"error": "codename, email, subject and message are required"}), 400

    with get_db() as conn:
        conn.execute(
            "INSERT INTO contact_messages (codename,email,subject,threat,message,encrypted) VALUES (?,?,?,?,?,?)",
            (codename, email, subject, threat, message, encrypted)
        )
        conn.commit()

    return jsonify({"status": "sent", "message": "Transmission received by the Council."}), 201


@app.route("/api/contact", methods=["GET"])
def contact_list():
    """Simple admin view of all messages."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM contact_messages ORDER BY id DESC"
        ).fetchall()
    return jsonify({"messages": rows_to_list(rows)})


# ---------------------------------------------------------------------------
# CHAT  /api/chat
# ---------------------------------------------------------------------------

@app.route("/api/chat", methods=["GET"])
def chat_get():
    channel = request.args.get("channel", "global")
    since   = int(request.args.get("since_id", 0))

    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE channel=? AND id>? ORDER BY id ASC LIMIT 50",
            (channel, since)
        ).fetchall()

    return jsonify({"messages": rows_to_list(rows)})


@app.route("/api/chat", methods=["POST"])
def chat_post():
    data    = request.get_json(force=True)
    sender  = (data.get("sender") or "HERO").strip()
    message = (data.get("message") or "").strip()
    channel = (data.get("channel") or "global").strip()

    if not message:
        return jsonify({"error": "message required"}), 400

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO chat_messages (sender, message, channel) VALUES (?,?,?)",
            (sender, message, channel)
        )
        new_id = cur.lastrowid

        # Auto-reply from a random ally after a short random delay
        allies = [
            ("Wizard_42",  ["Close to cracking that ZIP password! Stay ready.",
                             "The HTML scrolls speak of you, Chosen One.",
                             "Level 99 has perks. I can see everything."]),
            ("DragonKid",  ["BACKUP NEEDED! Asia sector falling fast!!",
                             "My dragon Compaq is injured but fighting.",
                             "The Chosen One speaks! Dragon roars in your honor."]),
            ("xXHero99Xx", ["shhh. in 5t34lth m0d3.",
                             "h4x0r mode activ4ted.",
                             "c4n't t4lk. t00 busy b31ng aw3s0me"]),
        ]
        ally_name, ally_lines = random.choice(allies)
        reply = random.choice(ally_lines)
        conn.execute(
            "INSERT INTO chat_messages (sender, message, channel) VALUES (?,?,?)",
            (ally_name, reply, channel)
        )
        conn.commit()

        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE channel=? AND id>=? ORDER BY id ASC",
            (channel, new_id)
        ).fetchall()

    return jsonify({"messages": rows_to_list(rows)}), 201


# ---------------------------------------------------------------------------
# MISSIONS  /api/missions
# ---------------------------------------------------------------------------

MISSION_LIST = [
    {"idx": 0, "title": "DEFEAT MALKOR.EXE AND HIS ARMY OF POPUP ADS",            "xp": 150},
    {"idx": 1, "title": "RETRIEVE THE SACRED .ZIP FILE OF DESTINY",               "xp": 200},
    {"idx": 2, "title": "DEFRAG THE CORRUPTED CRYSTALS OF KNOWLEDGE",             "xp": 175},
    {"idx": 3, "title": "UNITE THE 7 INTERNET KINGDOMS UNDER ONE DIAL-UP",        "xp": 300},
    {"idx": 4, "title": "RESTORE THE ANCIENT HOMEPAGE OF LIGHT",                  "xp": 250},
    {"idx": 5, "title": "DEFEAT THE COUNCIL OF SHADOW WEBMASTERS",                "xp": 100},
    {"idx": 6, "title": "SIGN THE GUESTBOOK (VERY IMPORTANT)",                    "xp":  50},
]


@app.route("/api/missions/<session_id>", methods=["GET"])
def missions_get(session_id):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT mission_idx, completed, completed_at FROM missions WHERE session_id=?",
            (session_id,)
        ).fetchall()

    completed_map = {r["mission_idx"]: r for r in rows}
    result = []
    for m in MISSION_LIST:
        entry = dict(m)
        row   = completed_map.get(m["idx"])
        entry["completed"]    = bool(row and row["completed"])
        entry["completed_at"] = row["completed_at"] if row else None
        result.append(entry)

    total_xp = sum(m["xp"] for m in MISSION_LIST
                   if completed_map.get(m["idx"]) and completed_map[m["idx"]]["completed"])

    return jsonify({"missions": result, "total_xp": total_xp, "session_id": session_id})


@app.route("/api/missions/<session_id>/<int:mission_idx>", methods=["POST"])
def mission_toggle(session_id, mission_idx):
    if mission_idx < 0 or mission_idx >= len(MISSION_LIST):
        return jsonify({"error": "invalid mission index"}), 400

    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM missions WHERE session_id=? AND mission_idx=?",
            (session_id, mission_idx)
        ).fetchone()

        if existing:
            new_val = 0 if existing["completed"] else 1
            conn.execute(
                "UPDATE missions SET completed=?, completed_at=? WHERE session_id=? AND mission_idx=?",
                (new_val, datetime.utcnow().isoformat() if new_val else None, session_id, mission_idx)
            )
        else:
            conn.execute(
                "INSERT INTO missions (session_id, mission_idx, completed, completed_at) VALUES (?,?,1,?)",
                (session_id, mission_idx, datetime.utcnow().isoformat())
            )
            new_val = 1

        conn.commit()

    xp = MISSION_LIST[mission_idx]["xp"] if new_val else 0
    return jsonify({
        "mission_idx": mission_idx,
        "completed":   bool(new_val),
        "xp_change":   xp if new_val else -MISSION_LIST[mission_idx]["xp"]
    })


@app.route("/api/session/new", methods=["GET"])
def new_session():
    return jsonify({"session_id": make_session_id()})


# ---------------------------------------------------------------------------
# SCORES / LEADERBOARD  /api/scores
# ---------------------------------------------------------------------------

@app.route("/api/scores", methods=["GET"])
def scores_list():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT hero_name, xp, kills, updated_at FROM scores ORDER BY xp DESC LIMIT 20"
        ).fetchall()
    return jsonify({"leaderboard": rows_to_list(rows)})


@app.route("/api/scores/<session_id>", methods=["GET"])
def score_get(session_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM scores WHERE session_id=?", (session_id,)
        ).fetchone()
    if not row:
        return jsonify({"error": "session not found"}), 404
    return jsonify(row_to_dict(row))


@app.route("/api/scores/<session_id>", methods=["POST"])
def score_update(session_id):
    data      = request.get_json(force=True)
    hero_name = (data.get("hero_name") or "HERO").strip()
    xp        = int(data.get("xp") or 0)
    kills     = int(data.get("kills") or 0)

    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM scores WHERE session_id=?", (session_id,)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE scores SET hero_name=?, xp=?, kills=?, updated_at=? WHERE session_id=?",
                (hero_name, xp, kills, datetime.utcnow().isoformat(), session_id)
            )
        else:
            conn.execute(
                "INSERT INTO scores (hero_name, xp, kills, session_id) VALUES (?,?,?,?)",
                (hero_name, xp, kills, session_id)
            )

        conn.commit()
        row = conn.execute("SELECT * FROM scores WHERE session_id=?", (session_id,)).fetchone()

    return jsonify(row_to_dict(row)), 201


# ---------------------------------------------------------------------------
# WORLD EVENTS  /api/events
# ---------------------------------------------------------------------------

@app.route("/api/events", methods=["GET"])
def events_list():
    limit = int(request.args.get("limit", 10))
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM world_events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return jsonify({"events": rows_to_list(rows)})


@app.route("/api/events", methods=["POST"])
def events_post():
    data   = request.get_json(force=True)
    region = (data.get("region") or "UNKNOWN").strip().upper()
    text   = (data.get("event_text") or "").strip()

    if not text:
        return jsonify({"error": "event_text required"}), 400

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO world_events (region, event_text) VALUES (?,?)", (region, text)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM world_events WHERE id=?", (cur.lastrowid,)).fetchone()

    return jsonify(row_to_dict(row)), 201


# ---------------------------------------------------------------------------
# VISITOR COUNTER  /api/visitors
# ---------------------------------------------------------------------------

@app.route("/api/visitors", methods=["GET"])
def visitors_get():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                id    INTEGER PRIMARY KEY CHECK (id=1),
                count INTEGER DEFAULT 41337
            )
        """)
        row = conn.execute("SELECT count FROM visitors WHERE id=1").fetchone()
        if not row:
            conn.execute("INSERT INTO visitors (id, count) VALUES (1, 41337)")
            conn.commit()
            count = 41337
        else:
            count = row["count"]
    return jsonify({"count": count})


@app.route("/api/visitors/increment", methods=["POST"])
def visitors_increment():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                id    INTEGER PRIMARY KEY CHECK (id=1),
                count INTEGER DEFAULT 41337
            )
        """)
        conn.execute("INSERT INTO visitors (id, count) VALUES (1, 41337) ON CONFLICT(id) DO UPDATE SET count=count+1")
        conn.commit()
        count = conn.execute("SELECT count FROM visitors WHERE id=1").fetchone()["count"]
    return jsonify({"count": count})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "db": DB_PATH})


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("\n  chosen-one-y2k backend running")
    print("  API: http://localhost:5000/api")
    print("  DB:  " + DB_PATH)
    print("  Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)
