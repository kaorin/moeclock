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
# Install the application icon in the hicolor theme as well as pixmaps.
install -D -m 644 "$APP_DIR/moeclock.png" /usr/share/icons/hicolor/64x64/apps/moeclock.png
install -D -m 644 "$APP_DIR/moeclock.png" /usr/share/icons/hicolor/128x128/apps/moeclock.png
install -D -m 644 "$APP_DIR/moeclock.png" /usr/share/icons/hicolor/256x256/apps/moeclock.png

# Use a themed icon name and match the running GTK window class.
sed -i 's|^Icon=.*|Icon=moeclock|' /usr/share/applications/moeclock.desktop
sed -i 's|^StartupWMClass=.*|StartupWMClass=MoeClock|' /usr/share/applications/moeclock.desktop
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f /usr/share/icons/hicolor || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi

# Install and enable the per-user GNOME Shell companion. On Wayland the
# compositor (Mutter) owns global window geometry, so the extension must run
# inside the active GNOME user session. Pass that session's D-Bus address to
# gnome-extensions; runuser alone would often lose it and silently fail.
EXT_UUID="moeclock-position-restore@local"
if [[ -n "${SUDO_USER:-}" && "${SUDO_USER}" != "root" ]]; then
    TARGET_USER="$SUDO_USER"
    TARGET_UID="$(id -u "$TARGET_USER")"
    TARGET_GROUP="$(id -gn "$TARGET_USER")"
    TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
    EXT_DIR="$TARGET_HOME/.local/share/gnome-shell/extensions/$EXT_UUID"
    RUNTIME_DIR="/run/user/$TARGET_UID"
    if [[ -n "$TARGET_HOME" && -d "$SCRIPT_DIR/gnome-extension" ]]; then
        install -d -o "$TARGET_USER" -g "$TARGET_GROUP" -m 755 "$EXT_DIR"
        cp -a "$SCRIPT_DIR/gnome-extension/." "$EXT_DIR/"
        chown -R "$TARGET_USER:$TARGET_GROUP" "$EXT_DIR"
        if command -v gnome-extensions >/dev/null 2>&1; then
            if [[ -S "$RUNTIME_DIR/bus" ]]; then
                if runuser -u "$TARGET_USER" -- env \
                    HOME="$TARGET_HOME" \
                    XDG_RUNTIME_DIR="$RUNTIME_DIR" \
                    DBUS_SESSION_BUS_ADDRESS="unix:path=$RUNTIME_DIR/bus" \
                    gnome-extensions enable "$EXT_UUID"; then
                    echo "GNOME Shell拡張を有効化しました: $EXT_UUID"
                else
                    echo "警告: GNOME Shell拡張の有効化に失敗しました。再ログイン後、次を実行してください:"
                    echo "  gnome-extensions enable $EXT_UUID"
                fi
            else
                echo "GNOMEセッションのD-Busが見つかりません。ログイン後に次を実行してください:"
                echo "  gnome-extensions enable $EXT_UUID"
            fi
        else
            echo "警告: gnome-extensions コマンドがありません。GNOME Shell拡張の有効化を確認してください。"
        fi
        echo "GNOME Shell拡張を $EXT_DIR にインストールしました。"
    fi
fi

echo
echo "萌え時計をインストールしました。アプリケーション一覧から「萌え時計」を起動してください。"
echo "端末から起動する場合: /opt/moeclock/moeclock"
