/**
 * sounds.js — Retro Web Audio sound engine for chosen-one-y2k
 * All sounds are procedurally generated. No audio files needed.
 * Include this before any page scripts.
 */

const SFX = (() => {
  let ctx = null;
  let enabled = true;

  function getCtx() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    // Resume if suspended (browser autoplay policy)
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  function setEnabled(val) {
    enabled = val;
    localStorage.setItem('chosen_sfx', val ? '1' : '0');
  }

  function isEnabled() {
    const stored = localStorage.getItem('chosen_sfx');
    if (stored !== null) enabled = stored === '1';
    return enabled;
  }

  // ── Low-level helpers ──────────────────────────────────────────────────

  function osc(type, freq, start, dur, gainVal, ac) {
    const o = ac.createOscillator();
    const g = ac.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, start);
    g.gain.setValueAtTime(gainVal, start);
    g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    o.connect(g);
    g.connect(ac.destination);
    o.start(start);
    o.stop(start + dur + 0.01);
    return { osc: o, gain: g };
  }

  function noise(dur, gainVal, ac) {
    const bufSize = ac.sampleRate * dur;
    const buf = ac.createBuffer(1, bufSize, ac.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) data[i] = Math.random() * 2 - 1;
    const src = ac.createBufferSource();
    const g   = ac.createGain();
    src.buffer = buf;
    g.gain.setValueAtTime(gainVal, ac.currentTime);
    g.gain.exponentialRampToValueAtTime(0.0001, ac.currentTime + dur);
    src.connect(g);
    g.connect(ac.destination);
    src.start();
    return src;
  }

  // ── Sound definitions ──────────────────────────────────────────────────

  /**
   * Dial-up modem handshake — plays on page load.
   * Sequence of tones mimicking an actual modem negotiation.
   */
  function modemConnect() {
    if (!isEnabled()) return;
    const ac = getCtx();
    const now = ac.currentTime;

    // Phase 1: dial tone
    osc('sine', 440, now,        0.4, 0.15, ac);
    osc('sine', 480, now,        0.4, 0.15, ac);

    // Phase 2: carrier detection squeal
    const seq = [
      [1200, 0.08], [2400, 0.06], [1800, 0.08], [600, 0.05],
      [3000, 0.06], [1200, 0.08], [2400, 0.05], [900, 0.07],
    ];
    let t = now + 0.5;
    seq.forEach(([freq, dur]) => {
      osc('sawtooth', freq, t, dur, 0.08, ac);
      t += dur + 0.01;
    });

    // Phase 3: handshake noise burst
    const noiseStart = t;
    const nBuf = ac.sampleRate * 0.6;
    const nBufNode = ac.createBuffer(1, nBuf, ac.sampleRate);
    const nData = nBufNode.getChannelData(0);
    for (let i = 0; i < nBuf; i++) nData[i] = (Math.random() * 2 - 1) * 0.3;
    const nSrc = ac.createBufferSource();
    const nGain = ac.createGain();
    nSrc.buffer = nBufNode;
    nGain.gain.setValueAtTime(0.15, noiseStart);
    nGain.gain.linearRampToValueAtTime(0, noiseStart + 0.6);
    nSrc.connect(nGain);
    nGain.connect(ac.destination);
    nSrc.start(noiseStart);

    // Phase 4: CONNECTED confirmation tone
    const connTime = noiseStart + 0.7;
    osc('sine', 1004, connTime,       0.12, 0.2, ac);
    osc('sine', 1004, connTime + 0.15, 0.12, 0.2, ac);
    osc('sine', 1004, connTime + 0.30, 0.25, 0.2, ac);
  }

  /**
   * UI click blip — used on any button press.
   */
  function blip() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;
    osc('square', 880, now,        0.03, 0.18, ac);
    osc('square', 660, now + 0.03, 0.04, 0.10, ac);
  }

  /**
   * Negative / error blip.
   */
  function bloop() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;
    osc('square', 220, now,        0.05, 0.2, ac);
    osc('square', 180, now + 0.05, 0.08, 0.15, ac);
  }

  /**
   * Mission complete jingle — ascending fanfare.
   */
  function missionComplete() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;

    const notes = [523, 659, 784, 1047]; // C5 E5 G5 C6
    notes.forEach((freq, i) => {
      osc('square', freq, now + i * 0.12, 0.18, 0.18, ac);
    });
    // Final chord swell
    osc('square', 523,  now + 0.6, 0.4, 0.12, ac);
    osc('square', 659,  now + 0.6, 0.4, 0.10, ac);
    osc('square', 784,  now + 0.6, 0.4, 0.08, ac);
    osc('square', 1047, now + 0.6, 0.4, 0.06, ac);
  }

  /**
   * Enemy defeated — descending crash.
   */
  function enemyDefeat() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;
    osc('sawtooth', 440, now,        0.05, 0.25, ac);
    osc('sawtooth', 220, now + 0.06, 0.10, 0.20, ac);
    osc('sawtooth', 110, now + 0.17, 0.15, 0.15, ac);
    noise(0.2, 0.1, ac);
  }

  /**
   * Alert / warning ping.
   */
  function alert() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;
    osc('sine', 880, now,        0.08, 0.3, ac);
    osc('sine', 880, now + 0.15, 0.08, 0.3, ac);
  }

  /**
   * Chat message received.
   */
  function chatPing() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;
    osc('sine', 1200, now,        0.04, 0.15, ac);
    osc('sine', 1600, now + 0.05, 0.04, 0.12, ac);
  }

  /**
   * Weapon equipped.
   */
  function equip() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;
    osc('square', 330, now,        0.04, 0.2, ac);
    osc('square', 440, now + 0.05, 0.04, 0.2, ac);
    osc('square', 550, now + 0.10, 0.06, 0.2, ac);
  }

  /**
   * Guestbook signed / form submitted.
   */
  function formSubmit() {
    if (!isEnabled()) return;
    const ac  = getCtx();
    const now = ac.currentTime;
    osc('sine', 660, now,        0.06, 0.2, ac);
    osc('sine', 880, now + 0.07, 0.10, 0.2, ac);
  }

  // ── Auto-wire all buttons on DOMContentLoaded ──────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
      const el = e.target.closest('button, .btn, a.menu-item');
      if (el) blip();
    });
  });

  return {
    modemConnect,
    blip,
    bloop,
    missionComplete,
    enemyDefeat,
    alert,
    chatPing,
    equip,
    formSubmit,
    setEnabled,
    isEnabled,
  };
})();
