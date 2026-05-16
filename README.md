# 🎵 spotify-to-mp3

Automatically download any Spotify playlist as MP3 files using [exportify.app](https://exportify.app) and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

---

## ✨ Features

- 📋 Downloads any Spotify playlist exported as CSV via [exportify.app](https://exportify.app)
- ✅ Smart registry — only downloads new songs, never re-downloads
- 🔍 Searches multiple sources: YouTube → YouTube (variants) → SoundCloud
- 🎨 Embeds metadata and album artwork into every MP3
- 💾 Interactive arrow-key menu — no code editing needed
- 🍪 Auto-detects your browser for cookies (bypasses YouTube age restrictions)
- 🗑️ Duplicate detector — finds exact and similar duplicates, lets you select which to delete
- 🔁 Retry failed songs with one click
- 📂 Native file browser for selecting CSV and download folder
- 📊 Failures saved to `.failures.csv` with song name, error and date

---

## 💻 Supported platforms

| Platform | Script | Launcher |
|----------|--------|----------|
| Linux (Fedora, Ubuntu, Mint, Arch, Bazzite, CachyOS...) | `spotify-to-mp3.py` | `launch.sh` |
| Windows 10 / 11 | `spotify-to-mp3-windows.py` | `launch.bat` |
| macOS (Intel + Apple Silicon) | `spotify-to-mp3-mac.py` | `launch-mac.sh` |

---

## 🚀 Installation

```bash
git clone https://github.com/Pazco/spotify-to-mp3.git
cd spotify-to-mp3
```

**Linux:**
```bash
chmod +x launch.sh
```

**macOS:**
```bash
chmod +x launch-mac.sh
```

**Windows:** No extra steps needed.

---

## 📖 Usage

### 1. Export your Spotify playlist

1. Go to [exportify.app](https://exportify.app)
2. Log in with your Spotify account
3. Click **Export** next to any playlist (Liked Songs, your own playlists, or any public playlist)
4. Save the CSV file somewhere on your computer

### 2. Open your browser at least once

Before running the script, open your browser and log in to **YouTube**. This allows the script to use your cookies to bypass age restrictions and bot detection.

> You only need to do this once.

### 3. Run the script

**Linux:**
```bash
./launch.sh
```

**macOS:**
```bash
./launch-mac.sh
```

**Windows:** Double-click `launch.bat`

> The launcher installs all dependencies automatically on first run.

Navigate the menu with arrow keys:

```
  > Start download
    Retry failed songs
    Change CSV path
    Change download folder
    Check for duplicates
    Exit                        (Windows also has: Setup YouTube cookies)
```

### 4. Update when you add new songs

1. Export a new CSV from exportify.app
2. Run the script again — **it will only download the new songs**

---

## 🍪 Browser & cookies

The script auto-detects your installed browser in this order:

**Linux / macOS:** Brave → Firefox → Chrome → Chromium → Edge

**Windows:** Firefox first (recommended), then Brave, Chrome, Edge

> ⚠️ **Windows users with Chrome/Brave/Edge:** These browsers encrypt cookies with DPAPI, which yt-dlp cannot read directly. Use the **"Setup YouTube cookies"** option in the menu — it guides you through exporting a `cookies.txt` file in one click. Firefox does not have this issue.

To force a specific browser, edit this line in the script:
```python
COOKIES_NAVEGADOR = "firefox"   # brave | firefox | chrome | chromium | edge
```

---

## 🗑️ Duplicate checker

Option in the menu that scans your download folder and detects:

- **Exact duplicates** — same song, different filename (e.g. `Song.mp3` and `Song - copia.mp3`)
- **Similar files** — 85%+ similar names (e.g. `Song.mp3` and `Song (Remastered).mp3`)

For each group you can:
- Navigate with arrow keys
- **SPACE** to toggle individual files
- **N** to select all newest files
- **O** to select all oldest files
- **A** to select all except the oldest
- **ENTER** to confirm deletion

---

## 🔁 Retry failed songs

If some songs failed to download, use **"Retry failed songs"** in the menu. It reads `.failures.csv` from the script folder, retries each song, and updates the file — removing the ones that succeeded. If all succeed, the file is deleted automatically.

---

## ❌ When a song fails

Some songs will fail and be saved to `.failures.csv`. This usually happens when:

- The video has been **deleted** from YouTube
- The video is **copyright blocked** in all countries
- The video requires **age verification** and no browser cookies are available

For most songs (~95%) the download will work fine.

---

## 📁 Project structure

```
spotify-to-mp3/
├── spotify-to-mp3.py         # Linux script
├── spotify-to-mp3-windows.py # Windows script
├── spotify-to-mp3-mac.py     # macOS script
├── launch.sh                 # Linux launcher
├── launch-mac.sh             # macOS launcher
├── launch.bat                # Windows launcher
├── .gitignore
└── README.md
```

Files generated at runtime (not uploaded to GitHub):
```
├── .config.json              # Your path configuration
├── .registry.json            # Download history
├── .failures.csv             # Failed songs (song, error, date)
└── cookies.txt               # YouTube cookies (Windows)
```

---

## ⚠️ Disclaimer

This project is for personal and educational use only. Only download music you have the rights to or that is freely available. Respect the terms of service of Spotify and YouTube.

---

## 🤝 Contributing

Have ideas to improve the script? Open an **issue** or a **pull request** — all contributions are welcome.
