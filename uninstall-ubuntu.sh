#!/usr/bin/env bash
set -euo pipefail
if [[ "${EUID}" -ne 0 ]]; then
    echo "管理者権限が必要です。sudo ./uninstall-ubuntu.sh を実行してください。"
    exit 1
fi
rm -rf /opt/moeclock
rm -f /usr/share/applications/moeclock.desktop /usr/share/pixmaps/moeclock.png
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi
echo "萌え時計をアンインストールしました。設定ファイル ~/.config/moeclock.xml は保持しています。"
