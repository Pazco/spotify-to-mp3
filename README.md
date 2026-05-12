[README.md](https://github.com/user-attachments/files/27660698/README.md)
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
- 💾 Interactive menu to configure paths without editing the code
- 🍪 Browser cookie support to avoid YouTube blocks

---

## 📦 Requirements

The launcher installs all dependencies automatically. Supported distros:

| Distro | Package Manager |
|--------|----------------|
| Fedora, Bazzite, RHEL | `dnf` |
| Ubuntu, Debian, Mint, Kali | `apt` |
| Arch, CachyOS, Manjaro | `pacman` |

> **Note:** Your system needs configured repositories. On a fresh Kali install, set them up first:
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

No Python libraries to install — only uses the standard library.

---

## 📖 Usage

### 1. Export your Spotify playlist

1. Go to [exportify.app](https://exportify.app)
2. Log in with your Spotify account
3. Click **Export** next to any playlist (Liked Songs, your own playlists, or any public playlist)
4. Save the CSV file as `songs.csv` in the project folder

### 2. Run the script

Double-click `launch.sh` and select **"Run in terminal"**, or run it from the terminal:

```bash
./launch.sh
```

You will see an interactive menu:

```
══════════════════════════════════════════════════════
       Music Downloader
══════════════════════════════════════════════════════

  CSV     : songs.csv
  Dest    : /home/user/music_downloaded

  [1] Start download
  [2] Change CSV path
  [3] Change download folder
  [4] Exit
```

### 3. Update when you add new songs

1. Export a new CSV from exportify.app
2. Run the script again — **it will only download the new songs**

---

## 🍪 Avoiding YouTube blocks

If YouTube starts asking for verification, edit this line in `spotify-to-mp3.py`:

```python
COOKIES_BROWSER = "brave"   # brave | firefox | chrome | chromium | edge
```

Or use a manually exported cookies file:

```python
COOKIES_BROWSER = "/path/to/cookies.txt"
```

---

## 📁 Project structure

```
spotify-to-mp3/
├── spotify-to-mp3.py   # Main script
├── launch.sh           # Double-click launcher
├── .gitignore
└── README.md
```

Files generated when running (not uploaded to GitHub):
```
├── songs.csv                   # Your exported Spotify CSV
├── .registro.json              # Download history
├── .descargador_config.json    # Your path configuration
└── music_downloaded/           # Your MP3 files
```

---

## ⚠️ Disclaimer

This project is for personal and educational use only. Only download music you have the rights to or that is freely available. Respect the terms of service of Spotify and YouTube.

---

## 🤝 Contributing

Have ideas to improve the script? Open an **issue** or a **pull request** — all contributions are welcome.
