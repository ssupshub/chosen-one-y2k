"""
api/index.py — Vercel Serverless Backend for chosen-one-y2k

Vercel runs this as a Python serverless function.
Flask app is exposed via the standard WSGI handler Vercel expects.

Database: SQLite stored in /tmp/chosen.db (Vercel ephemeral filesystem)
Note: /tmp is reset between cold starts on Vercel. For persistent data
in production, swap SQLite for a hosted DB like Supabase or PlanetScale.
For demo/portfolio use, /tmp is perfectly fine.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import random
import string
from datetime import datetime

app = Flask(__name__)
CORS(app, origins="*")

# Vercel gives us /tmp for writable storage
DB_PATH = "/tmp/chosen.db"


# ── Database ──────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS guestbook (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                location   TEXT    DEFAULT 'Unknown Location',
                message    TEXT    NOT NULL,
                stars      INTEGER DEFAULT 5,
                created_at TEXT    DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS contact_messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                codename   TEXT NOT NULL,
                email      TEXT NOT NULL,
                subject    TEXT NOT NULL,
                threat     TEXT DEFAULT 'low',
                message    TEXT NOT NULL,
                encrypted  INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS chat_messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                sender     TEXT NOT NULL,
                message    TEXT NOT NULL,
                channel    TEXT DEFAULT 'global',
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS missions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                mission_idx  INTEGER NOT NULL,
                completed    INTEGER DEFAULT 0,
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
            CREATE TABLE IF NOT EXISTS visitors (
                id    INTEGER PRIMARY KEY CHECK (id=1),
                count INTEGER DEFAULT 41337
            );

            CREATE TABLE IF NOT EXISTS inventory (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                item_id     TEXT NOT NULL,
                item_name   TEXT NOT NULL,
                item_type   TEXT NOT NULL,
                rarity      TEXT DEFAULT 'common',
                description TEXT,
                atk_bonus   INTEGER DEFAULT 0,
                def_bonus   INTEGER DEFAULT 0,
                hp_bonus    INTEGER DEFAULT 0,
                equipped    INTEGER DEFAULT 0,
                dropped_by  TEXT,
                acquired_at TEXT DEFAULT (datetime('now')),
                UNIQUE(session_id, item_id)
            );

            CREATE TABLE IF NOT EXISTS mission_tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                mission_idx INTEGER NOT NULL,
                task_idx    INTEGER NOT NULL,
                completed   INTEGER DEFAULT 0,
                completed_at TEXT,
                UNIQUE(session_id, mission_idx, task_idx)
            );
        """)

        # Seed guestbook if empty
        count = conn.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO guestbook (name, location, message, stars) VALUES (?,?,?,?)",
                [
                    ("Wizard_42",    "Server Room Alpha, Sector 3",
                     "I have been waiting for the Chosen One for SEVEN YEARS. You are finally here. Do not fail us. The password is almost cracked.", 5),
                    ("DragonKid",    "Asia Region, Fighting Zone",
                     "CHOSEN ONE. COME TO ASIA. WE ARE LOSING THE SERVERS. BRING THE AD-BLOCK CANNON. MY DRAGON IS TIRED.", 5),
                    ("xXHero99Xx",   "CLASSIFIED",
                     "n1c3 w3bs1t3 ch0s3n 0n3. th3 pr0ph3cy 1s r34l. s33 u 0n th3 b4ttl3f13ld.", 4),
                    ("ElderByte",    "Council Chambers, Moon Base",
                     "Child. You have found the page. The algorithm does not lie. Welcome to your destiny.", 5),
                    ("GeoCity_Gary", "GeoCities, USA",
                     "wow cool site!! good luck with the whole saving the world thing lol", 3),
                    ("DialUp_Dana",  "56k Connection, Suburb",
                     "this page took 45 minutes to load on my modem but it was WORTH IT. bookmarked.", 5),
                ]
            )

        # Seed chat if empty
        chat_count = conn.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]
        if chat_count == 0:
            conn.executemany(
                "INSERT INTO chat_messages (sender, message, channel) VALUES (?,?,?)",
                [
                    ("Council",   "THE CHOSEN HAS ARRIVED",                            "global"),
                    ("Wizard_42", "about time lol",                                    "global"),
                    ("Wizard_42", "I've almost cracked the ZIP password! Stay ready.", "global"),
                    ("DragonKid", "NEED BACKUP IN ASIA SECTOR NOW",                    "global"),
                ]
            )

        # Seed world events if empty
        ev_count = conn.execute("SELECT COUNT(*) FROM world_events").fetchone()[0]
        if ev_count == 0:
            conn.executemany(
                "INSERT INTO world_events (region, event_text) VALUES (?,?)",
                [
                    ("ASIA",          "POPUP attack on ASIA-7"),
                    ("EUROPE",        "EUROPE firewall holding"),
                    ("ANTARCTICA",    "ANTARCTICA OFFLINE confirmed"),
                    ("MOON",          "MOON BASE laser fired"),
                    ("NORTH AMERICA", "N. AMERICA patrol normal"),
                ]
            )

        # Seed visitor count
        row = conn.execute("SELECT id FROM visitors WHERE id=1").fetchone()
        if not row:
            conn.execute("INSERT INTO visitors (id, count) VALUES (1, 41337)")

        conn.commit()


