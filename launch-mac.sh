#!/bin/bash
# ─────────────────────────────────────────────
# spotify-to-mp3 launcher for macOS
# Double-click this file or run: bash launch-mac.sh
# ─────────────────────────────────────────────

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎵  spotify-to-mp3  (macOS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}  Checking dependencies...${RESET}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Homebrew ─────────────────────────────────
if ! command -v brew &>/dev/null; then
    echo -e "${YELLOW}  Homebrew not found. Installing...${RESET}"
    echo -e "${YELLOW}  This may take a few minutes and ask for your password.${RESET}"
    echo ""
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add brew to PATH for Apple Silicon and Intel
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi

    if ! command -v brew &>/dev/null; then
        echo -e "${RED}  Homebrew installation failed.${RESET}"
        echo "  Please install it manually from https://brew.sh"
        read -p "  Press Enter to exit..."
        exit 1
    fi
    echo -e "${GREEN}  Homebrew installed${RESET}"
else
    # Make sure brew is in PATH (Apple Silicon)
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo -e "${GREEN}  [OK] Homebrew ready${RESET}"
fi

# ── Python 3 ─────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}  Installing Python 3...${RESET}"
    brew install python
fi
echo -e "${GREEN}  [OK] Python ready${RESET}"

# ── ffmpeg ───────────────────────────────────
if ! command -v ffmpeg &>/dev/null; then
    echo -e "${YELLOW}  Installing ffmpeg...${RESET}"
    brew install ffmpeg
fi
echo -e "${GREEN}  [OK] ffmpeg ready${RESET}"

# ── nodejs ───────────────────────────────────
if ! command -v node &>/dev/null; then
    echo -e "${YELLOW}  Installing Node.js...${RESET}"
    brew install node
fi
echo -e "${GREEN}  [OK] Node.js ready${RESET}"

# ── yt-dlp ───────────────────────────────────
if ! command -v yt-dlp &>/dev/null; then
    echo -e "${YELLOW}  Installing yt-dlp...${RESET}"
    brew install yt-dlp
    if ! command -v yt-dlp &>/dev/null; then
        echo -e "${YELLOW}  Trying pip...${RESET}"
        pip3 install yt-dlp --break-system-packages 2>/dev/null || pip3 install yt-dlp
    fi
fi
echo -e "${GREEN}  [OK] yt-dlp ready${RESET}"

# ── Final check ──────────────────────────────
MISSING=()
command -v yt-dlp  &>/dev/null || MISSING+=("yt-dlp")
command -v ffmpeg  &>/dev/null || MISSING+=("ffmpeg")
command -v python3 &>/dev/null || MISSING+=("python3")

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}  Could not install: ${MISSING[*]}${RESET}"
    echo "  Please install them manually with: brew install ${MISSING[*]}"
    read -p "  Press Enter to exit..."
    exit 1
fi

echo ""
echo -e "${GREEN}  All dependencies ready${RESET}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Run the bot ──────────────────────────────
python3 "$SCRIPT_DIR/spotify-to-mp3-mac.py"
