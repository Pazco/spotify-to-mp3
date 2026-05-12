#!/bin/bash
# ─────────────────────────────────────────────
# spotify-to-mp3 launcher
# Double-click this file to start the bot
# ─────────────────────────────────────────────

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎵  spotify-to-mp3"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Detect package manager ──────────────────
if command -v dnf &>/dev/null; then
    PKG="dnf"
elif command -v apt &>/dev/null; then
    PKG="apt"
elif command -v pacman &>/dev/null; then
    PKG="pacman"
else
    echo -e "${RED}  ✗ Could not detect package manager (dnf/apt/pacman)${RESET}"
    echo "  Please install yt-dlp, ffmpeg and nodejs manually."
    read -p "  Press Enter to exit..."
    exit 1
fi

echo -e "${CYAN}  Checking dependencies...${RESET}"

# ── python3 ─────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}  Installing python3...${RESET}"
    if [ "$PKG" = "dnf" ]; then
        sudo dnf install -y python3
    elif [ "$PKG" = "apt" ]; then
        sudo apt update -qq && sudo apt install -y python3
    elif [ "$PKG" = "pacman" ]; then
        sudo pacman -S --noconfirm python
    fi
fi

# ── ffmpeg ──────────────────────────────────
if ! command -v ffmpeg &>/dev/null; then
    echo -e "${YELLOW}  Installing ffmpeg...${RESET}"
    if [ "$PKG" = "dnf" ]; then
        sudo dnf install -y ffmpeg
    elif [ "$PKG" = "apt" ]; then
        sudo apt update -qq && sudo apt install -y ffmpeg
    elif [ "$PKG" = "pacman" ]; then
        sudo pacman -S --noconfirm ffmpeg
    fi
fi

# ── nodejs ──────────────────────────────────
if ! command -v node &>/dev/null; then
    echo -e "${YELLOW}  Installing nodejs...${RESET}"
    if [ "$PKG" = "dnf" ]; then
        sudo dnf install -y nodejs
    elif [ "$PKG" = "apt" ]; then
        sudo apt update -qq && sudo apt install -y nodejs
    elif [ "$PKG" = "pacman" ]; then
        sudo pacman -S --noconfirm nodejs
    fi
fi

# ── yt-dlp ──────────────────────────────────
# yt-dlp is not always in apt repos, so we try multiple methods
if ! command -v yt-dlp &>/dev/null; then
    echo -e "${YELLOW}  Installing yt-dlp...${RESET}"
    if [ "$PKG" = "dnf" ]; then
        sudo dnf install -y yt-dlp
    elif [ "$PKG" = "pacman" ]; then
        sudo pacman -S --noconfirm yt-dlp
    elif [ "$PKG" = "apt" ]; then
        # Try apt first, fall back to pip, then direct binary
        if sudo apt install -y yt-dlp 2>/dev/null; then
            echo -e "${GREEN}  yt-dlp installed via apt${RESET}"
        elif command -v pip3 &>/dev/null; then
            echo -e "${YELLOW}  Installing yt-dlp via pip...${RESET}"
            pip3 install yt-dlp --break-system-packages 2>/dev/null || pip3 install yt-dlp
        else
            echo -e "${YELLOW}  Installing yt-dlp via direct download...${RESET}"
            sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
            sudo chmod a+rx /usr/local/bin/yt-dlp
        fi
    fi
fi

# ── Final check ─────────────────────────────
MISSING=()
command -v yt-dlp &>/dev/null  || MISSING+=("yt-dlp")
command -v ffmpeg &>/dev/null  || MISSING+=("ffmpeg")
command -v python3 &>/dev/null || MISSING+=("python3")

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}  ✗ Could not install: ${MISSING[*]}${RESET}"
    echo "  Please install them manually and try again."
    read -p "  Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}  ✓ All dependencies ready${RESET}"
echo ""

# ── Run the bot ─────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/spotify-to-mp3.py"

