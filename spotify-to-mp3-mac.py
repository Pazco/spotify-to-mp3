#!/usr/bin/env python3
"""
Music downloader bot from CSV.
Requirements:
    sudo dnf install yt-dlp ffmpeg nodejs
"""

import sys, os, csv, time, json, shutil, subprocess, re, urllib.parse

# ═══════════════════════════════════════════════════════
#  CONFIGURACION POR DEFECTO
# ═══════════════════════════════════════════════════════
CARPETA_SALIDA     = os.path.join(os.path.expanduser("~"), "Music", "spotify-to-mp3")
CSV_FILE           = "songs.csv"
COOKIES_NAVEGADOR  = "auto"    # auto | brave | firefox | chrome | chromium | edge
ESPERA_ENTRE_SONGS = 1
TIMEOUT_SONG       = 300
CONFIG_FILE        = ".config.json"
# ═══════════════════════════════════════════════════════

VERDE    = "\033[92m"
ROJO     = "\033[91m"
AMARILLO = "\033[93m"
CYAN     = "\033[96m"
GRIS     = "\033[90m"
AZUL     = "\033[94m"
RESET    = "\033[0m"
NEGRITA  = "\033[1m"


def detect_browser():
    """Auto-detect which browser is installed and has cookies available."""
    import shutil
    # On macOS, check both PATH and common app locations
    mac_paths = {
        "chrome":   [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ],
        "brave":    [
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            os.path.expanduser("~/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        ],
        "firefox":  [
            "/Applications/Firefox.app/Contents/MacOS/firefox",
            os.path.expanduser("~/Applications/Firefox.app/Contents/MacOS/firefox"),
        ],
        "chromium": [
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ],
        "edge":     [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ],
    }
    # Check app paths first
    for name, paths in mac_paths.items():
        if any(os.path.isfile(p) for p in paths):
            return name
    # Fallback to PATH
    candidates = [
        ("brave",    ["brave-browser", "brave"]),
        ("firefox",  ["firefox"]),
        ("chrome",   ["google-chrome", "google-chrome-stable", "chrome"]),
        ("chromium", ["chromium-browser", "chromium"]),
        ("edge",     ["microsoft-edge", "microsoft-edge-stable"]),
    ]
    for name, bins in candidates:
        if any(shutil.which(b) for b in bins):
            return name
    return None

def p(color, texto): print(f"{color}{texto}{RESET}")

def browse_file(title="Select file"):
    """Open file browser dialog using osascript (macOS native)."""
    try:
        script = f'''
        tell application "System Events"
            set theFile to choose file with prompt "{title}" of type {{"csv", "CSV"}}
            return POSIX path of theFile
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script],
                                capture_output=True, text=True)
        path = result.stdout.strip()
        return path if path else None
    except Exception:
        pass
    return None

def browse_folder(title="Select folder"):
    """Open folder browser dialog using osascript (macOS native)."""
    try:
        script = f'''
        tell application "System Events"
            set theFolder to choose folder with prompt "{title}"
            return POSIX path of theFolder
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script],
                                capture_output=True, text=True)
        path = result.stdout.strip()
        return path if path else None
    except Exception:
        pass
    return None


def sep(): print(f"{GRIS}{'─'*54}{RESET}")
def limpiar(): os.system("clear")


# ═══════════════════════════════════════════════════════
#  EXPORTAR CSV AUTOMATICAMENTE DESDE EXPORTIFY
#  (comentado — descomenta si quieres usarlo en el futuro)
# ═══════════════════════════════════════════════════════

# BRAVE_PROFILE = os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default")
# BRAVE_BIN_CANDIDATOS = [
#     "/usr/bin/brave-browser",
#     "/usr/bin/brave",
#     "/usr/bin/brave-browser-stable",
#     "/opt/brave.com/brave/brave-browser",
# ]
#
# def exportar_csv(ruta_csv):
#     from playwright.sync_api import sync_playwright
#     brave_exe = next((c for c in BRAVE_BIN_CANDIDATOS if os.path.isfile(c)), None)
#     if not brave_exe:
#         brave_exe = shutil.which("brave-browser") or shutil.which("brave")
#     if not brave_exe:
#         p(ROJO, "  Brave browser not found.")
#         return False
#     with sync_playwright() as pw:
#         context = pw.chromium.launch_persistent_context(
#             BRAVE_PROFILE, headless=False, executable_path=brave_exe,
#             args=["--no-sandbox","--no-first-run","--no-default-browser-check"],
#             accept_downloads=True, ignore_default_args=["--enable-automation"],
#         )
#         page = context.new_page()
#         page.goto("https://exportify.app/", wait_until="networkidle", timeout=30000)
#         page.wait_for_timeout(2000)
#         if page.query_selector("button:has-text('Comenzar'), button:has-text('Get Started')"):
#             p(AMARILLO, "  Click Get Started and log in to Spotify. The script will continue automatically.")
#         try:
#             page.wait_for_selector("table tbody tr", timeout=180000)
#         except Exception:
#             page.screenshot(path="exportify_debug.png"); context.close(); return False
#         page.wait_for_timeout(1500)
#         liked_row = None
#         for txt in ["Liked Songs", "Canciones que te gustan"]:
#             row = page.locator("tr", has_text=txt).first
#             if row.count() > 0:
#                 liked_row = row; break
#         if not liked_row:
#             page.screenshot(path="exportify_debug.png"); context.close(); return False
#         export_btn = liked_row.locator("button", has_text="Export").first
#         if export_btn.count() == 0:
#             export_btn = liked_row.locator("button").last
#         with page.expect_download(timeout=120000) as dl_info:
#             export_btn.click()
#         dl_info.value.save_as(ruta_csv)
#         context.close()
#         return True


