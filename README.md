# 🎵 spotify-to-mp3

Automatically download any Spotify playlist as MP3 files using [exportify.app](https://exportify.app) and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- 📋 Reads songs from a CSV exported from any Spotify playlist via [exportify.app](https://exportify.app)
- ✅ Smart registry — only downloads new songs, never re-downloads
- 🔍 Searches multiple sources: YouTube → YouTube (variants) → SoundCloud
- 🎨 Embeds metadata and album artwork into every MP3
- 💾 Interactive arrow-key menu — no code editing needed
- 🍪 Auto-detects your browser for cookies (avoids YouTube age restrictions and blocks)
- 🗑️ Built-in duplicate file detector with multi-select deletion
- 🔄 Auto-installs all dependencies on first run

---

## 📦 Supported systems

| Distro | Package Manager |
|--------|----------------|
| Fedora, Bazzite, RHEL | `dnf` |
| Ubuntu, Debian, Mint, Kali | `apt` |
| Arch, CachyOS, Manjaro | `pacman` |

> **Note for Kali users:** Make sure your repositories are configured before running:
> ```bash
> echo "deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" | sudo tee /etc/apt/sources.list
> sudo apt update
> ```

---

## 🚀 Installation

```bash
git clone https://github.com/Pazco/spotify-to-mp3.git
cd spotify-to-mp3
chmod +x launch.sh
```

No Python libraries needed — only uses the standard library.

---

## 📖 Usage

### 1. Export your Spotify playlist

1. Go to [exportify.app](https://exportify.app)
2. Log in with your Spotify account
3. Click **Export** next to any playlist (Liked Songs, your own playlists, or any public playlist)
4. Save the CSV file as `songs.csv` in the project folder

### 2. Open your browser at least once

Before running the script, open your browser (Firefox, Chrome, Brave...) and log in to **YouTube**. This allows the script to use your cookies to bypass age restrictions and bot detection.

> You only need to do this once.

### 3. Run the script

Double-click `launch.sh` and select **"Run in terminal"**, or from the terminal:

```bash
./launch.sh
```

Navigate with arrow keys:

```
  > Start download
    Change CSV path
    Change download folder
    Check for duplicates
    Exit
```

### 4. Update when you add new songs

1. Export a new CSV from exportify.app
2. Run the script again — **it will only download the new songs**

---

## 🍪 Browser auto-detection

The script automatically detects your installed browser for cookies in this order:

**Brave → Firefox → Chrome → Chromium → Edge**

To force a specific browser, edit this line in `spotify-to-mp3.py`:

```python
COOKIES_NAVEGADOR = "firefox"   # brave | firefox | chrome | chromium | edge
```

Or use a manually exported cookies file:

```python
COOKIES_NAVEGADOR = "/path/to/cookies.txt"
```

---

## 🗑️ Duplicate checker

The built-in duplicate checker (option 4 in the menu) scans your download folder and lets you:

- **Select which duplicates to delete** using the arrow key + space selector
- **Delete all duplicates at once**

It detects duplicates by normalized filename (ignores case, spaces and special characters).

---

## ❌ When a song fails

Some songs will fail and be saved to `_failures.txt`. This usually happens when:

- The video has been **deleted** from YouTube
- The video is **copyright blocked** in all countries
- The video requires **age verification** and no browser cookies are available

For most songs (~95%) the download will work fine.

---

## 📁 Project structure

```
spotify-to-mp3/
├── spotify-to-mp3.py   # Main script
├── launch.sh           # Double-click launcher (installs dependencies automatically)
├── .gitignore
└── README.md
```

Files generated at runtime (not uploaded to GitHub):
```
├── songs.csv                       # Your exported Spotify CSV
├── .registro.json                  # Download history
├── .descargador_config.json        # Your path configuration
└── music_downloaded/               # Your MP3 files
    └── _failures.txt               # Songs that could not be downloaded
```

---

## ⚠️ Disclaimer

This project is for personal and educational use only. Only download music you have the rights to or that is freely available. Respect the terms of service of Spotify and YouTube.

---

## 🤝 Contributing

Have ideas to improve the script? Open an **issue** or a **pull request** — all contributions are welcome.
