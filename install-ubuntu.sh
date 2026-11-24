#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "管理者権限が必要です。sudo ./install-ubuntu.sh を実行してください。"
    exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/opt/moeclock"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
    python3 \
    python3-gi \
    python3-gi-cairo \
    python3-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-rsvg-2.0 \
    pulseaudio-utils \
    fonts-noto-cjk

install -d -m 755 "$APP_DIR"
# Copy the application and all bundled skins/locales/sounds, excluding repository metadata.
cp -a "$SCRIPT_DIR/." "$APP_DIR/"
rm -rf "$APP_DIR/.git" "$APP_DIR/__pycache__"
chmod 755 "$APP_DIR/moeclock" "$APP_DIR/moeclock.py" "$APP_DIR/moeclock_autostart"

install -D -m 644 "$APP_DIR/moeclock.desktop" /usr/share/applications/moeclock.desktop
install -D -m 644 "$APP_DIR/moeclock.png" /usr/share/pixmaps/moeclock.png

# Make desktop icon use the standard icon path.
sed -i 's|Icon=/opt/moeclock/moeclock.png|Icon=moeclock|' /usr/share/applications/moeclock.desktop

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi

echo
echo "萌え時計をインストールしました。アプリケーション一覧から「萌え時計」を起動してください。"
echo "端末から起動する場合: /opt/moeclock/moeclock"
