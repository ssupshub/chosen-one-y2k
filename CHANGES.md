# CHANGES.md — chosen-one-y2k

Complete changelog, upcoming features and known bug tracker.

---

## VERSION HISTORY

---

### v1.0.0 — Initial Release
**Released: May 2026**

First commit. The world needed saving. A website was born.

#### Added
- 9-page retro Y2K-themed hero website
- Home page with animated visitor counter and world status panel
- Shared navigation across all pages
- CRT scanline overlay and screen flicker effect
- Scrolling marquee banners on every page
- Static HTML with inline CSS and vanilla JavaScript
- No frameworks, no build step

#### Pages shipped
- `index.html` — Home page with visitor counter, world status, mission intro
- `mission.html` — Mission checklist (original static version)
- `prophecy.html` — Ancient prophecy scrolls
- `enemies.html` — Enemy database (static, no battle)
- `weapons.html` — Armory with loadout builder
- `alliances.html` — Ally roster with simulated chat
- `world.html` — ASCII world map with clickable regions
- `guestbook.html` — Guestbook with local in-memory entries
- `contact.html` — Contact form (frontend only)

---

### v1.1.0 — Flask Backend + SQLite
**Released: May 2026**

Every interactive feature now talks to a real database.

#### Added
- Python Flask backend (`backend/app.py`)
- SQLite database (`backend/chosen.db`) auto-created on first run
- `api.js` — shared frontend API client used by all pages
- Windows launcher (`start.bat`)
- Mac/Linux launcher (`start.sh`)
- Seeded starter data: guestbook entries, chat history, world events
- `backend/requirements.txt`

#### API endpoints added
- `GET/POST /api/guestbook` — persistent guestbook with pagination
- `POST /api/contact` — contact messages saved to database
- `GET/POST /api/chat` — real-time global alliance chat with auto ally replies
- `GET/POST /api/missions/<session>` — mission progress per session
- `GET/POST /api/scores/<session>` — hero leaderboard
- `GET/POST /api/events` — world event log
- `GET /api/visitors` and `POST /api/visitors/increment`
- `GET /api/session/new` and `GET /api/health`

#### Changed
- Guestbook now reads/writes from database (paginated, persistent)
- Alliance chat polls backend every 4 seconds
- Mission progress persists across page reloads via session ID in localStorage
- Visitor counter is real and increments on every page load
- World events fed live from database

---

### v1.2.0 — Hero Setup, Sounds and Light Mode
**Released: May 2026**

Four quality-of-life features shipped together.

#### Added
- `hero-setup.js` — hero name setup screen on first visit
  - Full-screen modal with ASCII banner
  - Name auto-uppercases, strips invalid characters
  - Name shown in navbar on every page as `[HERO: NAME]`
  - Click name in navbar to rename at any time
- `sounds.js` — procedural Web Audio sound engine (zero audio files)
  - Dial-up modem handshake on every page load
  - Retro blip on every button and nav click
  - Victory jingle (4-note fanfare + chord) on mission complete
  - Enemy defeat crash sound
  - Weapon equip chime
  - Form submit confirmation tone
  - Chat ping when ally messages arrive
  - `[ SFX ON / OFF ]` toggle in navbar
- Light/dark mode toggle in navbar
  - Dark: CRT green on black (default)
  - Light: washed-out beige/sepia early-web look
  - Preference saved to localStorage, applied before first paint
- Typing indicator in alliance chat
  - Private DMs: `Wizard_42 is typing...` appears immediately, cleared on reply
  - Global chat: random ally shown typing with 600-1400ms human delay
  - Safety timeout clears indicator after 4 seconds

#### Changed
- All pages now include `sounds.js` and `hero-setup.js`
- `API.getHeroName()` returns the name from localStorage
- Alliance chat ally replies use hero name from localStorage

---

### v1.3.0 — Project Restructure
**Released: May 2026**

Flat root structure was unprofessional. Reorganised into proper folders.

#### Changed
- All HTML pages moved to `frontend/pages/`
- CSS moved to `frontend/assets/css/style.css`
- JS files moved to `frontend/assets/js/`
- All asset paths updated in every HTML file (`../../assets/css/style.css` etc.)
- Inter-page nav links verified correct after move
- README updated with new tree structure

#### Structure after v1.3.0
```
chosen-one-y2k/
├── frontend/
│   ├── pages/        9 HTML files
│   └── assets/
│       ├── css/      style.css
│       └── js/       api.js, sounds.js, hero-setup.js
├── backend/          app.py, requirements.txt
├── start.bat
├── start.sh
└── README.md
```

---

### v1.4.0 — Vercel Deployment
**Released: May 2026**

Frontend and backend deployable to Vercel with zero config changes.

#### Added
- `api/index.py` — Vercel Python serverless function (all API routes)
  - Database writes to `/tmp/chosen.db` (Vercel ephemeral storage)
  - Identical routes to `backend/app.py`
  - Seeds starter data on cold start
- `vercel.json` — routing and build configuration
  - `/api/*` routes to Python serverless function
  - `/`, `/mission`, `/enemies` etc. route to HTML pages
  - `/assets/*` routes to static files
