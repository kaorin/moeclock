# GitHub Release 用情報

**タグ:** `v1.5.2.16`  
**リリース名:** 萌え時計 1.5.2.16 - Ubuntu 26.10 / Wayland対応

## リリース本文

Ubuntu 26.10対応版「萌え時計 1.5.2.16」を公開します。

### 主な更新
- Wayland環境でGNOME Shell拡張機能（Mutter連携）を使用したウィンドウ位置の保存・復元に対応。
- タイトルバーの表示・非表示を切り替えた際の位置ずれを修正。
- タイトルバー再表示後も、切り替え前のウィンドウ位置を維持。
- 位置復元時にサイズを強制変更しないよう変更。
- GNOME Shell拡張機能をバージョン7に更新。

### インストール
ZIPを展開し、展開先で次を実行してください。

```bash
sudo ./install-ubuntu.sh
```

拡張機能の更新後はログアウト・再ログインし、次のコマンドで状態を確認してください。

```bash
gnome-extensions info moeclock-position-restore@local
```

詳細は同梱の `README.md` と `RELEASE_NOTES.md` を参照してください。