# Run init on every cold start
init_db()


# ── Helpers ───────────────────────────────────────────────────────────────

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

def make_session_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=16))


# ── Mission list ──────────────────────────────────────────────────────────

MISSION_LIST = [
    {"idx": 0, "title": "DEFEAT MALKOR.EXE AND HIS ARMY OF POPUP ADS",       "xp": 150},
    {"idx": 1, "title": "RETRIEVE THE SACRED .ZIP FILE OF DESTINY",           "xp": 200},
    {"idx": 2, "title": "DEFRAG THE CORRUPTED CRYSTALS OF KNOWLEDGE",         "xp": 175},
    {"idx": 3, "title": "UNITE THE 7 INTERNET KINGDOMS UNDER ONE DIAL-UP",    "xp": 300},
    {"idx": 4, "title": "RESTORE THE ANCIENT HOMEPAGE OF LIGHT",              "xp": 250},
    {"idx": 5, "title": "DEFEAT THE COUNCIL OF SHADOW WEBMASTERS",            "xp": 100},
    {"idx": 6, "title": "SIGN THE GUESTBOOK (VERY IMPORTANT)",                "xp":  50},
]


# ── Routes ────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "db": DB_PATH, "env": "vercel"})


# Visitors
@app.route("/api/visitors", methods=["GET"])
def visitors_get():
    with get_db() as conn:
        row = conn.execute("SELECT count FROM visitors WHERE id=1").fetchone()
    return jsonify({"count": row["count"] if row else 41337})

@app.route("/api/visitors/increment", methods=["POST"])
def visitors_increment():
    with get_db() as conn:
        conn.execute(
            "INSERT INTO visitors (id,count) VALUES (1,41338) "
            "ON CONFLICT(id) DO UPDATE SET count=count+1"
        )
        conn.commit()
        count = conn.execute("SELECT count FROM visitors WHERE id=1").fetchone()["count"]
    return jsonify({"count": count})


# Guestbook
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
        "pages":   max(1, -(-total // per_page))
    })

@app.route("/api/guestbook", methods=["POST"])
def guestbook_post():
    data    = request.get_json(force=True)
    name    = (data.get("name") or "").strip()
    loc     = (data.get("location") or "Unknown Location").strip()
    message = (data.get("message") or "").strip()
    stars   = min(5, max(1, int(data.get("stars") or 5)))
    if not name or not message:
        return jsonify({"error": "name and message required"}), 400
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO guestbook (name,location,message,stars) VALUES (?,?,?,?)",
            (name, loc, message, stars)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM guestbook WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify({"entry": row_to_dict(row), "xp_awarded": 50}), 201


# Contact
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
        return jsonify({"error": "all fields required"}), 400
    with get_db() as conn:
        conn.execute(
            "INSERT INTO contact_messages (codename,email,subject,threat,message,encrypted) VALUES (?,?,?,?,?,?)",
            (codename, email, subject, threat, message, encrypted)
        )
        conn.commit()
    return jsonify({"status": "sent"}), 201

@app.route("/api/contact", methods=["GET"])
def contact_list():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM contact_messages ORDER BY id DESC").fetchall()
    return jsonify({"messages": rows_to_list(rows)})