- `requirements.txt` at root level (Vercel reads this)
- `.gitignore` updated to exclude `.vercel/` and `*.db`

#### Changed
- `api.js` BASE URL auto-detects environment
  - `localhost` or `127.0.0.1` or `file://` → `http://localhost:5000/api`
  - Any other host (Vercel) → `/api`
- All nav links changed from `.html` extensions to clean URLs (`/mission`, `/guestbook` etc.)

---

### v1.5.0 — 1v1 Battle System
**Released: May 2026**

Enemy Files page now features a full turn-based fight screen.

#### Added
- Full-screen battle overlay with Street Fighter / Tekken aesthetic
- HP bars, special bars, and VS header for both fighters
- 5 enemies with unique stats, moves and behaviour
  - MALKOR.EXE (500 HP, CRITICAL) — enters RAGE MODE below 25% HP
  - POPUP_GENERAL.EXE (280 HP, HIGH)
  - COOKIE_THIEF.BAT (200 HP, HIGH)
  - DIALUP_DRAIN.VBS (150 HP, MEDIUM)
  - CHAINMAIL_WORM.EXE (60 HP, LOW)
- 6 hero moves: PUNCH, KICK, HACK, BLOCK, DODGE, SPECIAL
  - HACK is slow — enemy attacks first
  - BLOCK reduces incoming damage by 70%
  - DODGE has 60% chance to avoid all damage
  - SPECIAL requires full bar, deals 40-60 base damage
- Status effects: BURN (damage per turn), STUN (lose turn), SHIELD (absorb hit)
- Floating damage numbers on every hit
- Sprite animations: shake, flash, jump, dodge, KO fall
- SPECIAL FX text overlays for criticals, rage mode, ultimates
- Round announcement overlay
- Win/lose result screen with stats (damage dealt, turns, HP remaining)
- Keyboard shortcuts: keys 1-6 for moves, Escape to exit
- Kills and XP synced to backend leaderboard on win
- Rematch button on result screen
- Search and filter system (by name, threat level, defeated status)

---

### v1.6.0 — Mission Tasks and Inventory System
**Released: May 2026**

Missions now redirect to dedicated task pages. Enemies drop loot.

#### Added
- `frontend/pages/mission-task.html` — individual task page per mission
  - 7 missions, each with 3-6 unique tasks
  - Step-tracker progress bar at top
  - Timed tasks auto-complete with countdown timer
  - Page-redirect tasks link to required page then let you mark complete
  - Battle tasks link directly to Enemy Files
  - All task completions saved to backend (`mission_tasks` table)
  - When all tasks done: mission auto-checked on backend, XP awarded, overlay shown
- `frontend/pages/inventory.html` — full inventory management page
  - Items loaded from backend per session
  - Filter tabs: ALL / EQUIPPED / WEAPONS / ARMOR / ACCESSORIES / RELICS / LEGENDARY
  - Equip/unequip with one-per-type-slot enforcement
  - Drop item with confirmation modal
  - Live ATK/DEF/HP bonus bars from equipped items
  - Toast notifications for all actions
  - Rarity colour coding: LEGENDARY / RARE / UNCOMMON / COMMON
- Item drop system — 12 unique items across 4 types
  - MALKOR drops: Virus Core (legendary), ZIP Fragment (legendary), Broadband Blade Shard (rare)
  - POPUP_GENERAL drops: Ad-Block Cannon Fragment, Popup Shield, Firewall Gauntlet
  - COOKIE_THIEF drops: Cracked Cookie Jar, Stolen Session Token
  - DIALUP_DRAIN drops: 56k Dial-up Crystal, Modem Whip
  - CHAINMAIL_WORM drops: Chain Mail Amulet, Popup Badge
  - Drops shown on battle win screen

#### Changed
- Mission page rewritten: clickable cards with task progress instead of checklist
- Mission cards show: title, description, XP, task progress `(2/4)`, status badge
- First 2 missions always unlocked; rest unlock sequentially
- Inventory nav link added to all pages
- `/inventory` and `/mission-task` routes added to `vercel.json`

#### Backend changes
- New table: `inventory` (items, equipped status, stat bonuses, drop source)
- New table: `mission_tasks` (per-session task completion)
- New routes: `GET/POST /api/inventory/<session>`
- New routes: `POST /api/inventory/<session>/drop/<enemy>`
- New routes: `POST /api/inventory/<session>/equip/<item>`
- New routes: `DELETE /api/inventory/<session>/remove/<item>`
- New routes: `GET /api/inventory/<session>/stats`
- New routes: `GET/POST /api/missions/<session>/tasks/<mission>/<task>`
- All routes mirrored in `api/index.py` for Vercel

---

## UPCOMING FEATURES

Features planned for future releases, in rough priority order.

---

### v1.7.0 — Real-time Chat (WebSockets)
Replace the 4-second polling on the alliance page with Flask-SocketIO.
Messages will appear instantly without any delay or polling overhead.

### v1.7.1 — User Accounts and Login
Replace session IDs with a proper username/password system using Flask-Login
and bcrypt. Missions, scores and inventory persist across devices and browsers.

