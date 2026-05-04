/**
 * api.js — Frontend API client for chosen-one-y2k
 * All pages import this via <script src="../../assets/js/api.js"></script>
 *
 * BASE URL logic:
 *   - localhost / 127.0.0.1  → http://localhost:5000/api  (local Flask dev server)
 *   - Vercel / any other host → /api                       (Vercel serverless function)
 */

const API = (() => {
  const isLocal = (
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.protocol === "file:"
  );
  const BASE = isLocal ? "http://localhost:5000/api" : "/api";

  async function req(method, path, body) {
    const opts = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(BASE + path, opts);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || "Request failed: " + res.status);
      }
      return await res.json();
    } catch (e) {
      console.warn("[API]", method, path, "=>", e.message);
      throw e;
    }
  }

  const get  = (path)        => req("GET",  path);
  const post = (path, body)  => req("POST", path, body);

  // ── Session ────────────────────────────────────────────────────────────
  function getSessionId() {
    let sid = localStorage.getItem("chosen_session");
    if (!sid) {
      sid = Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem("chosen_session", sid);
    }
    return sid;
  }

  function getHeroName() {
    return localStorage.getItem("chosen_hero") || "HERO";
  }

  function setHeroName(name) {
    localStorage.setItem("chosen_hero", name);
  }

  // ── Visitors ───────────────────────────────────────────────────────────
  async function getVisitors()      { return get("/visitors"); }
  async function incrementVisitors(){ return post("/visitors/increment"); }

  // ── Guestbook ──────────────────────────────────────────────────────────
  async function getGuestbook(page = 1, perPage = 4) {
    return get(`/guestbook?page=${page}&per_page=${perPage}`);
  }
  async function postGuestbook(entry) {
    return post("/guestbook", entry);
  }

  // ── Contact ────────────────────────────────────────────────────────────
  async function sendContact(data) {
    return post("/contact", data);
  }

  // ── Chat ───────────────────────────────────────────────────────────────
  async function getChat(channel = "global", sinceId = 0) {
    return get(`/chat?channel=${encodeURIComponent(channel)}&since_id=${sinceId}`);
  }
  async function postChat(sender, message, channel = "global") {
    return post("/chat", { sender, message, channel });
  }

  // ── Missions ───────────────────────────────────────────────────────────
  async function getMissions() {
    return get(`/missions/${getSessionId()}`);
  }
  async function toggleMission(idx) {
    return post(`/missions/${getSessionId()}/${idx}`);
  }

  // ── Scores ─────────────────────────────────────────────────────────────
  async function getLeaderboard() {
    return get("/scores");
  }
  async function updateScore(xp, kills) {
    return post(`/scores/${getSessionId()}`, {
      hero_name: getHeroName(),
      xp,
      kills,
    });
  }

  // ── World events ───────────────────────────────────────────────────────
  async function getEvents(limit = 8) {
    return get(`/events?limit=${limit}`);
  }
  async function postEvent(region, eventText) {
    return post("/events", { region, event_text: eventText });
  }

  // ── Health ─────────────────────────────────────────────────────────────
  async function health() { return get("/health"); }

  return {
    BASE,
    getSessionId,
    getHeroName,
    setHeroName,
    getVisitors,
    incrementVisitors,
    getGuestbook,
    postGuestbook,
    sendContact,
    getChat,
    postChat,
    getMissions,
    toggleMission,
    getLeaderboard,
    updateScore,
    getEvents,
    postEvent,
    health,
  };
})();