# ═══════════════════════════════════════════════════════
#  CONFIGURACION PERSISTENTE
# ═══════════════════════════════════════════════════════

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"folder": CARPETA_SALIDA, "csv": CSV_FILE}

def guardar_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════
#  DEPENDENCIAS
# ═══════════════════════════════════════════════════════

def verificar_deps():
    errores = []
    if not shutil.which("yt-dlp"):
        errores.append(("yt-dlp",  "sudo dnf install yt-dlp"))
    if not shutil.which("ffmpeg"):
        errores.append(("ffmpeg",  "sudo dnf install ffmpeg"))
    if errores:
        p(ROJO, "\n  Missing dependencies:")
        for tool, cmd in errores:
            p(AMARILLO, f"    {tool:8} ->  {cmd}")
        return False
    return True


# ═══════════════════════════════════════════════════════
#  LEER CSV
# ═══════════════════════════════════════════════════════

def norm_col(c):
    return c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")

def leer_csv(ruta_csv):
    songs = []
    COL_NOMBRE  = ("track_name", "nombre", "name", "cancion", "title", "song")
    COL_ARTISTA = ("artist_names", "artist_name_s", "artista", "artist", "artists")

    def get_col(d, opts):
        for k in opts:
            if k in d and d[k]:
                return d[k].strip()
        return ""

    with open(ruta_csv, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(4096); f.seek(0)
        try:
            tiene_cab = csv.Sniffer().has_header(muestra)
        except csv.Error:
            tiene_cab = False

        reader   = csv.reader(f)
        cabecera = None
        if tiene_cab:
            cabecera = [norm_col(c) for c in next(reader)]

        for fila in reader:
            if not fila or all(c.strip() == "" for c in fila):
                continue
            fila = [c.strip() for c in fila]
            if cabecera:
                row     = dict(zip(cabecera, fila))
                nombre  = get_col(row, COL_NOMBRE) or fila[0]
                artista = get_col(row, COL_ARTISTA)
                if artista and "," in artista:
                    artista = artista.split(",")[0].strip()
            else:
                nombre  = fila[0]
                artista = fila[1] if len(fila) > 1 else ""

            if re.match(r"^spotify:(track|album|artist):", nombre):
                continue
            if nombre:
                songs.append((nombre, artista))

    return songs


# ═══════════════════════════════════════════════════════
#  REGISTRO
# ═══════════════════════════════════════════════════════

def clave(nombre, artista):
    return f"{artista.lower().strip()}|||{nombre.lower().strip()}"

def cargar_registro(ruta):
    if os.path.exists(ruta):
        try:
            with open(ruta, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_registro(registro, ruta):
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════
#  DESCARGAR CON YT-DLP
# ═══════════════════════════════════════════════════════

def descargar(nombre, artista, folder, cookies=None):
    query     = f"{artista} - {nombre}" if artista else nombre
    safe_name = re.sub(r'[\\/*?:"<>|]', "", query)
    output = os.path.join(folder, f"{safe_name}.%(ext)s")

    cookies_args = []
    if cookies:
        if os.path.isfile(str(cookies)):
            cookies_args = ["--cookies", cookies]
        else:
            cookies_args = ["--cookies-from-browser", cookies]

    # Intentar varias fuentes en orden
    fuentes = [
        f"ytsearch3:{query}",           # YouTube
        f"ytsearch3:{query} audio",     # YouTube (variante)
        f"scsearch1:{query}",           # SoundCloud
        f"ytsearch3:{query} lyrics",    # YouTube (otro resultado)
    ]

    for fuente in fuentes:
        cmd = [
            "yt-dlp",
            fuente,
            "--format", "bestaudio/best",
            "--match-filter", "!is_live",
            "-x",
            "--audio-format",   "mp3",
            "--audio-quality",  "0",
            "--add-metadata",
            "--embed-thumbnail",
            "--no-playlist",
            "--output", output,
            "--no-overwrites",
            "--socket-timeout", "30",
            "--retries",        "2",
            "--no-warnings",
        ] + cookies_args

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SONG)

            if result.returncode == 0:
                return True, "OK"

            err = (result.stderr or result.stdout).strip()

            if any(e in err for e in [
                "Requested format is not available",
                "Only images are available",
                "Signature solving failed",
                "No video formats found",
                "Unable to extract",
                "No results",
                "HTTP Error 404",
                "HTTP Error 403",
                "Unable to download JSON metadata",
                "Did not get any data blocks",
            ]):
                continue

            lines = [l for l in err.splitlines() if "ERROR" in l]
            return False, (lines[-1].strip() if lines else err[-150:])

        except subprocess.TimeoutExpired:
            return False, f"Timeout ({TIMEOUT_SONG}s)"
        except Exception as e:
            return False, str(e)[:120]

    return False, "Blocked or unavailable on YouTube"


# ═══════════════════════════════════════════════════════
#  PROCESO DE DESCARGA
# ═══════════════════════════════════════════════════════

def iniciar_descarga(config):
    limpiar()
    print(f"\n{NEGRITA}{'='*54}")
    print(f"  Starting download")
    print(f"{'='*54}{RESET}\n")

    ruta_csv       = config["csv"]
    download_folder = os.path.expanduser(config["folder"])
    script_dir     = os.path.dirname(os.path.abspath(__file__))
    registro_file  = os.path.join(script_dir, ".registry.json")
    if COOKIES_NAVEGADOR == "auto":
        cookies = detect_browser()
        if not cookies:
            p(AMARILLO, "  No browser found for cookies — downloads may be blocked by YouTube.")
            p(AMARILLO, "  Set COOKIES_NAVEGADOR in the script to your browser name.")
            cookies = None
        else:
            p(VERDE, f"  Auto-detected browser: {cookies}")
    else:
        cookies = COOKIES_NAVEGADOR

    # Verificar CSV
    if not os.path.exists(ruta_csv):
        p(ROJO, f"  CSV file not found: {ruta_csv}")
        p(AMARILLO, "  Go to the menu and set the CSV path.")
        input(f"\n  {GRIS}Press Enter to go back...{RESET}")
        return

    # Verificar dependencias
    p(CYAN, "  Checking dependencies...")
    if not verificar_deps():
        input(f"\n  {GRIS}Press Enter to go back...{RESET}")
        return
    p(VERDE, "  yt-dlp + ffmpeg ready")
    sep()

    # Leer CSV
    p(CYAN, "  Reading CSV...")
    try:
        songs = leer_csv(ruta_csv)
    except Exception as e:
        p(ROJO, f"  Error leyendo CSV: {e}")
        input(f"\n  {GRIS}Press Enter to go back...{RESET}")
        return

    if not songs:
        p(ROJO, "  CSV is empty.")
        input(f"\n  {GRIS}Press Enter to go back...{RESET}")
        return

    p(VERDE, f"  {len(songs)} songs in the CSV")
    sep()

    # Comparar con registro
    registro   = cargar_registro(registro_file)
    new_songs  = [(n, a) for n, a in songs if clave(n, a) not in registro]
    already    = len(songs) - len(new_songs)

    p(VERDE, f"  Already downloaded: {already} (skipped)")
    p(CYAN,  f"  New to download   : {len(new_songs)}")

    if not new_songs:
        p(VERDE, "\n  All up to date, no new songs.")
        input(f"\n  {GRIS}Press Enter to go back to menu...{RESET}")
        return

    os.makedirs(download_folder, exist_ok=True)
    p(CYAN, f"  Destination: {os.path.abspath(download_folder)}\n")
    sep()
    print()

    # Descargar
    ok_list, failures = [], []

    for i, (nombre, artista) in enumerate(new_songs, 1):
        texto   = f"{artista} - {nombre}" if artista else nombre
        display = (texto[:55] + "...") if len(texto) > 55 else texto
        print(f"  [{i:>4}/{len(new_songs)}] {display}", end=" ", flush=True)

        if clave(nombre, artista) in registro:
            p(GRIS, "already exists")
            continue

        exito, msg = descargar(nombre, artista, download_folder, cookies)

        if exito:
            p(VERDE, "OK")
            ok_list.append(texto)
            registro[clave(nombre, artista)] = {
                "nombre":  nombre,
                "artista": artista,
                "fecha":   time.strftime("%Y-%m-%d %H:%M"),
            }
            guardar_registro(registro, registro_file)
        else:
            p(ROJO, "FAILED")
            print(f"         {GRIS}{msg}{RESET}")
            failures.append((texto, msg))

        if i < len(new_songs):
            time.sleep(ESPERA_ENTRE_SONGS)

    # Resumen
    sep()
    print(f"\n{NEGRITA}{'='*54}{RESET}")
    p(NEGRITA + VERDE, f"  Downloaded this session: {len(ok_list)}")
    p(VERDE,           f"  Already had          : {already}")
    p(VERDE,           f"  Total in library     : {len(registro)}")

    if failures:
        p(ROJO, f"  Failures             : {len(failures)}")
        script_dir2  = os.path.dirname(os.path.abspath(__file__))
        failures_csv = os.path.join(script_dir2, ".failures.csv")
        write_header = not os.path.exists(failures_csv)
        with open(failures_csv, "a", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            if write_header:
                writer.writerow(["#", "Song", "Error", "Date"])
            with open(failures_csv, "r", encoding="utf-8") as fr:
                start_idx = max(0, sum(1 for _ in fr) - 1)
            for j, (nom, mot) in enumerate(failures, start_idx + 1):
                writer.writerow([j, nom, mot.strip(), time.strftime("%Y-%m-%d %H:%M")])
        p(AMARILLO, f"\n  Failures saved -> {failures_csv}")

    print(f"{'='*54}\n")
    input(f"  {GRIS}Press Enter to go back to menu...{RESET}")



# ═══════════════════════════════════════════════════════
#  CHECK DUPLICATES
# ═══════════════════════════════════════════════════════

def check_duplicates(config):
    import unicodedata, curses

    def normalize(name):
        name = os.path.splitext(name)[0].lower()
        name = unicodedata.normalize("NFKD", name)
        name = re.sub(r" *- *copia *(\(\d+\))?$", "", name, flags=re.IGNORECASE)
        name = re.sub(r" *- *copy *(\(\d+\))?$", "", name, flags=re.IGNORECASE)
        name = re.sub(r" *\(\d+\)$", "", name)
        name = re.sub(r" *_\d+$", "", name)
        name = re.sub(r" *\[\d+\]$", "", name)
        name = re.sub(r"[^a-z0-9]", "", name)
        return name

    def similarity(a, b):
        """Return similarity ratio between 0 and 1 using SequenceMatcher."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()

    SIMILARITY_THRESHOLD = 0.85  # 85% similar = possible duplicate

    def get_mtime(folder, fname):
        try:
            return os.path.getmtime(os.path.join(folder, fname))
        except Exception:
            return 0

    def delete_files(files, folder):
        deleted = 0
        for f in files:
            try:
                os.remove(os.path.join(folder, f))
                p(VERDE, f"  Deleted: {f}")
                deleted += 1
            except Exception as e:
                p(ROJO, f"  Could not delete {f}: {e}")
        return deleted

    def duplicates_selector(groups, folder):
        """
        curses UI for selecting which files to delete per group.
        Each group shows all files sorted by mtime.
        Keys: UP/DOWN navigate, SPACE toggle, N select all newest,
              O select all oldest, A select all (keep one), ENTER confirm, Q cancel.
        """
        # Flatten into rows with group info
        # rows: list of {group_idx, file, mtime, marked}
        rows = []
        for gi, group in enumerate(groups):
            # Sort group by mtime oldest first
            sorted_files = sorted(group, key=lambda f: get_mtime(folder, f))
            for fi, fname in enumerate(sorted_files):
                mtime = get_mtime(folder, fname)
                rows.append({
                    "group":    gi,
                    "file":     fname,
                    "mtime":    mtime,
                    "is_oldest": fi == 0,
                    "is_newest": fi == len(sorted_files) - 1,
                    "marked":   False,
                    "all_in_group": sorted_files,
                })

        def _draw(stdscr, cur, rows, scroll):
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            curses.curs_set(0)
            curses.init_pair(1, curses.COLOR_GREEN,  curses.COLOR_BLACK)  # marked
            curses.init_pair(2, curses.COLOR_CYAN,   curses.COLOR_BLACK)  # header
            curses.init_pair(3, curses.COLOR_WHITE,  curses.COLOR_GREEN)  # selected
            curses.init_pair(4, curses.COLOR_WHITE,  curses.COLOR_BLACK)  # normal
            curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # info
            curses.init_pair(6, curses.COLOR_RED,    curses.COLOR_BLACK)  # marked+selected

            # Header
            stdscr.addstr(0, 0, "  Select files to DELETE (originals will be kept)", curses.color_pair(2) | curses.A_BOLD)

            row_y = 2
            prev_group = -1
            visible_rows = []

            for i, row in enumerate(rows):
                # Group separator
                if row["group"] != prev_group:
                    visible_rows.append(("sep", row["group"]))
                    prev_group = row["group"]
                visible_rows.append(("file", i))

            # Scrolling
            display = visible_rows[scroll:]
            for item in display:
                if row_y >= h - 2:
                    break
                if item[0] == "sep":
                    gi = item[1]
                    label = f"  ── Group {gi+1} " + "─" * max(0, w - 16)
                    try:
                        stdscr.addstr(row_y, 0, label[:w-1], curses.color_pair(5))
                    except Exception:
                        pass
                    row_y += 1
                else:
                    i = item[1]
                    row = rows[i]
                    mark   = "●" if row["marked"] else "○"
                    age    = "oldest" if row["is_oldest"] else "newest" if row["is_newest"] else "      "
                    mtime  = time.strftime("%Y-%m-%d %H:%M", time.localtime(row["mtime"]))
                    fname  = row["file"]
                    max_fname = max(10, w - 35)
                    fname_short = fname[:max_fname] + "…" if len(fname) > max_fname else fname

                    line = f"  {mark} [{age}] {mtime}  {fname_short}"

                    if i == cur and row["marked"]:
                        attr = curses.color_pair(6) | curses.A_BOLD
                    elif i == cur:
                        attr = curses.color_pair(3) | curses.A_BOLD
                    elif row["marked"]:
                        attr = curses.color_pair(1)
                    else:
                        attr = curses.color_pair(4)
                    try:
                        stdscr.addstr(row_y, 0, line[:w-1], attr)
                    except Exception:
                        pass
                    row_y += 1

            # Footer
            marked_count = sum(1 for r in rows if r["marked"])
            footer = f"  SPACE:toggle  N:newest  O:oldest  A:all-but-oldest  ENTER:confirm({marked_count} selected)  Q:cancel"
            try:
                stdscr.addstr(h-1, 0, footer[:w-1], curses.color_pair(5))
            except Exception:
                pass
            stdscr.refresh()

        def _run(stdscr):
            cur    = 0
            scroll = 0

            while True:
                h, w = stdscr.getmaxyx()

                # Build visible list: separators + file rows
                prev_group = -1
                visible = []  # list of ("sep", group_idx) or ("file", row_idx)
                for i, row in enumerate(rows):
                    if row["group"] != prev_group:
                        visible.append(("sep", row["group"]))
                        prev_group = row["group"]
                    visible.append(("file", i))

                # Map cur (file index) to visible index
                cur_vis = next(
                    (vi for vi, item in enumerate(visible)
                     if item[0] == "file" and item[1] == cur),
                    0
                )

                # Scroll so that cur_vis is always visible
                # Header takes 2 rows, footer takes 1 row, leave margin of 1
                visible_area = h - 4
                if cur_vis < scroll:
                    scroll = cur_vis
                elif cur_vis >= scroll + visible_area:
                    scroll = cur_vis - visible_area + 1

                _draw(stdscr, cur, rows, scroll)
                key = stdscr.getch()

                if key == curses.KEY_DOWN:
                    cur = min(cur + 1, len(rows) - 1)
                elif key == curses.KEY_UP:
                    cur = max(cur - 1, 0)
                elif key == ord(" "):
                    rows[cur]["marked"] = not rows[cur]["marked"]
                elif key in (ord("n"), ord("N")):
                    for r in rows:
                        r["marked"] = r["is_newest"]
                elif key in (ord("o"), ord("O")):
                    for r in rows:
                        r["marked"] = r["is_oldest"]
                elif key in (ord("a"), ord("A")):
                    for r in rows:
                        r["marked"] = not r["is_oldest"]
                elif key in (curses.KEY_ENTER, 10, 13):
                    return [r["file"] for r in rows if r["marked"]]
                elif key in (ord("q"), ord("Q")):
                    return []

        try:
            return curses.wrapper(_run)
        except Exception:
            # Fallback if curses fails
            print()
            for i, r in enumerate(rows):
                mark = "●" if r["marked"] else "○"
                print(f"  [{i+1}] {mark} {r['file']}")
            sel = input("  Enter numbers to delete (space separated): ").split()
            return [rows[int(x)-1]["file"] for x in sel if x.isdigit() and 1 <= int(x) <= len(rows)]

    while True:
        limpiar()
        print(f"\n{NEGRITA}{'='*54}")
        print(f"  Check for duplicates")
        print(f"{'='*54}{RESET}\n")

        download_folder = os.path.expanduser(config["folder"])

        if not os.path.exists(download_folder):
            p(ROJO, f"  Folder not found: {download_folder}")
            input(f"\n  {GRIS}Press Enter to go back...{RESET}")
            return

        p(CYAN, f"  Scanning: {os.path.abspath(download_folder)}\n")
        mp3_files = [f for f in os.listdir(download_folder) if f.lower().endswith(".mp3")]

        if not mp3_files:
            p(AMARILLO, "  No MP3 files found.")
            input(f"\n  {GRIS}Press Enter to go back...{RESET}")
            return

        # ── Exact duplicates ──────────────────────────────
        seen   = {}
        groups = []

        for f in sorted(mp3_files):
            key = normalize(f)
            if key in seen:
                added = False
                for g in groups:
                    if normalize(g[0]) == key:
                        g.append(f)
                        added = True
                        break
                if not added:
                    groups.append([seen[key], f])
            else:
                seen[key] = f

        # ── Similar files (fuzzy) ──────────────────────────
        keys      = [(f, normalize(f)) for f in mp3_files]
        similar_groups = []
        used      = set()

        for i, (fa, ka) in enumerate(keys):
            if fa in used:
                continue
            grp = [fa]
            for j, (fb, kb) in enumerate(keys):
                if i == j or fb in used:
                    continue
                # Skip if already an exact duplicate
                if ka == kb:
                    continue
                if similarity(ka, kb) >= SIMILARITY_THRESHOLD:
                    grp.append(fb)
            if len(grp) > 1:
                for f in grp:
                    used.add(f)
                similar_groups.append(grp)

        total_dups    = sum(len(g) - 1 for g in groups)
        total_similar = sum(len(g) - 1 for g in similar_groups)

        if not groups and not similar_groups:
            p(VERDE, "  No duplicates found!")
            input(f"\n  {GRIS}Press Enter to go back...{RESET}")
            return

        summary = []
        if groups:
            summary.append(f"{len(groups)} exact group(s) — {total_dups} duplicate(s)")
        if similar_groups:
            summary.append(f"{len(similar_groups)} similar group(s) — {total_similar} possible duplicate(s)")
        p(AMARILLO, "  " + "  |  ".join(summary))
        sep()

        action_opts = [
            "Exact duplicates — select to delete",
            "Exact duplicates — delete all newest",
            "Exact duplicates — delete all oldest",
            "Similar files — review and select",
            "Back to menu",
        ]
        if not groups:
            action_opts = [o for o in action_opts if "Exact" not in o]
        if not similar_groups:
            action_opts = [o for o in action_opts if "Similar" not in o]

        action_idx_map = {label: label for label in action_opts}
        action_idx = selector(action_opts,
                              titulo="Duplicates found",
                              subtitulo="  |  ".join(summary))
        chosen = action_opts[action_idx]

        if "Back" in chosen:
            return

        elif "delete all newest" in chosen.lower():
            to_delete = []
            for g in groups:
                sorted_g = sorted(g, key=lambda f: get_mtime(download_folder, f))
                to_delete.extend(sorted_g[1:])
            limpiar()
            deleted = delete_files(to_delete, download_folder)
            p(VERDE, f"\n  {deleted} file(s) deleted.")
            input(f"\n  {GRIS}Press Enter to continue...{RESET}")

        elif "delete all oldest" in chosen.lower():
            to_delete = []
            for g in groups:
                sorted_g = sorted(g, key=lambda f: get_mtime(download_folder, f))
                to_delete.append(sorted_g[0])
            limpiar()
            deleted = delete_files(to_delete, download_folder)
            p(VERDE, f"\n  {deleted} file(s) deleted.")
            input(f"\n  {GRIS}Press Enter to continue...{RESET}")

        elif "exact duplicates — select" in chosen.lower():
            to_delete = duplicates_selector(groups, download_folder)
            limpiar()
            if to_delete:
                deleted = delete_files(to_delete, download_folder)
                p(VERDE, f"\n  {deleted} file(s) deleted.")
            else:
                p(GRIS, "  Nothing deleted.")
            input(f"\n  {GRIS}Press Enter to continue...{RESET}")

        elif "similar" in chosen.lower():
            to_delete = duplicates_selector(similar_groups, download_folder)
            limpiar()
            if to_delete:
                deleted = delete_files(to_delete, download_folder)
                p(VERDE, f"\n  {deleted} file(s) deleted.")
            else:
                p(GRIS, "  Nothing deleted.")
            input(f"\n  {GRIS}Press Enter to continue...{RESET}")
# ═══════════════════════════════════════════════════════
#  RETRY FAILURES
# ═══════════════════════════════════════════════════════

def retry_failures(config):
    limpiar()
    print(f"\n{NEGRITA}{'='*54}")
    print(f"  Retry failed songs")
    print(f"{'='*54}{RESET}\n")

    script_dir    = os.path.dirname(os.path.abspath(__file__))
    failures_csv  = os.path.join(script_dir, ".failures.csv")
    registry_file = os.path.join(script_dir, ".registry.json")
    download_folder = os.path.expanduser(config["folder"])

    if not os.path.exists(failures_csv):
        p(AMARILLO, "  No failures file found.")
        p(GRIS,     f"  Expected at: {failures_csv}")
        input(f"\n  {GRIS}Press Enter to go back...{RESET}")
        return

    failed_songs = []
    with open(failures_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                song = row[1].strip()
                if " - " in song:
                    parts = song.split(" - ", 1)
                    failed_songs.append((parts[1].strip(), parts[0].strip()))
                else:
                    failed_songs.append((song, ""))

    if not failed_songs:
        p(AMARILLO, "  No failed songs found.")
        input(f"\n  {GRIS}Press Enter to go back...{RESET}")
        return

    p(CYAN,  f"  {len(failed_songs)} failed song(s) found")
    p(GRIS,  f"  From: {failures_csv}\n")
    sep()

    cookies = COOKIES_NAVEGADOR
    if cookies == "auto":
        cookies = detect_browser()

    os.makedirs(download_folder, exist_ok=True)
    registro  = cargar_registro(registry_file)
    ok_list   = []
    still_failing = []

    for i, (nombre, artista) in enumerate(failed_songs, 1):
        texto   = f"{artista} - {nombre}" if artista else nombre
        display = (texto[:55] + "...") if len(texto) > 55 else texto
        print(f"  [{i:>3}/{len(failed_songs)}] {display}", end=" ", flush=True)

        exito, msg = descargar(nombre, artista, download_folder, cookies)

        if exito:
            p(VERDE, "OK")
            ok_list.append(texto)
            registro[clave(nombre, artista)] = {
                "nombre": nombre, "artista": artista,
                "fecha": time.strftime("%Y-%m-%d %H:%M"),
            }
            guardar_registro(registro, registry_file)
        else:
            p(ROJO, "FAILED")
            print(f"         {GRIS}{msg}{RESET}")
            still_failing.append((texto, msg))

        if i < len(failed_songs):
            time.sleep(ESPERA_ENTRE_SONGS)

    sep()
    p(NEGRITA + VERDE, f"  Downloaded : {len(ok_list)}")
    p(ROJO if still_failing else VERDE, f"  Still failing: {len(still_failing)}")

    if still_failing:
        with open(failures_csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["#", "Song", "Error", "Date"])
            for i, (nom, mot) in enumerate(still_failing, 1):
                writer.writerow([i, nom, mot.strip(), time.strftime("%Y-%m-%d %H:%M")])
        p(AMARILLO, f"\n  Updated: {failures_csv}")
    else:
        os.remove(failures_csv)
        p(VERDE, "\n  All songs downloaded! Failures file removed.")

    input(f"\n  {GRIS}Press Enter to go back...{RESET}")


def cabecera_menu(config):
    limpiar()
    print(f"\n{NEGRITA}{AZUL}{'═'*54}{RESET}")
    print(f"{NEGRITA}{AZUL}       Music Downloader{RESET}")
    print(f"{NEGRITA}{AZUL}{'═'*54}{RESET}\n")
    p(GRIS, f"  CSV     : {config['csv']}")
    p(GRIS, f"  Dest    : {os.path.abspath(os.path.expanduser(config['folder']))}")
    print()
    sep()
    print()

def menu_change_csv(config):
    limpiar()
    print(f"\n{NEGRITA}  Change CSV path{RESET}\n")
    p(GRIS, f"  Current path: {config['csv']}")
    print()
    p(CYAN, "  Opening file browser...")
    time.sleep(0.5)

    nueva = browse_file(title="Select your Spotify CSV file")

    if not nueva:
        # Fallback to manual input
        limpiar()
        print(f"\n{NEGRITA}  Change CSV path{RESET}\n")
        p(GRIS, f"  Current path: {config['csv']}")
        print()
        p(AMARILLO, "  No file browser found. Enter path manually:")
        p(GRIS, "  (leave blank to cancel)")
        print()
        nueva = input("  > ").strip()
        if not nueva:
            return
        nueva = os.path.expanduser(nueva)

    if not os.path.exists(nueva):
        p(ROJO, f"\n  File not found: {nueva}")
        p(AMARILLO, "  Check the path and try again.")
        time.sleep(2)
        return

    config["csv"] = nueva
    guardar_config(config)
    limpiar()
    p(VERDE, f"\n  CSV updated:")
    p(GRIS,  f"  {nueva}")
    time.sleep(2)

def menu_change_folder(config):
    limpiar()
    print(f"\n{NEGRITA}  Change download folder{RESET}\n")
    p(GRIS, f"  Current path: {os.path.abspath(os.path.expanduser(config['folder']))}")
    print()
    p(CYAN, "  Opening folder browser...")
    time.sleep(0.5)

    nueva = browse_folder(title="Select download folder for MP3 files")

    if not nueva:
        # Fallback to manual input
        limpiar()
        print(f"\n{NEGRITA}  Change download folder{RESET}\n")
        p(GRIS, f"  Current path: {os.path.abspath(os.path.expanduser(config['folder']))}")
        print()
        p(AMARILLO, "  No file browser found. Enter path manually:")
        p(GRIS, "  (leave blank to cancel)")
        print()
        nueva = input("  > ").strip()
        if not nueva:
            return
        nueva = os.path.expanduser(nueva)

    config["folder"] = nueva
    guardar_config(config)
    limpiar()
    p(VERDE, f"\n  Folder updated:")
    p(GRIS,  f"  {os.path.abspath(nueva)}")
    time.sleep(2)

def selector(opciones, titulo="", subtitulo=""):
    """
    Arrow key menu selector.
    Returns the index of the selected option.
    Use UP/DOWN to navigate, ENTER to confirm.
    """
    try:
        import curses
    except ImportError:
        # Windows needs windows-curses
        try:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "pip", "install", "windows-curses", "--quiet"], check=True)
            import curses
        except Exception:
            # Fallback to simple numbered menu if curses fails
            print(f"\n  {titulo}\n")
            if subtitulo:
                for line in subtitulo.split("\n"):
                    print(f"  {line}")
            print()
            for i, opt in enumerate(opciones, 1):
                print(f"  [{i}] {opt}")
            print()
            while True:
                try:
                    choice = int(input("  Select: ").strip())
                    if 1 <= choice <= len(opciones):
                        return choice - 1
                except (ValueError, KeyboardInterrupt):
                    pass

    def _draw(stdscr, selected):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_GREEN,  curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN,   curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK,  curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_WHITE,  curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        row = 1
        # Title
        if titulo:
            line = f"  {titulo}"
            stdscr.addstr(row, 0, "  " + "="*50, curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 0, line, curses.color_pair(2) | curses.A_BOLD)
            row += 1
            stdscr.addstr(row, 0, "  " + "="*50, curses.color_pair(2))
            row += 2

        if subtitulo:
            for line in subtitulo.split("\n"):
                if row < h - 1:
                    stdscr.addstr(row, 0, f"  {line}", curses.color_pair(5))
                    row += 1
            row += 1

        # Options
        for i, opt in enumerate(opciones):
            if row >= h - 2:
                break
            if i == selected:
                stdscr.addstr(row, 0, f"  > {opt} ", curses.color_pair(3) | curses.A_BOLD)
            else:
                stdscr.addstr(row, 0, f"    {opt}", curses.color_pair(4))
            row += 1

        row += 1
        if row < h - 1:
            stdscr.addstr(row, 0, "  ↑↓ navigate   ENTER select   Q quit", curses.color_pair(5))

        stdscr.refresh()

    def _run(stdscr):
        selected = 0
        while True:
            _draw(stdscr, selected)
            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(opciones)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(opciones)
            elif key in (curses.KEY_ENTER, 10, 13):
                return selected
            elif key in (ord("q"), ord("Q")):
                return len(opciones) - 1  # last = Exit

    return curses.wrapper(_run)


def selector_multi(opciones, titulo="", subtitulo=""):
    """
    Multi-select menu. SPACE to toggle, ENTER to confirm.
    Returns list of selected indexes.
    """
    try:
        import curses
    except ImportError:
        try:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "pip", "install", "windows-curses", "--quiet"], check=True)
            import curses
        except Exception:
            # Fallback to simple numbered multi-select
            print(f"\n  {titulo}\n")
            for i, opt in enumerate(opciones, 1):
                print(f"  [{i}] {opt}")
            print()
            print("  Enter numbers separated by spaces (e.g. 1 3 5):")
            try:
                selection = input("  > ").strip().split()
                return [int(x)-1 for x in selection if x.isdigit() and 1 <= int(x) <= len(opciones)]
            except (ValueError, KeyboardInterrupt):
                return []

    def _draw(stdscr, selected_idx, checked):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_GREEN,  curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN,   curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK,  curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_WHITE,  curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED,    curses.COLOR_BLACK)

        row = 1
        if titulo:
            stdscr.addstr(row, 0, "  " + "="*50, curses.color_pair(2))
            row += 1
            stdscr.addstr(row, 0, f"  {titulo}", curses.color_pair(2) | curses.A_BOLD)
            row += 1
            stdscr.addstr(row, 0, "  " + "="*50, curses.color_pair(2))
            row += 2

        if subtitulo:
            for line in subtitulo.split("\n"):
                if row < h - 1:
                    stdscr.addstr(row, 0, f"  {line}", curses.color_pair(5))
                    row += 1
            row += 1

        for i, opt in enumerate(opciones):
            if row >= h - 2:
                break
            mark = "●" if i in checked else "○"
            color = curses.color_pair(1) if i in checked else curses.color_pair(4)
            if i == selected_idx:
                stdscr.addstr(row, 0, f"  > {mark} {opt} ", curses.color_pair(3) | curses.A_BOLD)
            else:
                stdscr.addstr(row, 0, f"    {mark} {opt}", color)
            row += 1

        row += 1
        if row < h - 1:
            sel_count = len(checked)
            stdscr.addstr(row, 0,
                f"  ↑↓ navigate   SPACE select ({sel_count} selected)   ENTER confirm   Q cancel",
                curses.color_pair(5))
        stdscr.refresh()

    def _run(stdscr):
        selected_idx = 0
        checked = set()
        while True:
            _draw(stdscr, selected_idx, checked)
            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                selected_idx = (selected_idx - 1) % len(opciones)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected_idx = (selected_idx + 1) % len(opciones)
            elif key == ord(" "):
                if selected_idx in checked:
                    checked.remove(selected_idx)
                else:
                    checked.add(selected_idx)
            elif key in (curses.KEY_ENTER, 10, 13):
                return sorted(checked)
            elif key in (ord("q"), ord("Q")):
                return []

    return curses.wrapper(_run)


def menu_principal():
    config = cargar_config()

    opciones = [
        ("Start download",         lambda: iniciar_descarga(config)),
        ("Retry failed songs",     lambda: retry_failures(config)),
        ("Change CSV path",        lambda: menu_change_csv(config)),
        ("Change download folder", lambda: menu_change_folder(config)),
        ("Check for duplicates",   lambda: check_duplicates(config)),
        ("Exit",                   None),
    ]

    while True:
        # Build subtitle with current config
        csv_path   = config.get("csv", "not set")
        dest       = os.path.abspath(os.path.expanduser(config.get("folder", CARPETA_SALIDA)))
        subtitulo  = f"CSV  : {csv_path}\nDest : {dest}"

        labels = [o[0] for o in opciones]
        idx = selector(labels, titulo="🎵  Music Downloader", subtitulo=subtitulo)

        limpiar()
        action = opciones[idx][1]

        if action is None:
            limpiar()
            p(VERDE, "\n  Goodbye!\n")
            sys.exit(0)
        else:
            action()


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        limpiar()
        p(VERDE, "\n  Goodbye!\n")
        sys.exit(0)
