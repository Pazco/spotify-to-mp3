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
CARPETA_SALIDA     = "music_downloaded"
CSV_FILE           = "songs.csv"
COOKIES_NAVEGADOR  = "brave"
ESPERA_ENTRE_SONGS = 1
TIMEOUT_SONG       = 300
CONFIG_FILE        = ".descargador_config.json"
# ═══════════════════════════════════════════════════════

VERDE    = "\033[92m"
ROJO     = "\033[91m"
AMARILLO = "\033[93m"
CYAN     = "\033[96m"
GRIS     = "\033[90m"
AZUL     = "\033[94m"
RESET    = "\033[0m"
NEGRITA  = "\033[1m"

def p(color, texto): print(f"{color}{texto}{RESET}")
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
    registro_file  = os.path.join(script_dir, ".registro.json")
    cookies        = COOKIES_NAVEGADOR

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
        log_path = os.path.join(download_folder, "_failures.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("Songs that could not be downloaded:\n\n")
            for nom, mot in failures:
                f.write(f"- {nom}\n  {mot}\n\n")
        p(AMARILLO, f"\n  Failures log -> {log_path}")

    print(f"{'='*54}\n")
    input(f"  {GRIS}Press Enter to go back to menu...{RESET}")


# ═══════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════

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
    p(CYAN, "  Enter the new CSV path")
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
    p(VERDE, f"\n  CSV updated: {nueva}")
    time.sleep(1.5)

def menu_change_folder(config):
    limpiar()
    print(f"\n{NEGRITA}  Change download folder{RESET}\n")
    p(GRIS, f"  Current path: {os.path.abspath(os.path.expanduser(config['folder']))}")
    print()
    p(CYAN, "  Enter the new download folder path")
    p(GRIS, "  (leave blank to cancel)")
    print()
    nueva = input("  > ").strip()
    if not nueva:
        return
    nueva = os.path.expanduser(nueva)
    config["folder"] = nueva
    guardar_config(config)
    p(VERDE, f"\n  Folder updated: {os.path.abspath(nueva)}")
    time.sleep(1.5)

def menu_principal():
    config = cargar_config()

    opciones = [
        ("1", "Start download",          lambda: iniciar_descarga(config)),
        ("2", "Change CSV path",        lambda: menu_change_csv(config)),
        ("3", "Change download folder", lambda: menu_change_folder(config)),
        ("4", "Exit",                       None),
    ]

    while True:
        cabecera_menu(config)
        for clave_op, label, _ in opciones:
            if clave_op == "4":
                p(GRIS, f"  [{clave_op}] {label}")
            else:
                p(RESET, f"  {NEGRITA}[{clave_op}]{RESET} {label}")
        print()
        sep()
        opcion = input(f"\n  {CYAN}Select an option:{RESET} ").strip()

        if opcion == "1":
            iniciar_descarga(config)
        elif opcion == "2":
            menu_change_csv(config)
        elif opcion == "3":
            menu_change_folder(config)
        elif opcion == "4":
            limpiar()
            p(VERDE, "\n  Goodbye!\n")
            sys.exit(0)
        else:
            p(ROJO, "  Invalid option.")
            time.sleep(1)


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        limpiar()
        p(VERDE, "\n  Goodbye!\n")
        sys.exit(0)
