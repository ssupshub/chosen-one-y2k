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

            CREATE TABLE IF NOT EXISTS achievements (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                unlocked_at  TEXT DEFAULT (datetime('now')),
                UNIQUE(session_id, achievement_id)
            );

            CREATE TABLE IF NOT EXISTS enemy_respawn (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                enemy_key    TEXT NOT NULL,
                defeated_at  TEXT DEFAULT (datetime('now')),
                ng_plus      INTEGER DEFAULT 0,
                UNIQUE(session_id, enemy_key)
            );

            CREATE TABLE IF NOT EXISTS hero_profile (
                session_id      TEXT PRIMARY KEY,
                hero_name       TEXT DEFAULT 'HERO',
                total_battles   INTEGER DEFAULT 0,
                battles_won     INTEGER DEFAULT 0,
                battles_lost    INTEGER DEFAULT 0,
                perfect_wins    INTEGER DEFAULT 0,
                total_damage    INTEGER DEFAULT 0,
                ng_plus_level   INTEGER DEFAULT 0,
                created_at      TEXT DEFAULT (datetime('now')),
                updated_at      TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS battle_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                enemy_key    TEXT NOT NULL,
                result       TEXT NOT NULL,
                damage_dealt INTEGER DEFAULT 0,
                turns        INTEGER DEFAULT 0,
                perfect      INTEGER DEFAULT 0,
                ng_plus      INTEGER DEFAULT 0,
                fought_at    TEXT DEFAULT (datetime('now'))
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

# ---------------------------------------------------------------------------
# ACHIEVEMENTS  /api/achievements
# ---------------------------------------------------------------------------

ACHIEVEMENT_CATALOG = {
    # Battle achievements
    "first_blood":      {"name":"FIRST BLOOD",          "desc":"Win your first battle",                    "rarity":"common",   "icon":"⚔️",  "xp":25},
    "five_kills":       {"name":"KILLING SPREE",         "desc":"Defeat 5 enemies total",                   "rarity":"common",   "icon":"💀",  "xp":50},
    "malkor_slain":     {"name":"VIRUS LORD SLAYER",     "desc":"Defeat MALKOR.EXE",                        "rarity":"legendary","icon":"👑",  "xp":500},
    "perfect_win":      {"name":"FLAWLESS VICTORY",      "desc":"Win a battle without taking damage",       "rarity":"rare",     "icon":"✨",  "xp":150},
    "three_perfect":    {"name":"UNTOUCHABLE",           "desc":"Win 3 battles without taking damage",      "rarity":"epic",     "icon":"🛡️", "xp":300},
    "all_enemies":      {"name":"EXTERMINATOR",          "desc":"Defeat all 5 enemy types",                 "rarity":"rare",     "icon":"🏆",  "xp":200},
    "ng_plus":          {"name":"NEW GAME+",             "desc":"Complete NG+ cycle 1",                     "rarity":"epic",     "icon":"🔄",  "xp":400},
    "ng_plus_3":        {"name":"VETERAN CHOSEN ONE",    "desc":"Complete NG+ cycle 3",                     "rarity":"legendary","icon":"⚡",  "xp":750},
    "special_attack":   {"name":"ULTIMATE USER",         "desc":"Use the SPECIAL move 10 times",            "rarity":"uncommon", "icon":"💥",  "xp":75},
    "block_master":     {"name":"BLOCK MASTER",          "desc":"Block 20 attacks successfully",            "rarity":"uncommon", "icon":"🛡️", "xp":75},
    # Mission achievements
    "first_mission":    {"name":"MISSION ACCEPTED",      "desc":"Complete your first mission",              "rarity":"common",   "icon":"📋",  "xp":30},
    "all_missions":     {"name":"MISSION ACCOMPLISHED",  "desc":"Complete all 7 missions",                  "rarity":"legendary","icon":"🌟",  "xp":600},
    # Social achievements
    "guestbook_signed": {"name":"SIGNED AND SEALED",     "desc":"Sign the guestbook",                       "rarity":"common",   "icon":"📖",  "xp":50},
    "chat_active":      {"name":"COUNCIL MEMBER",        "desc":"Send 10 messages in alliance chat",        "rarity":"uncommon", "icon":"💬",  "xp":60},
    # Inventory achievements
    "legendary_item":   {"name":"LEGENDARY COLLECTOR",   "desc":"Obtain a legendary item",                  "rarity":"rare",     "icon":"🔮",  "xp":100},
    "full_loadout":     {"name":"FULLY LOADED",          "desc":"Have all 4 item slots equipped",           "rarity":"uncommon", "icon":"⚙️",  "xp":80},
    # Hidden achievements
    "die_to_worm":      {"name":"EMBARRASSING DEFEAT",   "desc":"Lose a battle to CHAINMAIL_WORM",          "rarity":"common",   "icon":"🐛",  "xp":10},
    "speedrun":         {"name":"SPEEDRUNNER",           "desc":"Win a battle in 3 turns or fewer",         "rarity":"rare",     "icon":"⚡",  "xp":120},
    "visitor":          {"name":"JUST VISITING",         "desc":"Visit the site 10 times",                  "rarity":"common",   "icon":"👀",  "xp":20},
}

@app.route("/api/achievements/<session_id>", methods=["GET"])
def achievements_get(session_id):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT achievement_id, unlocked_at FROM achievements WHERE session_id=?",
            (session_id,)
        ).fetchall()
    unlocked = {r["achievement_id"]: r["unlocked_at"] for r in rows}
    result = []
    for aid, ach in ACHIEVEMENT_CATALOG.items():
        entry = dict(ach)
        entry["id"]          = aid
        entry["unlocked"]    = aid in unlocked
        entry["unlocked_at"] = unlocked.get(aid)
        result.append(entry)
    total_xp = sum(ACHIEVEMENT_CATALOG[aid]["xp"] for aid in unlocked)
    return jsonify({"achievements": result, "unlocked_count": len(unlocked),
                    "total": len(ACHIEVEMENT_CATALOG), "achievement_xp": total_xp})