# Chat
@app.route("/api/chat", methods=["GET"])
def chat_get():
    channel  = request.args.get("channel", "global")
    since_id = int(request.args.get("since_id", 0))
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE channel=? AND id>? ORDER BY id ASC LIMIT 50",
            (channel, since_id)
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

    allies = [
        ("Wizard_42",  ["Close to cracking that ZIP password!", "The HTML scrolls speak of you.", "MALKOR is weakening."]),
        ("DragonKid",  ["BACKUP NEEDED! Asia falling!!", "My dragon Compaq is fighting on.", "The Chosen speaks! Dragon roars!"]),
        ("xXHero99Xx", ["shhh. 5t34lth m0d3.", "h4x0r mode activ4ted.", "t00 busy b31ng aw3s0me"]),
    ]
    ally_name, ally_lines = random.choice(allies)
    reply = random.choice(ally_lines)

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO chat_messages (sender,message,channel) VALUES (?,?,?)",
            (sender, message, channel)
        )
        conn.execute(
            "INSERT INTO chat_messages (sender,message,channel) VALUES (?,?,?)",
            (ally_name, reply, channel)
        )
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE channel=? AND id>=? ORDER BY id ASC",
            (channel, cur.lastrowid)
        ).fetchall()
    return jsonify({"messages": rows_to_list(rows)}), 201


# Missions
@app.route("/api/missions/<session_id>", methods=["GET"])
def missions_get(session_id):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT mission_idx,completed,completed_at FROM missions WHERE session_id=?",
            (session_id,)
        ).fetchall()
    completed_map = {r["mission_idx"]: r for r in rows}
    result = []
    total_xp = 0
    for m in MISSION_LIST:
        entry = dict(m)
        row   = completed_map.get(m["idx"])
        entry["completed"]    = bool(row and row["completed"])
        entry["completed_at"] = row["completed_at"] if row else None
        if entry["completed"]:
            total_xp += m["xp"]
        result.append(entry)
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
                "UPDATE missions SET completed=?,completed_at=? WHERE session_id=? AND mission_idx=?",
                (new_val, datetime.utcnow().isoformat() if new_val else None, session_id, mission_idx)
            )
        else:
            new_val = 1
            conn.execute(
                "INSERT INTO missions (session_id,mission_idx,completed,completed_at) VALUES (?,?,1,?)",
                (session_id, mission_idx, datetime.utcnow().isoformat())
            )
        conn.commit()
    xp = MISSION_LIST[mission_idx]["xp"]
    return jsonify({
        "mission_idx": mission_idx,
        "completed":   bool(new_val),
        "xp_change":   xp if new_val else -xp
    })

@app.route("/api/session/new", methods=["GET"])
def new_session():
    return jsonify({"session_id": make_session_id()})


# Scores
@app.route("/api/scores", methods=["GET"])
def scores_list():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT hero_name,xp,kills,updated_at FROM scores ORDER BY xp DESC LIMIT 20"
        ).fetchall()
    return jsonify({"leaderboard": rows_to_list(rows)})

@app.route("/api/scores/<session_id>", methods=["GET"])
def score_get(session_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM scores WHERE session_id=?", (session_id,)).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row_to_dict(row))

@app.route("/api/scores/<session_id>", methods=["POST"])
def score_update(session_id):
    data      = request.get_json(force=True)
    hero_name = (data.get("hero_name") or "HERO").strip()
    xp        = int(data.get("xp") or 0)
    kills     = int(data.get("kills") or 0)
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM scores WHERE session_id=?", (session_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE scores SET hero_name=?,xp=?,kills=?,updated_at=? WHERE session_id=?",
                (hero_name, xp, kills, datetime.utcnow().isoformat(), session_id)
            )
        else:
            conn.execute(
                "INSERT INTO scores (hero_name,xp,kills,session_id) VALUES (?,?,?,?)",
                (hero_name, xp, kills, session_id)
            )
        conn.commit()
        row = conn.execute("SELECT * FROM scores WHERE session_id=?", (session_id,)).fetchone()
    return jsonify(row_to_dict(row)), 201


# World events
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
            "INSERT INTO world_events (region,event_text) VALUES (?,?)", (region, text)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM world_events WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(row_to_dict(row)), 201




# ── Inventory ──────────────────────────────────────────────────────────────

