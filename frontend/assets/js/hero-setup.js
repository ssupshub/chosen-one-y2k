/**
 * hero-setup.js — Hero name setup screen + light/dark mode toggle
 * Include on every page after style.css and before page scripts.
 *
 * On first visit: shows a full-screen setup modal to enter hero name.
 * On every visit: injects the mode toggle button into the navbar.
 */

(function () {

  // ── Constants ────────────────────────────────────────────────────────────
  const KEY_NAME  = 'chosen_hero';
  const KEY_THEME = 'chosen_theme';
  const KEY_SETUP = 'chosen_setup_done';

  // ── Theme ─────────────────────────────────────────────────────────────────

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(KEY_THEME, theme);
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) btn.textContent = theme === 'light' ? '[ CRT MODE ]' : '[ DAY MODE ]';
  }

  function toggleTheme() {
    const current = localStorage.getItem(KEY_THEME) || 'dark';
    applyTheme(current === 'dark' ? 'light' : 'dark');
    if (window.SFX) SFX.blip();
  }

  function injectThemeStyles() {
    const style = document.createElement('style');
    style.textContent = `
      /* ── LIGHT MODE (day mode) ─────────────────────────────────────── */
      [data-theme="light"] {
        --green:      #2a4a1a;
        --dark-green: #3a5a2a;
        --dim-green:  #c8d8b8;
        --yellow:     #8a6a00;
        --red:        #8a1a00;
        --orange:     #8a4400;
        --blue:       #1a2a8a;
        --purple:     #5a1a6a;
        --cyan:       #1a5a6a;
        --bg:         #f0ede0;
        --panel:      #e4e0d0;
        --panel2:     #dedad0;
      }
      [data-theme="light"] body {
        background: #f0ede0;
        color: #2a4a1a;
      }
      [data-theme="light"] body::before {
        background: repeating-linear-gradient(
          0deg,
          rgba(0,0,0,0.03) 0px, rgba(0,0,0,0.03) 1px,
          transparent 1px, transparent 3px
        );
      }
      [data-theme="light"] .panel           { background: #e4e0d0; border-color: #3a5a2a; }
      [data-theme="light"] .panel-red       { border-color: #8a1a00; }
      [data-theme="light"] .panel-blue      { background: #d8daea; border-color: #1a2a8a; }
      [data-theme="light"] .panel-purple    { background: #e4d8ea; border-color: #5a1a6a; }
      [data-theme="light"] .panel-cyan      { background: #d8eae4; border-color: #1a5a6a; }
      [data-theme="light"] .panel-orange    { background: #eae0d0; border-color: #8a4400; }
      [data-theme="light"] .marquee-wrap    { border-color: #8a1a00; background: #ede8d8; }
      [data-theme="light"] .marquee-inner   { color: #8a1a00; }
      [data-theme="light"] .navbar          { background: #ede8d8; border-color: #3a5a2a; }
      [data-theme="light"] .navbar a        { color: #2a4a1a; border-color: #b0c8a0; }
      [data-theme="light"] .navbar a:hover,
      [data-theme="light"] .navbar a.active { background: #2a4a1a; color: #f0ede0; border-color: #2a4a1a; }
      [data-theme="light"] .navbar-title    { color: #8a6a00; border-color: #b0c8a0; }
      [data-theme="light"] .panel-title     { color: #8a6a00; border-color: #3a5a2a; }
      [data-theme="light"] .visitor-bar     { background: #dedad0; border-color: #1a2a8a; color: #1a2a8a; }
      [data-theme="light"] .page-header     { background: #e4e0d0; border-color: #2a4a1a; }
      [data-theme="light"] .site-footer     { border-color: #3a5a2a; }
      [data-theme="light"] .site-footer .footer-text { color: #3a5a2a; }
      [data-theme="light"] .prog-bar        { background: #c8c4b0; border-color: #a0a090; }
      [data-theme="light"] input[type=text],
      [data-theme="light"] input[type=email],
      [data-theme="light"] textarea,
      [data-theme="light"] select {
        background: #faf8f0;
        color: #2a4a1a;
        border-color: #3a5a2a;
      }
      [data-theme="light"] ::-webkit-scrollbar-track { background: #e4e0d0; }
      [data-theme="light"] ::-webkit-scrollbar-thumb { background: #3a5a2a; }
      [data-theme="light"] .blink { animation: blink 1s step-end infinite; }
    `;
    document.head.appendChild(style);
  }

  function injectToggleButton() {
    // Wait for navbar to exist
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    if (document.getElementById('theme-toggle-btn')) return;

    const btn = document.createElement('button');
    btn.id          = 'theme-toggle-btn';
    btn.textContent = '[ DAY MODE ]';
    btn.style.cssText = [
      'font-family:"Courier Prime",monospace',
      'font-size:13px',
      'font-weight:700',
      'background:transparent',
      'border:1px solid var(--dark-green)',
      'color:var(--green)',
      'padding:3px 8px',
      'cursor:pointer',
      'letter-spacing:1px',
      'margin-left:auto',
    ].join(';');
    btn.addEventListener('click', toggleTheme);
    navbar.appendChild(btn);

    // Inject sound toggle button too
    const sfxBtn = document.createElement('button');
    sfxBtn.id          = 'sfx-toggle-btn';
    sfxBtn.textContent = '[ SFX ON ]';
    sfxBtn.style.cssText = btn.style.cssText;
    sfxBtn.style.marginLeft = '4px';
    sfxBtn.addEventListener('click', () => {
      if (window.SFX) {
        const now = !SFX.isEnabled();
        SFX.setEnabled(now);
        sfxBtn.textContent = now ? '[ SFX ON ]' : '[ SFX OFF ]';
        if (now) SFX.blip();
      }
    });
    navbar.appendChild(sfxBtn);

    // Set correct label immediately
    const theme = localStorage.getItem(KEY_THEME) || 'dark';
    btn.textContent = theme === 'light' ? '[ CRT MODE ]' : '[ DAY MODE ]';
    if (window.SFX) {
      sfxBtn.textContent = SFX.isEnabled() ? '[ SFX ON ]' : '[ SFX OFF ]';
    }
  }

  // ── Hero name display in navbar ───────────────────────────────────────────

  function injectHeroName() {
    const name   = localStorage.getItem(KEY_NAME) || 'HERO';
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    if (document.getElementById('hero-name-display')) return;

    const span = document.createElement('span');
    span.id           = 'hero-name-display';
    span.style.cssText = [
      'font-family:"VT323",monospace',
      'font-size:16px',
      'color:var(--yellow)',
      'padding:3px 8px',
      'border:1px solid var(--dim-green)',
      'letter-spacing:1px',
      'cursor:pointer',
      'white-space:nowrap',
    ].join(';');
    span.textContent  = '[HERO: ' + name.toUpperCase() + ']';
    span.title        = 'Click to change hero name';
    span.addEventListener('click', () => {
      localStorage.removeItem(KEY_SETUP);
      showSetupScreen(true);
    });

    // Insert before the theme toggle
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) navbar.insertBefore(span, themeBtn);
    else navbar.appendChild(span);
  }

  // ── Setup modal ───────────────────────────────────────────────────────────

  function showSetupScreen(isRename) {
    if (window.SFX) SFX.alert();

    const existing = document.getElementById('hero-setup-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'hero-setup-overlay';
    overlay.style.cssText = [
      'position:fixed',
      'inset:0',
      'background:rgba(0,0,0,0.92)',
      'display:flex',
      'align-items:center',
      'justify-content:center',
      'z-index:99999',
      'font-family:"Courier Prime",monospace',
    ].join(';');

    const box = document.createElement('div');
    box.style.cssText = [
      'border:3px double #00ff00',
      'background:#001100',
      'padding:30px 36px',
      'max-width:480px',
      'width:90%',
      'text-align:center',
    ].join(';');

    const currentName = localStorage.getItem(KEY_NAME) || '';

    box.innerHTML = `
      <div style="font-family:'VT323',monospace;font-size:11px;color:#004400;line-height:1.1;margin-bottom:12px;white-space:pre">
 ██████╗██╗  ██╗ ██████╗ ███████╗███████╗███╗   ██╗
██╔════╝██║  ██║██╔═══██╗██╔════╝██╔════╝████╗  ██║
██║     ███████║██║   ██║███████╗█████╗  ██╔██╗ ██║
██║     ██╔══██║██║   ██║╚════██║██╔══╝  ██║╚██╗██║
╚██████╗██║  ██║╚██████╔╝███████║███████╗██║ ╚████║
 ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝</div>
      <div style="font-family:'VT323',monospace;font-size:22px;color:#00ff00;letter-spacing:3px;margin-bottom:6px">
        ${isRename ? 'CHANGE YOUR HERO NAME' : 'THE ANCIENT ALGORITHM HAS FOUND YOU'}
      </div>
      <div style="font-family:'VT323',monospace;font-size:16px;color:#446644;margin-bottom:20px;line-height:1.5">
        ${isRename
          ? 'Enter a new name. The Council will update its records.'
          : 'Before you begin your quest, the Council of Elders<br>requires your hero designation.'}
      </div>
      <input
        id="hero-name-input"
        type="text"
        maxlength="20"
        placeholder="Enter your hero name..."
        value="${currentName}"
        style="
          background:#000;
          color:#00ff00;
          border:2px solid #00aa00;
          font-family:'Courier Prime',monospace;
          font-size:18px;
          padding:8px 12px;
          width:100%;
          text-align:center;
          letter-spacing:2px;
          outline:none;
          margin-bottom:16px;
          text-transform:uppercase;
        "
      >
      <div id="hero-setup-error" style="font-family:'VT323',monospace;font-size:15px;color:#ff3300;min-height:18px;margin-bottom:10px"></div>
      <button id="hero-setup-confirm" style="
        font-family:'Courier Prime',monospace;
        font-size:15px;
        font-weight:700;
        background:#ffff00;
        color:#000;
        border:none;
        padding:10px 28px;
        cursor:pointer;
        letter-spacing:1px;
        margin-right:8px;
      ">[ CONFIRM IDENTITY ]</button>
      ${isRename ? `<button id="hero-setup-cancel" style="
        font-family:'Courier Prime',monospace;
        font-size:15px;
        font-weight:700;
        background:transparent;
        color:#00aa00;
        border:1px solid #00aa00;
        padding:10px 20px;
        cursor:pointer;
        letter-spacing:1px;
      ">[ CANCEL ]</button>` : ''}
      <div style="font-family:'VT323',monospace;font-size:13px;color:#333;margin-top:16px">
        Max 20 characters. No spaces. The Council is watching.
      </div>
    `;

    overlay.appendChild(box);
    document.body.appendChild(overlay);

    const input   = document.getElementById('hero-name-input');
    const confirm = document.getElementById('hero-setup-confirm');
    const cancel  = document.getElementById('hero-setup-cancel');
    const errEl   = document.getElementById('hero-setup-error');

    // Auto-select text
    setTimeout(() => { input.focus(); input.select(); }, 50);

    // Uppercase as you type
    input.addEventListener('input', () => {
      const pos = input.selectionStart;
      input.value = input.value.toUpperCase().replace(/[^A-Z0-9_\-]/g, '');
      input.setSelectionRange(pos, pos);
    });

    function submit() {
      const name = input.value.trim();
      if (!name || name.length < 2) {
        errEl.textContent = '>>> NAME MUST BE AT LEAST 2 CHARACTERS.';
        if (window.SFX) SFX.bloop();
        return;
      }
      localStorage.setItem(KEY_NAME, name);
      localStorage.setItem(KEY_SETUP, '1');
      overlay.remove();
      if (window.SFX) SFX.missionComplete();
      // Update navbar display
      const display = document.getElementById('hero-name-display');
      if (display) display.textContent = '[HERO: ' + name + ']';
      // Update api.js hero name if API is loaded
      if (window.API) API.setHeroName(name);
    }

    confirm.addEventListener('click', submit);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') submit(); });
    if (cancel) cancel.addEventListener('click', () => {
      localStorage.setItem(KEY_SETUP, '1');
      overlay.remove();
    });
  }

  // ── Boot sequence ─────────────────────────────────────────────────────────

  function boot() {
    injectThemeStyles();

    // Apply saved theme immediately (before paint)
    const savedTheme = localStorage.getItem(KEY_THEME) || 'dark';
    applyTheme(savedTheme);

    // Wait for DOM then inject UI chrome
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', afterDOM);
    } else {
      afterDOM();
    }
  }

  function afterDOM() {
    injectToggleButton();
    injectHeroName();

    // Play modem sound on load
    if (window.SFX) {
      // Small delay so AudioContext can be created after user gesture (some browsers)
      // We trigger on first click if autoplay is blocked
      const tryModem = () => {
        SFX.modemConnect();
        document.removeEventListener('click', tryModem);
      };
      // Try immediately; if blocked, it plays on first interaction
      try { SFX.modemConnect(); } catch(e) { document.addEventListener('click', tryModem, { once: true }); }
    }

    // Show setup screen if first visit
    const setupDone = localStorage.getItem(KEY_SETUP);
    if (!setupDone) {
      // Short delay so page renders first
      setTimeout(() => showSetupScreen(false), 600);
    }
  }

  boot();

})();