@app.route("/api/achievements/<session_id>/unlock/<achievement_id>", methods=["POST"])
def achievement_unlock(session_id, achievement_id):
    if achievement_id not in ACHIEVEMENT_CATALOG:
        return jsonify({"error": "unknown achievement"}), 404
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM achievements WHERE session_id=? AND achievement_id=?",
            (session_id, achievement_id)
        ).fetchone()
        if existing:
            return jsonify({"already_unlocked": True, "achievement_id": achievement_id})
        conn.execute(
            "INSERT INTO achievements (session_id, achievement_id) VALUES (?,?)",
            (session_id, achievement_id)
        )
        conn.commit()
    ach = dict(ACHIEVEMENT_CATALOG[achievement_id])
    ach["id"] = achievement_id
    ach["newly_unlocked"] = True
    return jsonify(ach), 201

@app.route("/api/achievements/<session_id>/check", methods=["POST"])
def achievements_check(session_id):
    """Auto-check and unlock any earned achievements based on current state."""
    data = request.get_json(force=True) or {}
    newly_unlocked = []

    with get_db() as conn:
        # Get existing unlocked
        existing = set(r["achievement_id"] for r in conn.execute(
            "SELECT achievement_id FROM achievements WHERE session_id=?", (session_id,)
        ).fetchall())

        def unlock(aid):
            if aid not in existing and aid in ACHIEVEMENT_CATALOG:
                conn.execute(
                    "INSERT OR IGNORE INTO achievements (session_id, achievement_id) VALUES (?,?)",
                    (session_id, aid)
                )
                existing.add(aid)
                ach = dict(ACHIEVEMENT_CATALOG[aid])
                ach["id"] = aid
                newly_unlocked.append(ach)

        kills        = data.get("kills", 0)
        battles_won  = data.get("battles_won", 0)
        perfect_wins = data.get("perfect_wins", 0)
        missions_done= data.get("missions_done", 0)
        enemy_types  = data.get("enemy_types_defeated", [])
        turns_last   = data.get("turns_last_battle", 99)
        last_result  = data.get("last_result", "")
        last_enemy   = data.get("last_enemy", "")
        ng_level     = data.get("ng_plus_level", 0)
        specials_used= data.get("specials_used", 0)
        blocks_used  = data.get("blocks_used", 0)
        inv_equipped = data.get("inventory_equipped", 0)
        chat_msgs    = data.get("chat_messages_sent", 0)
        has_legendary= data.get("has_legendary_item", False)
        visit_count  = data.get("visit_count", 0)

        if battles_won >= 1:                        unlock("first_blood")
        if kills >= 5:                              unlock("five_kills")
        if "MALKOR" in enemy_types:                unlock("malkor_slain")
        if perfect_wins >= 1:                       unlock("perfect_win")
        if perfect_wins >= 3:                       unlock("three_perfect")
        if len(enemy_types) >= 5:                   unlock("all_enemies")
        if ng_level >= 1:                           unlock("ng_plus")
        if ng_level >= 3:                           unlock("ng_plus_3")
        if specials_used >= 10:                     unlock("special_attack")
        if blocks_used >= 20:                       unlock("block_master")
        if missions_done >= 1:                      unlock("first_mission")
        if missions_done >= 7:                      unlock("all_missions")
        if last_result == "win" and turns_last <= 3:unlock("speedrun")
        if last_result == "lose" and last_enemy == "CHAINMAIL_WORM": unlock("die_to_worm")
        if inv_equipped >= 4:                       unlock("full_loadout")
        if has_legendary:                           unlock("legendary_item")
        if chat_msgs >= 10:                         unlock("chat_active")
        if visit_count >= 10:                       unlock("visitor")

        conn.commit()

    return jsonify({"newly_unlocked": newly_unlocked, "count": len(newly_unlocked)})