ITEM_CATALOG = {
    "popup_badge":       {"name":"Popup Immunity Badge",    "type":"accessory","rarity":"common",  "description":"Grants resistance to popup attacks.","atk_bonus":0, "def_bonus":5,  "hp_bonus":0},
    "cookie_jar":        {"name":"Cracked Cookie Jar",      "type":"accessory","rarity":"common",  "description":"A jar of stolen cookies.","atk_bonus":0,"def_bonus":0,"hp_bonus":10},
    "dialup_crystal":    {"name":"56k Dial-up Crystal",     "type":"relic",    "rarity":"uncommon","description":"Hums with the sound of a modem.","atk_bonus":5,"def_bonus":0,"hp_bonus":0},
    "chain_amulet":      {"name":"Chain Mail Amulet",       "type":"accessory","rarity":"common",  "description":"Cursed amulet from a chain letter.","atk_bonus":3,"def_bonus":3,"hp_bonus":0},
    "ad_block_fragment": {"name":"Ad-Block Cannon Fragment","type":"weapon",   "rarity":"uncommon","description":"A shard from a destroyed Ad-Block Cannon.","atk_bonus":12,"def_bonus":0,"hp_bonus":0},
    "session_token":     {"name":"Stolen Session Token",    "type":"relic",    "rarity":"uncommon","description":"Stolen from COOKIE_THIEF.","atk_bonus":8,"def_bonus":0,"hp_bonus":5},
    "bandwidth_blade":   {"name":"Broadband Blade Shard",   "type":"weapon",   "rarity":"rare",    "description":"Fragment of the legendary Broadband Blade.","atk_bonus":20,"def_bonus":0,"hp_bonus":0},
    "virus_core":        {"name":"MALKOR Virus Core",       "type":"relic",    "rarity":"legendary","description":"The corrupted heart of MALKOR.EXE.","atk_bonus":25,"def_bonus":10,"hp_bonus":20},
    "firewall_gauntlet": {"name":"Firewall Gauntlet",       "type":"armor",    "rarity":"rare",    "description":"Dropped by elite popup generals.","atk_bonus":0,"def_bonus":20,"hp_bonus":0},
    "modem_whip":        {"name":"Modem Whip",              "type":"weapon",   "rarity":"uncommon","description":"Made from a tangled phone cord.","atk_bonus":15,"def_bonus":0,"hp_bonus":0},
    "zip_fragment":      {"name":"ZIP File Fragment",       "type":"relic",    "rarity":"legendary","description":"A piece of the Sacred ZIP File.","atk_bonus":0,"def_bonus":0,"hp_bonus":30},
    "popup_shield":      {"name":"Popup Shield",            "type":"armor",    "rarity":"common",  "description":"A shield made from deflected popup windows.","atk_bonus":0,"def_bonus":10,"hp_bonus":0},
}

ENEMY_DROPS = {
    "MALKOR":          [("virus_core",0.8),("zip_fragment",0.6),("bandwidth_blade",0.9),("firewall_gauntlet",0.5)],
    "POPUP_GENERAL":   [("ad_block_fragment",0.9),("popup_shield",0.8),("popup_badge",1.0),("firewall_gauntlet",0.3)],
    "COOKIE_THIEF":    [("cookie_jar",1.0),("session_token",0.85),("chain_amulet",0.4)],
    "DIALUP_DRAIN":    [("dialup_crystal",0.9),("modem_whip",0.75),("popup_badge",0.5)],
    "CHAINMAIL_WORM":  [("chain_amulet",1.0),("popup_badge",0.6),("cookie_jar",0.4)],
}

@app.route("/api/inventory/<session_id>", methods=["GET"])
def inventory_get(session_id):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM inventory WHERE session_id=? ORDER BY acquired_at DESC",(session_id,)).fetchall()
    return jsonify({"items": rows_to_list(rows)})