### v1.8.0 — Save Slots
Three named save slots styled like a JRPG. Each slot stores mission progress,
loadout, kills and XP independently. Select slot on first visit.

### v1.8.1 — Mini-Game: ASCII Dungeon
A playable text-adventure dungeon on a new `/dungeon` page.
Turn-based movement, rooms with enemies, loot chests and a boss floor.
Full backend state persistence per session.

### v1.9.0 — Email Notifications (Flask-Mail)
Send a confirmation email when a contact form is submitted.
Alert registered heroes when world corruption hits 50%.
Optional: daily mission reminder emails.

### v1.9.1 — Admin Panel
Password-protected `/admin` page to:
- View all contact messages
- Delete guestbook entries
- Manually post world events
- Reset individual sessions
- View leaderboard management

### v2.0.0 — Persistent Database (Supabase)
Replace SQLite with Supabase (hosted Postgres) so data survives Vercel
cold starts and scales to multiple users. Zero downtime migration path.

### v2.1.0 — API Rate Limiting
Add Flask-Limiter to protect chat, guestbook and score endpoints from spam.
Configurable per-route limits with 429 responses.

### v2.1.1 — Input Sanitization
Strip HTML from all user-submitted content before saving to the database.
Add server-side validation to all POST endpoints.

### v2.2.0 — Expanded Battle System
- More enemy attacks with unique animations
- Item stat bonuses apply in battle (ATK/DEF/HP from equipped inventory)
- Boss health phases — MALKOR gets a second form at 0 HP
- Combo system: chain 3 hits for a bonus attack
- Post-battle XP breakdown screen

### v2.2.1 — Unit Tests
A `backend/tests/` folder with pytest covering every API route.
GitHub Actions CI workflow runs the suite on every push to main.

### v2.3.0 — Markdown in Guestbook
Render safe markdown in guestbook messages: `**bold**`, `_italic_`, `[link]`.
Strip dangerous tags server-side before saving.

### v2.4.0 — Mobile Layout
Currently readable on mobile but not optimised. Proper responsive layout
for screens under 480px. Touch-friendly battle buttons. Swipeable panels.

---

## KNOWN BUGS

---

### OPEN

| ID    | Severity | Description                                                                 | Workaround                              |
| ----- | -------- | --------------------------------------------------------------------------- | --------------------------------------- |
| BUG-1 | LOW      | Modem sound sometimes blocked by browser autoplay policy on first load      | Click anywhere on the page to trigger   |
| BUG-2 | LOW      | Light mode toggle flashes dark briefly on initial page load on slow devices | None — resolves within one frame        |
| BUG-3 | MEDIUM   | Typing indicator occasionally persists if backend is slow to respond        | Clears automatically after 4 seconds    |
| BUG-4 | LOW      | Battle DODGE animation sometimes fires on the wrong sprite in Firefox       | No gameplay impact                      |
| BUG-5 | LOW      | Vercel cold start can take 2-3 seconds, making first API call appear slow   | Subsequent calls are fast               |
| BUG-6 | MEDIUM   | Inventory items with duplicate item_id ignored silently on second drop      | By design — UNIQUE constraint prevents doubles |
| BUG-7 | LOW      | Mission timer resets to 9:59 when it hits 0:00 instead of showing expired  | Cosmetic only, no gameplay impact       |
| BUG-8 | LOW      | World map region buttons overlap on screens narrower than 500px             | Use desktop or landscape mobile         |

---

### FIXED

| ID     | Version Fixed | Description                                                              |
| ------ | ------------- | ------------------------------------------------------------------------ |
| FIX-1  | v1.1.0        | Guestbook entries lost on page refresh (moved to database)               |
| FIX-2  | v1.1.0        | Chat messages not persisting between sessions (backend added)            |
| FIX-3  | v1.2.0        | Hero name showing as HERO across all pages (hero-setup.js added)         |
| FIX-4  | v1.3.0        | Broken asset paths after folder restructure                              |
| FIX-5  | v1.3.0        | Nav links pointing to .html files instead of clean URLs                  |
| FIX-6  | v1.4.0        | API calls failing on Vercel because BASE URL was hardcoded to localhost  |
| FIX-7  | v1.5.0        | Battle SPECIAL button enabled before bar was full                        |
| FIX-8  | v1.5.0        | Enemy RAGE mode sprite not resetting between rematches                   |
| FIX-9  | v1.6.0        | Mission checklist state lost on reload (moved to backend session)        |
| FIX-10 | v1.6.0        | Inventory equip not unequipping previous item of same type               |

---

## CONTRIBUTING

This is a solo hero project. No pull requests accepted until the Chosen One
completes all 7 missions and defeats MALKOR.EXE.

---

## NOTES

- SQLite on Vercel uses `/tmp` which is ephemeral. Data resets on cold start.
  See v2.0.0 for the Supabase migration plan.
- All sounds are generated by the Web Audio API. No audio files required.
- The frontend works completely offline. Backend is optional for persistence.
- Session IDs are stored in localStorage. Clearing localStorage resets progress.

---

(C) 2001 THE COUNCIL OF ELDERS. DO NOT STEAL THIS HTML.
