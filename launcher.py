"""
chosen-one-y2k Launcher
=======================
Double-click to run. This launcher:
  1. Checks Python dependencies are installed
  2. Starts the Flask backend on port 5000
  3. Opens the frontend in your default browser
  4. Keeps running until you close the window or press Ctrl+C

Works on Windows, macOS and Linux.
"""

import sys
import os
import time
import subprocess
import webbrowser
import threading
import socket

# ── Resolve paths relative to the exe / script ───────────────────────────
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BACKEND_DIR   = os.path.join(BASE_DIR, 'backend')
FRONTEND_PAGE = os.path.join(BASE_DIR, 'frontend', 'pages', 'index.html')
APP_PY        = os.path.join(BACKEND_DIR, 'app.py')
REQ_TXT       = os.path.join(BACKEND_DIR, 'requirements.txt')
PORT          = 5000

# ── ANSI colours (work on Windows 10+ terminal) ───────────────────────────
RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

def p(msg, colour=RESET):
    print(colour + msg + RESET, flush=True)

def banner():
    print()
    p('  ██████╗██╗  ██╗ ██████╗ ███████╗███████╗███╗   ██╗', CYAN)
    p(' ██╔════╝██║  ██║██╔═══██╗██╔════╝██╔════╝████╗  ██║', CYAN)
    p(' ██║     ███████║██║   ██║███████╗█████╗  ██╔██╗ ██║', CYAN)
    p(' ██║     ██╔══██║██║   ██║╚════██║██╔══╝  ██║╚██╗██║', CYAN)
    p(' ╚██████╗██║  ██║╚██████╔╝███████║███████╗██║ ╚████║', CYAN)
    p('  ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝', CYAN)
    p('  ONE-Y2K  ::  GAME LAUNCHER  ::  v1.6.0', YELLOW)
    print()

# ── Dependency check ──────────────────────────────────────────────────────
def check_and_install_deps():
    p('  [1/3] Checking Python dependencies...', YELLOW)
    try:
        import flask
        import flask_cors
        p('        flask and flask-cors: OK', GREEN)
        return True
    except ImportError:
        p('        Missing dependencies — installing...', YELLOW)

    if not os.path.exists(REQ_TXT):
        p(f'        requirements.txt not found at {REQ_TXT}', RED)
        p('        Make sure the launcher is in the chosen-one-y2k folder.', RED)
        return False

    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-r', REQ_TXT, '--quiet'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        p('        Installed successfully.', GREEN)
        return True
    else:
        # Try with --break-system-packages for Linux
        result2 = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', REQ_TXT,
             '--quiet', '--break-system-packages'],
            capture_output=True, text=True
        )
        if result2.returncode == 0:
            p('        Installed successfully.', GREEN)
            return True
        p('        Failed to install dependencies:', RED)
        p('        ' + (result.stderr or result2.stderr)[:200], RED)
        return False

# ── Port check ────────────────────────────────────────────────────────────
def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def wait_for_backend(port, timeout=12):
    """Poll until backend is accepting connections."""
    start = time.time()
    while time.time() - start < timeout:
        if not is_port_free(port):
            return True
        time.sleep(0.3)
    return False

# ── Start backend ─────────────────────────────────────────────────────────
backend_proc = None

def start_backend():
    global backend_proc

    p('  [2/3] Starting Flask backend...', YELLOW)

    if not os.path.exists(APP_PY):
        p(f'        app.py not found at {APP_PY}', RED)
        p('        Make sure the launcher is in the chosen-one-y2k folder.', RED)
        return False

    if not is_port_free(PORT):
        p(f'        Port {PORT} already in use — backend may already be running.', YELLOW)
        return True

    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'

    backend_proc = subprocess.Popen(
        [sys.executable, APP_PY],
        cwd=BACKEND_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    p(f'        Waiting for backend on port {PORT}...', YELLOW)
    if wait_for_backend(PORT):
        p(f'        Backend running at http://localhost:{PORT}', GREEN)
        return True
    else:
        p('        Backend failed to start in time.', RED)
        if backend_proc.poll() is not None:
            _, err = backend_proc.communicate()
            p('        Error: ' + err[:300], RED)
        return False

# ── Open browser ──────────────────────────────────────────────────────────
def open_browser():
    p('  [3/3] Opening game in browser...', YELLOW)

    # Try to open via local file if frontend exists
    if os.path.exists(FRONTEND_PAGE):
        file_url = 'file:///' + FRONTEND_PAGE.replace('\\', '/')
        # Give browser a moment after backend is up
        time.sleep(0.5)
        webbrowser.open(file_url)
        p('        Opened: ' + file_url, GREEN)
    else:
        webbrowser.open(f'http://localhost:{PORT}')
        p(f'        Opened: http://localhost:{PORT}', GREEN)

# ── Shutdown hook ─────────────────────────────────────────────────────────
def shutdown():
    global backend_proc
    if backend_proc and backend_proc.poll() is None:
        p('\n  Shutting down backend...', YELLOW)
        backend_proc.terminate()
        try:
            backend_proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            backend_proc.kill()
        p('  Backend stopped.', GREEN)

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    # Enable ANSI on Windows
    if sys.platform == 'win32':
        os.system('color')

    banner()

    p('  chosen-one-y2k Game Launcher', BOLD)
    p('  Press Ctrl+C at any time to stop the server and exit.', YELLOW)
    print()

    # Step 1: Dependencies
    if not check_and_install_deps():
        p('\n  Cannot start without dependencies. Exiting.', RED)
        input('\n  Press Enter to close...')
        sys.exit(1)

    # Step 2: Backend
    if not start_backend():
        p('\n  Backend failed. The game will open without backend features.', YELLOW)
        p('  Guestbook, chat and missions will not save.', YELLOW)
        open_browser()
    else:
        # Step 3: Browser
        threading.Thread(target=open_browser, daemon=True).start()

    print()
    p('  ═══════════════════════════════════════════════════', CYAN)
    p('  CHOSEN-ONE-Y2K IS RUNNING', GREEN)
    p(f'  Backend API : http://localhost:{PORT}/api', CYAN)
    p('  Frontend    : open frontend/pages/index.html', CYAN)
    p('  Stop server : Ctrl+C or close this window', YELLOW)
    p('  ═══════════════════════════════════════════════════', CYAN)
    print()

    try:
        # Stream backend output so errors are visible
        if backend_proc:
            for line in backend_proc.stdout:
                if line.strip():
                    p('  [backend] ' + line.rstrip(), RESET)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()

    p('\n  Game stopped. Goodbye, Chosen One.', CYAN)
    print()
    if sys.platform == 'win32':
        input('  Press Enter to close this window...')

if __name__ == '__main__':
    main()