@app.route("/api/inventory/<session_id>/drop/<enemy_key>", methods=["POST"])
def inventory_drop_enemy(session_id, enemy_key):
    data = request.get_json(force=True) or {}
    enemy_key = (data.get("enemy_key") or enemy_key).upper()
    drops = ENEMY_DROPS.get(enemy_key, [])
    added = []
    with get_db() as conn:
        for drop_id, chance in drops:
            if random.random() <= chance:
                catalog = ITEM_CATALOG.get(drop_id)
                if not catalog: continue
                uid = drop_id + "_" + str(int(random.random()*9999))
                try:
                    conn.execute("""INSERT OR IGNORE INTO inventory
                        (session_id,item_id,item_name,item_type,rarity,description,
                         atk_bonus,def_bonus,hp_bonus,equipped,dropped_by)
                        VALUES (?,?,?,?,?,?,?,?,?,0,?)""",
                        (session_id,uid,catalog["name"],catalog["type"],catalog["rarity"],
                         catalog["description"],catalog["atk_bonus"],catalog["def_bonus"],
                         catalog["hp_bonus"],enemy_key))
                    added.append({"item_id":uid,"item_name":catalog["name"],"rarity":catalog["rarity"]})
                except: pass
        conn.commit()
    return jsonify({"drops": added, "count": len(added)}), 201

@app.route("/api/inventory/<session_id>/equip/<item_id>", methods=["POST"])
def inventory_equip(session_id, item_id):
    data  = request.get_json(force=True) or {}
    equip = 1 if data.get("equip", True) else 0
    with get_db() as conn:
        if equip:
            item = conn.execute("SELECT item_type FROM inventory WHERE session_id=? AND item_id=?",(session_id,item_id)).fetchone()
            if item:
                conn.execute("UPDATE inventory SET equipped=0 WHERE session_id=? AND item_type=?",(session_id,item["item_type"]))
        conn.execute("UPDATE inventory SET equipped=? WHERE session_id=? AND item_id=?",(equip,session_id,item_id))
        conn.commit()
        row = conn.execute("SELECT * FROM inventory WHERE session_id=? AND item_id=?",(session_id,item_id)).fetchone()
    return jsonify(row_to_dict(row))

@app.route("/api/inventory/<session_id>/remove/<item_id>", methods=["DELETE"])
def inventory_remove(session_id, item_id):
    with get_db() as conn:
        conn.execute("DELETE FROM inventory WHERE session_id=? AND item_id=?",(session_id,item_id))
        conn.commit()
    return jsonify({"deleted": item_id})

@app.route("/api/inventory/<session_id>/stats", methods=["GET"])
def inventory_stats(session_id):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM inventory WHERE session_id=? AND equipped=1",(session_id,)).fetchall()
    items = rows_to_list(rows)
    return jsonify({"atk_bonus":sum(i["atk_bonus"] for i in items),
                    "def_bonus":sum(i["def_bonus"] for i in items),
                    "hp_bonus": sum(i["hp_bonus"]  for i in items),
                    "equipped_count":len(items)})

@app.route("/api/missions/<session_id>/tasks/<int:mission_idx>", methods=["GET"])
def mission_tasks_get(session_id, mission_idx):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM mission_tasks WHERE session_id=? AND mission_idx=? ORDER BY task_idx",
            (session_id, mission_idx)).fetchall()
    return jsonify({"tasks": rows_to_list(rows), "mission_idx": mission_idx})

@app.route("/api/missions/<session_id>/tasks/<int:mission_idx>/<int:task_idx>", methods=["POST"])
def mission_task_complete(session_id, mission_idx, task_idx):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM mission_tasks WHERE session_id=? AND mission_idx=? AND task_idx=?",
            (session_id, mission_idx, task_idx)).fetchone()
        if existing:
            conn.execute(
                "UPDATE mission_tasks SET completed=1,completed_at=? WHERE session_id=? AND mission_idx=? AND task_idx=?",
                (datetime.utcnow().isoformat(), session_id, mission_idx, task_idx))
        else:
            conn.execute(
                "INSERT INTO mission_tasks (session_id,mission_idx,task_idx,completed,completed_at) VALUES (?,?,?,1,?)",
                (session_id, mission_idx, task_idx, datetime.utcnow().isoformat()))
        conn.commit()
    return jsonify({"mission_idx": mission_idx, "task_idx": task_idx, "completed": True})

# ── Vercel WSGI handler ───────────────────────────────────────────────────
# Vercel looks for a variable named `app` that is a WSGI callable.
# Flask's app object IS a WSGI callable, so no wrapper needed.

# Local dev only
if __name__ == "__main__":
    print("Running locally at http://localhost:5000")
    app.run(debug=True, port=5000)
