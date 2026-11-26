import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

const APP_IDS = new Set(['moeclock', 'moeclock.desktop']);
const APP_CLASSES = new Set(['moeclock', 'moeclock.py']);
// Mutter frame placement can settle a little after a GTK/Wayland surface is
// mapped. Reapply POSITION ONLY; never resize the frame from a stale snapshot.
const RESTORE_DELAYS = [500, 1100, 1900];

export default class MoeClockPositionRestore extends Extension {
    enable() {
        this._log('extension enabled');
        this._file = Gio.File.new_for_path(
            GLib.build_filenamev([GLib.get_user_config_dir(), 'moeclock', 'wayland-window.json'])
        );
        this._geometry = this._loadGeometry();
        this._tracked = new Map();
        this._diagnosed = new WeakSet();
        this._windowCreatedId = global.display.connect('window-created', (_display, window) => {
            this._tryTrackWindow(window);
        });
        this._scanWindows();
        this._scanSource = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 700, () => {
            this._scanWindows();
            return GLib.SOURCE_CONTINUE;
        });
    }

    disable() {
        if (this._windowCreatedId) {
            global.display.disconnect(this._windowCreatedId);
            this._windowCreatedId = 0;
        }
        if (this._scanSource) {
            GLib.source_remove(this._scanSource);
            this._scanSource = 0;
        }
        for (const [window, info] of this._tracked) {
            for (const id of info.signals) {
                try { window.disconnect(id); } catch (_) {}
            }
            for (const source of [...info.restoreSources, info.saveSource]) {
                if (source) GLib.source_remove(source);
            }
        }
        this._tracked.clear();
        // Keep the last committed geometry. Disabling/reloading the extension
        // must never replace it with Mutter's transient startup placement.
        this._saveGeometry();
    }

    _log(message) { console.log(`[MoeClock Position] ${message}`); }

    _safeCall(window, method, fallback = '') {
        try {
            if (typeof window[method] === 'function') {
                const value = window[method]();
                return value === null || value === undefined ? fallback : value;
            }
        } catch (_) {}
        return fallback;
    }

    _processInfo(pid) {
        if (!pid || pid <= 0) return {comm: '', cmdline: ''};
        let comm = '', cmdline = '';
        try {
            const [ok, bytes] = GLib.file_get_contents(`/proc/${pid}/comm`);
            if (ok) comm = new TextDecoder().decode(bytes).trim().toLowerCase();
        } catch (_) {}
        try {
            const [ok, bytes] = GLib.file_get_contents(`/proc/${pid}/cmdline`);
            if (ok) cmdline = new TextDecoder().decode(bytes).replace(/\0/g, ' ').trim().toLowerCase();
        } catch (_) {}
        return {comm, cmdline};
    }

    _windowDetails(window) {
        const wmClass = String(this._safeCall(window, 'get_wm_class')).toLowerCase();
        const instance = String(this._safeCall(window, 'get_wm_class_instance')).toLowerCase();
        const appId = String(this._safeCall(window, 'get_gtk_application_id')).toLowerCase();
        const sandboxedAppId = String(this._safeCall(window, 'get_sandboxed_app_id')).toLowerCase();
        const title = String(this._safeCall(window, 'get_title'));
        const pid = Number(this._safeCall(window, 'get_pid', 0)) || 0;
        return {wmClass, instance, appId, sandboxedAppId, title, pid, ...this._processInfo(pid)};
    }

    _isMoeClock(d) {
        const values = [d.wmClass, d.instance, d.appId, d.sandboxedAppId];
        if (values.some(v => APP_CLASSES.has(v) || APP_IDS.has(v) || v.includes('moeclock'))) return true;
        return d.comm === 'moeclock' || d.cmdline.includes('/moeclock/moeclock.py') || d.cmdline.includes('/moeclock/moeclock ');
    }

    _scanWindows() {
        for (const actor of global.get_window_actors()) this._tryTrackWindow(actor.meta_window);
    }

    _tryTrackWindow(window) {
        if (!window || this._tracked.has(window)) return;
        const d = this._windowDetails(window);
        if (this._isMoeClock(d)) this._trackWindow(window, d);
        else if (!this._diagnosed.has(window)) {
            this._diagnosed.add(window);
            this._log(`window candidate: appId=${d.appId || '(empty)'} sandboxedAppId=${d.sandboxedAppId || '(empty)'} class=${d.wmClass || '(empty)'} instance=${d.instance || '(empty)'} pid=${d.pid} comm=${d.comm || '(empty)'} cmdline=${d.cmdline || '(empty)'} title=${d.title || '(empty)'}`);
        }
    }

    _trackWindow(window, details) {
        if (this._tracked.has(window)) return;
        const info = {signals: [], restoreSources: [], saveSource: 0, ready: false, restoring: true, unmanaged: false, lastFrame: null};
        this._tracked.set(window, info);
        this._log(`matched window: appId=${details.appId} class=${details.wmClass} instance=${details.instance} pid=${details.pid} title=${details.title}`);

        const scheduleSave = () => {
            if (!info.ready || info.restoring || info.unmanaged || info.saveSource) return;
            info.saveSource = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 450, () => {
                info.saveSource = 0;
                if (info.ready && !info.restoring && !info.unmanaged) this._capturePosition(window, 'geometry-change');
                return GLib.SOURCE_REMOVE;
            });
        };
        // Remember the last stable frame while this Meta.Window still exists.
        // GTK recreates its Wayland surface when decorations are toggled; the
        // unmanaged signal is the hand-off point to the replacement Meta.Window.
        const rememberFrame = () => {
            try {
                const r = window.get_frame_rect();
                if (r && r.width >= 80 && r.height >= 60)
                    info.lastFrame = {x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height)};
            } catch (_) {}
        };
        rememberFrame();
        for (const signal of ['position-changed', 'size-changed']) {
            try {
                info.signals.push(window.connect(signal, () => {
                    rememberFrame();
                    scheduleSave();
                }));
            } catch (e) { this._log(`signal connect failed (${signal}): ${e}`); }
        }
        info.signals.push(window.connect('unmanaged', () => {
            // Flush a pending user move before the native surface is destroyed.
            // Use the last observed frame, not the replacement window's initial
            // centered frame, which is the source of titlebar-toggle drift.
            if (info.saveSource) {
                GLib.source_remove(info.saveSource);
                info.saveSource = 0;
            }
            if (info.lastFrame && this._validGeometry({...info.lastFrame, monitor: 0})) {
                this._geometry = {
                    ...(this._geometry || {}),
                    x: info.lastFrame.x, y: info.lastFrame.y,
                    width: info.lastFrame.width, height: info.lastFrame.height,
                    monitor: window.get_monitor(), updated: new Date().toISOString(),
                };
                this._saveGeometry();
                this._log(`saved (pre-unmanage): x=${this._geometry.x} y=${this._geometry.y} width=${this._geometry.width} height=${this._geometry.height}`);
            }
            info.unmanaged = true;
            for (const id of info.signals) { try { window.disconnect(id); } catch (_) {} }
            for (const source of info.restoreSources) if (source) GLib.source_remove(source);
            this._tracked.delete(window);
            // The replacement Meta.Window will restore from this committed frame.
        }));

        if (this._geometry && this._validGeometry(this._geometry)) {
            for (const delay of RESTORE_DELAYS) {
                const source = GLib.timeout_add(GLib.PRIORITY_DEFAULT, delay, () => {
                    const index = info.restoreSources.indexOf(source);
                    if (index >= 0) info.restoreSources.splice(index, 1);
                    if (!info.unmanaged) this._restorePosition(window, info, delay === RESTORE_DELAYS.at(-1));
                    return GLib.SOURCE_REMOVE;
                });
                info.restoreSources.push(source);
            }
        } else {
            // First run: wait until the mapped frame is stable, then record it.
            const source = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1300, () => {
                if (!info.unmanaged) {
                    this._capturePosition(window, 'initial-frame');
                    info.ready = true;
                    info.restoring = false;
                }
                return GLib.SOURCE_REMOVE;
            });
            info.restoreSources.push(source);
        }
    }

    _validGeometry(g) {
        return g && Number.isFinite(g.x) && Number.isFinite(g.y) &&
            Number.isFinite(g.width) && Number.isFinite(g.height) && g.width >= 80 && g.height >= 60;
    }

    _restorePosition(window, info, finalAttempt) {
        const g = this._geometry;
        if (!this._validGeometry(g) || info.unmanaged) return;
        try {
            info.restoring = true;
            // Crucial: only move the frame. GTK owns client size; changing Mutter's
            // frame size here caused decoration-dependent height jumps and drift.
            this._log(`applying position only (non-user move) x=${g.x} y=${g.y}`);
            window.move_frame(false, Math.round(g.x), Math.round(g.y));
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, 180, () => {
                if (info.unmanaged) return GLib.SOURCE_REMOVE;
                const actual = window.get_frame_rect();
                this._log(`position check: target x=${g.x} y=${g.y}; actual x=${actual.x} y=${actual.y}; size=${actual.width}x${actual.height}`);
                if (finalAttempt) {
                    info.restoring = false;
                    info.ready = true;
                    this._capturePosition(window, 'post-restore');
                }
                return GLib.SOURCE_REMOVE;
            });
        } catch (e) {
            info.restoring = false;
            this._log(`position restore failed: ${e}`);
        }
    }

    _capturePosition(window, reason) {
        try {
            const rect = window.get_frame_rect();
            if (!rect || rect.width < 80 || rect.height < 60) {
                this._log(`capture skipped (${reason}): invalid frame`);
                return;
            }
            this._geometry = {
                x: Math.round(rect.x), y: Math.round(rect.y),
                width: Math.round(rect.width), height: Math.round(rect.height),
                monitor: window.get_monitor(), updated: new Date().toISOString(),
            };
            this._saveGeometry();
            this._log(`saved (${reason}): x=${this._geometry.x} y=${this._geometry.y} width=${this._geometry.width} height=${this._geometry.height}`);
        } catch (e) { this._log(`capture failed (${reason}): ${e}`); }
    }

    _loadGeometry() {
        try {
            const [ok, bytes] = this._file.load_contents(null);
            if (ok) {
                const g = JSON.parse(new TextDecoder().decode(bytes));
                if (this._validGeometry(g)) {
                    this._log(`loaded geometry: x=${g.x} y=${g.y} width=${g.width} height=${g.height}`);
                    return g;
                }
            }
        } catch (e) { this._log(`no readable geometry file: ${e.message || e}`); }
        return null;
    }

    _saveGeometry() {
        if (!this._validGeometry(this._geometry)) return;
        try {
            const parent = this._file.get_parent();
            if (!parent.query_exists(null)) parent.make_directory_with_parents(null);
            this._file.replace_contents(JSON.stringify(this._geometry, null, 2), null, false, Gio.FileCreateFlags.REPLACE_DESTINATION, null);
        } catch (e) { this._log(`save failed: ${e}`); }
    }
}