# ---------------------------------------------------------------------------
# ENEMY RESPAWN + NEW GAME+  /api/respawn
# ---------------------------------------------------------------------------

RESPAWN_HOURS = 24   # hours before enemy respawns

@app.route("/api/respawn/<session_id>", methods=["GET"])
def respawn_status(session_id):
    """Return defeat/respawn status for all enemies."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM enemy_respawn WHERE session_id=?", (session_id,)
        ).fetchall()
        profile = conn.execute(
            "SELECT ng_plus_level FROM hero_profile WHERE session_id=?", (session_id,)
        ).fetchone()

    ng_level   = profile["ng_plus_level"] if profile else 0
    now        = datetime.utcnow()
    enemy_keys = ["MALKOR","POPUP_GENERAL","COOKIE_THIEF","DIALUP_DRAIN","CHAINMAIL_WORM"]
    defeat_map = {r["enemy_key"]: r for r in rows}
    result     = {}

    for key in enemy_keys:
        row = defeat_map.get(key)
        if not row:
            result[key] = {"defeated": False, "respawns_in_seconds": 0, "ng_plus": ng_level}
        else:
            defeated_at  = datetime.fromisoformat(row["defeated_at"])
            respawn_time = defeated_at.replace(tzinfo=None)
            elapsed_secs = (now - respawn_time).total_seconds()
            respawn_secs = RESPAWN_HOURS * 3600
            remaining    = max(0, respawn_secs - elapsed_secs)
            result[key]  = {
                "defeated":           True,
                "defeated_at":        row["defeated_at"],
                "respawns_in_seconds":int(remaining),
                "respawned":          remaining == 0,
                "ng_plus":            row["ng_plus"],
            }

    all_defeated = all(
        result[k]["defeated"] and not result[k]["respawned"]
        for k in enemy_keys
    )

    return jsonify({
        "enemies":     result,
        "ng_plus_level": ng_level,
        "all_defeated": all_defeated,
    })

@app.route("/api/respawn/<session_id>/defeat/<enemy_key>", methods=["POST"])
def respawn_defeat(session_id, enemy_key):
    """Record an enemy as defeated."""
    with get_db() as conn:
        profile = conn.execute(
            "SELECT ng_plus_level FROM hero_profile WHERE session_id=?", (session_id,)
        ).fetchone()
        ng_level = profile["ng_plus_level"] if profile else 0

        conn.execute(
            """INSERT INTO enemy_respawn (session_id, enemy_key, defeated_at, ng_plus)
               VALUES (?,?,?,?)
               ON CONFLICT(session_id, enemy_key)
               DO UPDATE SET defeated_at=excluded.defeated_at, ng_plus=excluded.ng_plus""",
            (session_id, enemy_key.upper(), datetime.utcnow().isoformat(), ng_level)
        )

        # Check if all 5 enemies are now defeated → trigger NG+
        defeated_count = conn.execute(
            """SELECT COUNT(*) FROM enemy_respawn
               WHERE session_id=? AND ng_plus=?""",
            (session_id, ng_level)
        ).fetchone()[0]

        ng_triggered = False
        if defeated_count >= 5:
            new_ng = ng_level + 1
            conn.execute(
                """INSERT INTO hero_profile (session_id, ng_plus_level, updated_at)
                   VALUES (?,?,?)
                   ON CONFLICT(session_id)
                   DO UPDATE SET ng_plus_level=?, updated_at=?""",
                (session_id, new_ng, datetime.utcnow().isoformat(),
                 new_ng, datetime.utcnow().isoformat())
            )
            # Reset all enemy defeat records for new NG+ cycle
            conn.execute(
                "DELETE FROM enemy_respawn WHERE session_id=?", (session_id,)
            )
            ng_triggered = True

        conn.commit()

    return jsonify({
        "enemy_key":    enemy_key.upper(),
        "ng_triggered": ng_triggered,
        "ng_level":     ng_level + (1 if ng_triggered else 0),
    })

@app.route("/api/respawn/<session_id>/ng_plus_stats/<enemy_key>", methods=["GET"])
def ng_plus_stats(session_id, enemy_key):
    """Return scaled enemy stats for current NG+ level."""
    with get_db() as conn:
        profile = conn.execute(
            "SELECT ng_plus_level FROM hero_profile WHERE session_id=?", (session_id,)
        ).fetchone()
    ng = profile["ng_plus_level"] if profile else 0
    scale = 1 + (ng * 0.2)   # +20% per NG+ level
    return jsonify({"ng_plus_level": ng, "stat_multiplier": scale,
                    "enemy_key": enemy_key.upper()})


# ---------------------------------------------------------------------------
# HERO PROFILE  /api/profile
# ---------------------------------------------------------------------------

@app.route("/api/profile/<session_id>", methods=["GET"])
def profile_get(session_id):
    with get_db() as conn:
        profile  = conn.execute(
            "SELECT * FROM hero_profile WHERE session_id=?", (session_id,)
        ).fetchone()
        score    = conn.execute(
            "SELECT * FROM scores WHERE session_id=?", (session_id,)
        ).fetchone()
        ach_count= conn.execute(
            "SELECT COUNT(*) FROM achievements WHERE session_id=?", (session_id,)
        ).fetchone()[0]
        ach_xp   = sum(
            ACHIEVEMENT_CATALOG.get(r["achievement_id"], {}).get("xp", 0)
            for r in conn.execute(
                "SELECT achievement_id FROM achievements WHERE session_id=?", (session_id,)
            ).fetchall()
        )
        inv_count= conn.execute(
            "SELECT COUNT(*) FROM inventory WHERE session_id=?", (session_id,)
        ).fetchone()[0]
        equipped = conn.execute(
            "SELECT SUM(atk_bonus) as atk, SUM(def_bonus) as def, SUM(hp_bonus) as hp "
            "FROM inventory WHERE session_id=? AND equipped=1", (session_id,)
        ).fetchone()
        missions_done = conn.execute(
            "SELECT COUNT(*) FROM missions WHERE session_id=? AND completed=1", (session_id,)
        ).fetchone()[0]
        history  = conn.execute(
            "SELECT * FROM battle_history WHERE session_id=? ORDER BY fought_at DESC LIMIT 10",
            (session_id,)
        ).fetchall()

    prof = row_to_dict(profile) if profile else {
        "session_id": session_id, "hero_name": "HERO",
        "total_battles": 0, "battles_won": 0, "battles_lost": 0,
        "perfect_wins": 0, "total_damage": 0, "ng_plus_level": 0,
    }
    sc = row_to_dict(score) if score else {"xp": 0, "kills": 0}

    win_rate = 0
    if prof["total_battles"] > 0:
        win_rate = round(prof["battles_won"] / prof["total_battles"] * 100)

    return jsonify({
        "profile":          prof,
        "score":            sc,
        "achievements":     {"unlocked": ach_count, "total": len(ACHIEVEMENT_CATALOG), "xp": ach_xp},
        "inventory":        {"total": inv_count, "atk_bonus": equipped["atk"] or 0,
                             "def_bonus": equipped["def"] or 0, "hp_bonus": equipped["hp"] or 0},
        "missions_done":    missions_done,
        "win_rate":         win_rate,
        "battle_history":   rows_to_list(history),
    })

@app.route("/api/profile/<session_id>", methods=["POST"])
def profile_update(session_id):
    data = request.get_json(force=True) or {}
    hero_name     = (data.get("hero_name") or "HERO").strip()
    total_battles = int(data.get("total_battles") or 0)
    battles_won   = int(data.get("battles_won") or 0)
    battles_lost  = int(data.get("battles_lost") or 0)
    perfect_wins  = int(data.get("perfect_wins") or 0)
    total_damage  = int(data.get("total_damage") or 0)

    with get_db() as conn:
        conn.execute(
            """INSERT INTO hero_profile
               (session_id, hero_name, total_battles, battles_won, battles_lost,
                perfect_wins, total_damage, updated_at)
               VALUES (?,?,?,?,?,?,?,?)
               ON CONFLICT(session_id) DO UPDATE SET
               hero_name=excluded.hero_name,
               total_battles=excluded.total_battles,
               battles_won=excluded.battles_won,
               battles_lost=excluded.battles_lost,
               perfect_wins=excluded.perfect_wins,
               total_damage=excluded.total_damage,
               updated_at=excluded.updated_at""",
            (session_id, hero_name, total_battles, battles_won, battles_lost,
             perfect_wins, total_damage, datetime.utcnow().isoformat())
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM hero_profile WHERE session_id=?", (session_id,)
        ).fetchone()
    return jsonify(row_to_dict(row)), 201

@app.route("/api/profile/<session_id>/battle", methods=["POST"])
def profile_record_battle(session_id):
    """Record a completed battle in history."""
    data   = request.get_json(force=True) or {}
    enemy  = (data.get("enemy_key") or "UNKNOWN").upper()
    result = (data.get("result") or "").lower()
    dmg    = int(data.get("damage_dealt") or 0)
    turns  = int(data.get("turns") or 0)
    perfect= 1 if data.get("perfect") else 0
    ng     = int(data.get("ng_plus") or 0)

    with get_db() as conn:
        conn.execute(
            """INSERT INTO battle_history
               (session_id, enemy_key, result, damage_dealt, turns, perfect, ng_plus)
               VALUES (?,?,?,?,?,?,?)""",
            (session_id, enemy, result, dmg, turns, perfect, ng)
        )
        # Update profile counters
        won  = 1 if result == "win" else 0
        lost = 1 if result == "lose" else 0
        conn.execute(
            """INSERT INTO hero_profile
               (session_id, hero_name, total_battles, battles_won, battles_lost,
                perfect_wins, total_damage, updated_at)
               VALUES (?,?,1,?,?,?,?,?)
               ON CONFLICT(session_id) DO UPDATE SET
               total_battles = total_battles + 1,
               battles_won   = battles_won + ?,
               battles_lost  = battles_lost + ?,
               perfect_wins  = perfect_wins + ?,
               total_damage  = total_damage + ?,
               updated_at    = ?""",
            (session_id, "HERO", won, lost, perfect, dmg, datetime.utcnow().isoformat(),
             won, lost, perfect, dmg, datetime.utcnow().isoformat())
        )
        conn.commit()

    return jsonify({"recorded": True, "result": result, "enemy": enemy}), 201


# ── Vercel WSGI handler ───────────────────────────────────────────────────
# Vercel looks for a variable named `app` that is a WSGI callable.
# Flask's app object IS a WSGI callable, so no wrapper needed.

# Local dev only
if __name__ == "__main__":
    print("Running locally at http://localhost:5000")
    app.run(debug=True, port=5000)
