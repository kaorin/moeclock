#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Rsvg', '2.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf
from gi.repository import Rsvg

# GTK 3 on Wayland derives the xdg_toplevel app_id from the GLib
# program name. It must match the desktop-file basename: moeclock.desktop.
# Set it before creating any Gtk.Window (the legacy app uses Gtk.Builder).
GLib.set_prgname("moeclock")

# Keep the X11 class for sessions running through XWayland.
try:
    Gdk.set_program_class("MoeClock")
except Exception:
    pass
#import gnome.ui
import os
from os.path import abspath, dirname, join
import random
import logging
import logging.config
import traceback
from xml.dom import minidom
import base64
import codecs
import subprocess
import datetime
import cairo
import gettext
import locale
import gc
import json
import math
import ast
import shlex

WALLPAPER_PATH = "/home/kaoru/themes/BackGround/used-wallpaper"
__VERSION__="1.5.2.26"
NAME="moeclock"
APP = 'moeclock'
WHERE_AM_I = abspath(dirname(__file__))
LOCALE_DIR = join(WHERE_AM_I, 'locale')

SOUND_PLAY="paplay"

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    # Minimal installations may not have an en_US locale generated.
    pass
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

print('Using locale directory: {}'.format(LOCALE_DIR))

WEEKString=[ _('(Mon)'), _('(Tue)'), _('(Wed)'), _('(Thu)'), _('(Fri)'), _('(Sat)'), _('(Sun)'),]


def parse_color(value):
    """Parse a CSS-style color string into a Gdk.RGBA value."""
    rgba = Gdk.RGBA()
    if not rgba.parse(value):
        rgba.parse("#f366ff")
    return rgba

class ConfigXML:
    '''
    設定ファイル入出力クラス
    ConfigPathで指定されたファイルを読み込む
    '''
    OptionList = {  "x_pos":"0",
                    "y_pos":"0",
                    "x_size":"320",
                    "y_size":"200",
                    "wallpaper_path":"/usr/share/backgrounds",
                    "use_wallpaper":"",
                    "font":"Takao-Pゴシック-Regular",
                    "color":"#f366ff",
                    "notice":"True",
                    "alwaysTop":"False",
                    "weekOffset":"-10",
                    "skin": os.path.dirname(os.path.abspath(__file__)) + "/default",
                    "sound": os.path.dirname(os.path.abspath(__file__)) + "/sound.wav",
                    "windowDecorate":"True",
                    "annotationType":"0",
                    "soundCutOut":"False",
                    "calloutSize":"100%",
                    "drawFrame":"False",
                    "lineWidth":"4",
                    "round":"12",
                    "roundWindow":"False"}
    AppName = "moeclock"
    ConfigPath = os.path.join(".config", "moeclock.xml")
    Options = {}    #オプション値の辞書
    domobj = None

    def __init__(self, read):
        '''
        初期化
        read：設定ファイル読み込みフラグ　True=読み込み/False=初期化のみ
        '''
        #print "ConfigXML"
        if read == True :
            try:
                config_file = os.path.join(os.path.expanduser("~"), self.ConfigPath)
                self.domobj = minidom.parse(config_file)
                options = self.domobj.getElementsByTagName("options")
                for opt in options :
                    for op,defVal in self.OptionList.items():
                        elm = opt.getElementsByTagName(op)
                        if len(elm) > 0 :
                            self.Options[op] = self.getText(elm[0].childNodes)
                        else:
                            self.Options[op] = defVal
            except:
                for op,defVal in self.OptionList.items():
                    self.Options[op] = defVal

    def getText(self,nodelist):
        '''
        設定ファイルから文字列取得
        '''
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                text = str(node.data)
                text = text.rstrip(" \t\n")
                text = text.lstrip(" \t\n")
                rc = rc + text
        return rc

    def GetOption(self, optName ):
        '''
        設定取得
        optName：設定キー
        '''
        if optName == "password":
            return str(base64.b64decode(self.Options[optName]))
        else:
            try:
                return str(self.Options[optName])
            except:
                return str(self.OptionList[optName])

    def SetOption(self, optName, value ):
        '''
        設定値設定
        optName：設定キー
        value：設定値
        '''
        if optName == "password":
            val = base64.b64encode(value)
            self.Options[optName] = val
        else:
            self.Options[optName] = value

    def Write(self):
        '''
        設定ファイル書き込み
        '''
        try:
            impl = minidom.getDOMImplementation()
            newdoc = impl.createDocument(None, self.AppName, None)
            root = newdoc.documentElement
            opts = newdoc.createElement("options")
            root.appendChild(opts)
            for op in self.OptionList.keys():
                opt = newdoc.createElement(op)
                opts.appendChild(opt)
                text = newdoc.createTextNode(str(self.Options[op]))
                opt.appendChild(text)
            config_file = os.path.join(os.path.expanduser("~"), self.ConfigPath)
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with codecs.open(config_file, 'w', encoding='utf-8') as file:
                newdoc.writexml(file, '', '\t', '\n', encoding='utf-8')
        except:
            logging.error(traceback.format_exc())

class moeclock:
    '''
    萌え時計クラス
    '''
    wallpaper_list = []
    wlist = []
    sw = 0
    use_wallpaper_list = []
    #timeout_interval = 10
    timeout_interval = 1
    min = -1
    pixbuf2 = None
    userResize = True
    iconifed = False
    noticeFlag = True
    notice = True
    defaultHeaderBar = None
    customHeaderBar = None
    eventCancel = False

    def __init__(self):
        '''
        コンストラクタ
        '''
        logging.debug("__init__")
        #オプションを読み込み
        global WALLPAPER_PATH
        conf = ConfigXML(True)
        WALLPAPER_PATH = conf.GetOption("wallpaper_path")
        uselist = conf.GetOption("use_wallpaper")
        self.font =  conf.GetOption("font")
        self.color = conf.GetOption("color")
        def config_value(value, default):
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError, TypeError):
                return default

        self.notice = config_value(conf.GetOption("notice"), True)
        self.alwaysTop = config_value(conf.GetOption("alwaysTop"), False)
        self.weekOffset = config_value(conf.GetOption("weekOffset"), -10)
        self.skin = conf.GetOption("skin")
        # Migrate old installations that stored resources under /usr/share/moeclock.
        if not os.path.isdir(self.skin):
            self.skin = join(WHERE_AM_I, "default")
        self.windowDecorate = config_value(conf.GetOption("windowDecorate"), True)
        self.annotationType = config_value(conf.GetOption("annotationType"), 0)
        self.soundCutOut = config_value(conf.GetOption("soundCutOut"), False)
        self.sound = conf.GetOption("sound")
        if not os.path.isfile(self.sound):
            self.sound = join(WHERE_AM_I, "sound.wav")
        self.calloutSize = conf.GetOption("calloutSize")
        self.drawFrame = config_value(conf.GetOption("drawFrame"), False)
        self.roundWindow = config_value(conf.GetOption("roundWindow"), False)
        if uselist:
            self.use_wallpaper_list = config_value(uselist, [])
        path = self.skin + '/style.css'
        if os.path.exists(path) == True:
            self.set_style()
        #メインウィンドウを作成
        self.wMain = Gtk.Builder()
        self.wMain.set_translation_domain(APP)
        self.wMain.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/moeclock.glade")
        #Create our dictionay and connect it
        dicMain = { "on_Main_button_press_event" : self.showMenu,
                    "on_miSetting_activate" : self.properties,
                    "on_miExit_activate" : self.on_quit,
                    "on_miInfo_activate" : self.showAboutDialog,
                    "on_miNotice_toggled" : self.on_miNotice_toggled,
                    "on_miTop_toggled" : self.on_miTop_toggled,
                    "on_miDecorate_toggled" : self.on_miDecorate_toggled,
                    "on_miMicro_activate" : self.on_miMicro_activate,
                    "on_miSmall_activate" : self.on_miSmall_activate,
                    "on_miMidium_activate" : self.on_miMidium_activate,
                    "on_miLarge_activate" : self.on_miLarge_activate,
                    "on_miBig_activate" : self.on_miBig_activate,
                    "on_miTopLeft_activate" : self.on_miTopLeft_activate,
                    "on_miTopRight_activate" : self.on_miTopRight_activate,
                    "on_miBottomLeft_activate" : self.on_miBottomLeft_activate,
                    "on_miBottomRight_activate" : self.on_miBottomRight_activate,
                    "on_miRemovePrefix_activate" : self.on_miRemovePrefix_activate,
                    "on_mi100_activate" : self.on_miCalloutSize_activate,
                    "on_mi110_activate" : self.on_miCalloutSize_activate,
                    "on_mi120_activate" : self.on_miCalloutSize_activate,
                    "on_mi130_activate" : self.on_miCalloutSize_activate,
                    "on_mi140_activate" : self.on_miCalloutSize_activate,
                    "on_mi150_activate" : self.on_miCalloutSize_activate,
                    "on_daPict_draw" : self.on_daPict_draw,
                    "on_Main_size_allocate" : self.on_Main_size_allocate,
                    "on_Main_window_state_event" : self.on_Main_window_state_event,
                    "on_Main_focus_in_event" : self.on_Main_focus_in_event,
                    "on_Main_focus_out_event" : self.on_Main_focus_out_event,
                    "on_Main_configure_event" : self.on_Main_configure_event,
                    "on_Main_destroy" : self.on_quit }
        self.wMain.connect_signals(dicMain)
        self.context_menu =  self.wMain.get_object ("mainMenu")
        mainWindow = self.wMain.get_object("Main")
        # Draw the shadow on a dedicated transparent canvas. GTK CSS box-shadow
        # on a Wayland toplevel is clipped at the native surface boundary, so it
        # cannot create visible pixels outside the window. The outer canvas
        # reserves real transparent space around the wallpaper for Cairo shadow.
        self._shadow_padding = 14
        self._shadow_enabled = not self.windowDecorate
        self.shadowArea = self.wMain.get_object("shadowArea")
        self.daPict = self.wMain.get_object("daPict")
        # The wallpaper DrawingArea must not let GTK's default draw handler
        # repaint its background after our CLEAR + rounded-clip Cairo pass.
        # Otherwise the transparent corner mask can be filled back in.
        self.daPict.set_app_paintable(True)
        # Draw directly into the RGBA toplevel surface. A child GdkWindow
        # can use an opaque visual and defeat per-pixel alpha at rounded corners.
        self.daPict.set_has_window(False)
        # Keep the shadow canvas transparent and fully allocated behind the
        # wallpaper. Returning True from its draw handler prevents GTK's
        # default background rendering from painting over the Cairo shadow.
        self.shadowArea.set_app_paintable(True)
        self.shadowArea.set_hexpand(True)
        self.shadowArea.set_vexpand(True)
        self.daPict.set_halign(Gtk.Align.FILL)
        self.daPict.set_valign(Gtk.Align.FILL)
        self.shadowArea.connect("draw", self.on_shadowArea_draw)
        self._update_custom_shadow(mainWindow)
        # Request an RGBA visual before the toplevel is realized. This allows
        # Cairo to leave the rounded wallpaper corners genuinely transparent
        # instead of changing the native window shape (which is unreliable on
        # Wayland and can desynchronize the image and client-area dimensions).
        try:
            screen = mainWindow.get_screen()
            rgba_visual = screen.get_rgba_visual() if screen is not None else None
            if rgba_visual is not None:
                mainWindow.set_visual(rgba_visual)
                mainWindow.set_app_paintable(True)
                self._rgba_visual_enabled = True
            else:
                self._rgba_visual_enabled = False
                logging.warning("RGBA visualを取得できません。角丸の透明表示は制限される場合があります")
        except Exception:
            self._rgba_visual_enabled = False
            logging.exception("RGBA visualの設定に失敗しました")
        # Set a stable X11/GTK WM_CLASS for desktop-shell icon matching.
        try:
            mainWindow.set_wmclass("moeclock", "MoeClock")
        except Exception:
            pass
        # Keep the running application visible in the desktop taskbar/dock.
        # The previous code hid the window from the taskbar in its normal state.
        mainWindow.set_skip_taskbar_hint(False)
        icon_path = join(WHERE_AM_I, "moeclock.png")
        if os.path.isfile(icon_path):
            try:
                mainWindow.set_icon_from_file(icon_path)
            except Exception as exc:
                logging.warning("アプリケーションアイコンを設定できません: %s", exc)
        miNotice = self.wMain.get_object("miNotice")
        miNotice.set_active(self.notice)
        miTop = self.wMain.get_object("miTop")
        miTop.set_active(self.alwaysTop)
        miDecorate = self.wMain.get_object("miDecorate")
        miDecorate.set_active(self.windowDecorate)
        mainWindow.set_decorated(self.windowDecorate)
        xpos = conf.GetOption("x_pos")
        ypos = conf.GetOption("y_pos")
        xsize = conf.GetOption("x_size")
        ysize = conf.GetOption("y_size")
        # Wayland does not expose global window coordinates to GTK clients.
        # The companion GNOME Shell extension restores the frame geometry.
        _display = Gdk.Display.get_default()
        _is_wayland = bool(_display and "wayland" in _display.get_name().lower())
        if not _is_wayland:
            mainWindow.move(int(xpos), int(ypos))
        if int(xsize) > 10 and int(ysize) > 10 :
            self.userResize = False
        _pad = self._shadow_padding if self._shadow_enabled else 0
        mainWindow.resize(int(xsize) + 2 * _pad, int(ysize) + 2 * _pad)
        mainWindow.set_keep_above(self.alwaysTop)
        #ダイアログを作成
        self.wTree = Gtk.Builder()
        self.wTree.set_translation_domain(APP)
        self.wTree.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/moeclockdlg.glade")
        preferencesDialog = self.wTree.get_object('properties')
        self.selectedFolder = self.wTree.get_object("FS_FOLDER")
        #self.selectedFolder.set_filename(WALLPAPER_PATH+"/")
        self.selectedFolder.set_current_folder(WALLPAPER_PATH+"/")
        self.lscvType = self.wTree.get_object ("listStyle")
        self.colorSelect = self.wTree.get_object ("clrPicker")
        rgba = Gdk.RGBA()
        rgba.parse(self.color)
        self.colorSelect.set_rgba(rgba)
        # 吹出位置 
        # 右下：0
        # 右上：1
        # 左下：2
        # 左上：3
        self.cbCalloutPosition = self.wTree.get_object("cbCalloutPosition")
        self.cbCalloutPosition.set_active_id(str(self.annotationType))
        self.fontSelect = self.wTree.get_object ("fntSelect")
        self.fontSelect.set_font(self.font)
        self.fontSelect.set_show_size(False)
        self.fontSelect.set_show_style(False)
        self.sbWeekOffset = self.wTree.get_object("sbWeekOffset")
        self.sbWeekOffset.set_value(self.weekOffset)
        self.fcSkin = self.wTree.get_object ("fcSkin")
        self.fcSkin.set_filename(self.skin+"/")
        self.fcSkin.set_current_folder(self.skin+"/")
        self.fcSound = self.wTree.get_object ("fcSound")
        self.fcSound.set_filename(self.sound)
        self.cbSoundCutOut = self.wTree.get_object ("cbSoundCutOut")
        self.cbSoundCutOut.set_active(self.soundCutOut)
        self.sclCalloutSize = self.wTree.get_object ("sclCalloutSize")
        self.sclCalloutSize.set_value(float(self.calloutSize.replace("%","")))
        self.cbDrawFrame = self.wTree.get_object ("cbDrawFrame")
        self.cbDrawFrame.set_active(self.drawFrame)
        self.lineWidth = float(conf.GetOption("lineWidth"))
        self.sclLineWidth = self.wTree.get_object ("sclLineWidth")
        self.sclLineWidth.set_value(self.lineWidth)
        self.round = float(conf.GetOption("round"))
        self.sclRound = self.wTree.get_object ("sclRound")
        self.sclRound.set_value(self.round)
        self.cbRoundWindow = self.wTree.get_object ("cbRoundWindow")
        self.cbRoundWindow.set_active(self.roundWindow)
        #フィルタの作成
        self.allFilter = Gtk.FileFilter()
        self.waveFilter = Gtk.FileFilter()

        self.allFilter.set_name(_("All Files"))
        self.allFilter.add_pattern("*")

        self.waveFilter.set_name(_("Sound Files"))
        self.waveFilter.add_pattern("*.wav")

        self.fcSound.add_filter(self.waveFilter)
        self.fcSound.add_filter(self.allFilter)
        self.fcSound.set_filter(self.waveFilter)
        self.cbCalloutPosition.set_active_id(str(self.annotationType))
        self.preferences = preferencesDialog
        #Create our dictionay and connect it
        dic = { "on_BTN_OK_clicked" : self.on_BTN_OK_clicked,
                "on_BTN_CANCEL_clicked" : self.on_BTN_CANCEL_clicked,
                "on_btnPlay_clicked" : self.on_btnPlay_clicked,
                "on_properties_delete_event" : self.on_properties_delete_event,
                "on_fcSkin_file_set" : self.on_fcSkin_file_set,
                "on_cbSoundCutOut_toggled": self.on_cbSoundCutOut_toggled
        }
        self.wTree.connect_signals(dic)
        #壁紙一覧を作成
        if os.path.isdir(WALLPAPER_PATH) == False:
            WALLPAPER_PATH = "/usr/share/backgrounds"
        for base, path, imPath in os.walk(WALLPAPER_PATH+"/"):
            for img in imPath:
                limg = img.lower()
                if limg.find("jpg") > 0 or limg.find("png") > 0 or limg.find("jpeg") > 0:
                    if base[-1] != '/' :
                        self.wallpaper_list.append(base+"/"+img)
                    else:
                        self.wallpaper_list.append(base+img)
        #tmplist = os.listdir(WALLPAPER_PATH+"/")
        #self.wallpaper_list = [ WALLPAPER_PATH+"/" +x for x in tmplist if x.find(".jpg") >= 0 or x.find(".JPG") >= 0 or x.find(".png") >= 0 or x.find(".PNG") >= 0]
        logging.debug(str(self.wallpaper_list))
        self.timeout = GLib.timeout_add_seconds(int(self.timeout_interval),self.timeout_callback,self)
        # Show only after the RGBA visual has been selected for the toplevel.
        mainWindow.show_all()

    def __getitem__(self, key):
        return self.wTree.get_object (key)

    def on_BTN_OK_clicked(self,widget):
        '''
        設定ダイアログOKボタンハンドラ
        '''
        global WALLPAPER_PATH
        WALLPAPER_PATH = self.selectedFolder.get_filename()
        print (WALLPAPER_PATH)
        tmp = self.fontSelect.get_font().split(' ')
        if len(tmp) > 1:
            tmp = tmp[:-1]
        self.font = ' '.join(tmp)
        print ("font:"+self.font)
        self.color = "#%02X%02X%02X" % (int(self.colorSelect.get_rgba().red * 255),int(self.colorSelect.get_rgba().green * 255),int(self.colorSelect.get_rgba().blue * 255))
        self.weekOffset = self.sbWeekOffset.get_value_as_int()
        soundFile = self.fcSound.get_filename()
        if len(soundFile) > 0:
            self.sound = soundFile
        self.skin = self.fcSkin.get_filename()
        self.calloutSize = str(self.sclCalloutSize.get_value()) + "%"
        self.drawFrame = self.cbDrawFrame.get_active()
        self.lineWidth = self.sclLineWidth.get_value()
        self.round = self.sclRound.get_value()
        self.roundWindow = self.cbRoundWindow.get_active()
        self.annotationType = int(self.cbCalloutPosition.get_active_id())
        self._saveConf()
        self.preferences.hide()
        GLib.source_remove(self.timeout)
        self._buildWallPaper(self.wlist[self.sw])
        self._setWallpaper("/tmp/moeclock.png")
        self.timeout = GLib.timeout_add_seconds(int(self.timeout_interval),self.timeout_callback,self)

    def on_BTN_CANCEL_clicked(self,widget):
        '''
        設定ダイアログキャンセルボタンハンドラ
        '''
        self.selectedFolder.set_filename(WALLPAPER_PATH+"/")
        self.preferences.hide()

    def on_btnPlay_clicked(self,widget):
        '''
        設定ダイアログ
        音声再生ボタン
        '''
        if self.soundCutOut:
            # 先頭がカットされる場合S/PDIF等
            # 一度無音の音声ファイルを再生する
            soundPath = os.path.join(WHERE_AM_I, "sound", "nosound.wav")
            if not os.path.exists(soundPath):
                soundPath = "/usr/share/moeclock/sound/nosound.wav"
            if os.path.exists(soundPath):
                self.execCommand([SOUND_PLAY, soundPath])
        if os.path.exists(self.sound) :
            soundFile = self.fcSound.get_filename()
            if soundFile:
                self.execCommand([SOUND_PLAY, soundFile])

    def on_fcSkin_file_set(self,widget):
        '''
        スキン選択
        '''
        skin = self.fcSkin.get_filename()
        if os.path.exists(skin + "/color_setting.txt") :
            for line in open(skin + "/color_setting.txt", 'r'):
                line = line.strip('\n')
                if len(line) > 0:
                    self.colorSelect.set_rgba(parse_color(line))

    def on_cbSoundCutOut_toggled(self, wiget):
        '''
        音声の先頭が切れる場合の対応を行うかどうか
        '''
        self.soundCutOut = self.cbSoundCutOut.get_active()

    def on_properties_delete_event(self,widget,event):
        widget.hide()
        return True

    def on_daPict_draw(self, widget, cr, event=None):
        """Draw the wallpaper with alpha-transparent rounded corners."""
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        if width <= 0 or height <= 0:
            return False

        # Always clear the drawing area to transparent. With roundWindow off,
        # the complete rectangular wallpaper is then painted over it.
        cr.save()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        if self.roundWindow:
            radius = max(0.0, min(float(self.round), width / 2.0, height / 2.0))
            # Build a single closed rounded-rectangle path. The legacy
            # roundedrec() helper starts an extra sub-path at (x, y), which
            # is suitable for stroking but can corrupt a fill/clip mask.
            x0, y0 = 0.0, 0.0
            x1, y1 = float(width), float(height)
            r = radius
            cr.new_sub_path()
            cr.arc(x1-r, y0+r, r, -math.pi/2.0, 0.0)
            cr.arc(x1-r, y1-r, r, 0.0, math.pi/2.0)
            cr.arc(x0+r, y1-r, r, math.pi/2.0, math.pi)
            cr.arc(x0+r, y0+r, r, math.pi, 3.0*math.pi/2.0)
            cr.close_path()
            cr.clip()

        if self.pixbuf2:
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf2, 0, 0)
            cr.paint()
            self.userResize = True

        # Draw the configurable frame LAST, above the wallpaper and shadow
        # layers. Previously the frame was baked into the generated wallpaper
        # pixbuf and could be covered/replaced during redraws and rounded-mask
        # clipping. Keep the stroke inside the allocation so it is not clipped.
        if self.drawFrame:
            line_width = max(0.5, float(self.lineWidth))
            inset = line_width / 2.0 + 0.5
            x0, y0 = inset, inset
            x1, y1 = float(width) - inset, float(height) - inset
            radius = max(0.0, min(float(self.round), (x1-x0)/2.0, (y1-y0)/2.0))
            col = parse_color(self.color)
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.set_source_rgb(col.red, col.green, col.blue)
            cr.set_line_width(line_width)
            cr.new_sub_path()
            cr.arc(x1-radius, y0+radius, radius, -math.pi/2.0, 0.0)
            cr.arc(x1-radius, y1-radius, radius, 0.0, math.pi/2.0)
            cr.arc(x0+radius, y1-radius, radius, math.pi/2.0, math.pi)
            cr.arc(x0+radius, y0+radius, radius, math.pi, 3.0*math.pi/2.0)
            cr.close_path()
            cr.stroke()
        cr.restore()
        # We fully handled this DrawingArea.  Stop GTK's default draw handler
        # from painting an opaque style background over the transparent mask.
        return True

    def _setWallpaper(self, WallpaperLocation):
        """Load and size the wallpaper; drawing is performed by GTK's draw signal."""
        try:
            mainWindow = self.wMain.get_object("Main")
            pict = self.wMain.get_object("daPict")
            window_width, window_height = mainWindow.get_size()
            pad = self._shadow_padding if self._shadow_enabled else 0
            xsize = max(1, window_width - 2 * pad)
            ysize = max(1, window_height - 2 * pad)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(WallpaperLocation)
            source_width = float(pixbuf.get_width())
            source_height = float(pixbuf.get_height())
            aspect = source_height / source_width
            target_width = max(1, int(xsize))
            target_height = max(1, int(target_width * aspect))
            self.pixbuf2 = pixbuf.scale_simple(target_width, target_height, GdkPixbuf.InterpType.BILINEAR)
            self.userResize = False
            target_window_width = target_width + 2 * pad
            target_window_height = target_height + 2 * pad
            if (window_width, window_height) != (target_window_width, target_window_height):
                mainWindow.resize(target_window_width, target_window_height)
            # Queue after resize so the clip uses the actual DrawingArea size.
            pict.queue_draw()
            del pixbuf
            gc.collect()
            return True
        except Exception as e:
            logging.exception("壁紙の設定に失敗しました: %s", e)
            return False

    def _changeWallPaper(self):
        '''
        壁紙切り替え
        一度使用した壁紙が表示されないようにフラグ管理を行っている
        '''
        self.wlist = self.wallpaper_list
        if len(self.use_wallpaper_list) > 0:
            chkSet = set(self.use_wallpaper_list)
            self.wlist = [x for x in self.wallpaper_list if x not in chkSet]
            #print (str(len(wlist)))
            if len(self.wlist) == 0:
                self.use_wallpaper_list = []
                self.wlist = self.wallpaper_list
        #print (wlist)
        flag = False
        while(flag == False):
            self.sw = random.randint(0,len(self.wlist)-1)
            #print (str(sw) +";" +wlist[sw])
            self.use_wallpaper_list.append(self.wlist[self.sw])
            self._buildWallPaper(self.wlist[self.sw])
            flag = self._setWallpaper("/tmp/moeclock.png")
        self._saveConf()

    def _saveConf(self):
        '''
        設定保存
        操作等で変更された設定を保存する
        '''
        #変更結果を保存
        mainWindow = self.wMain.get_object("Main")
        global WALLPAPER_PATH
        conf = ConfigXML(False)
        conf.SetOption("wallpaper_path",WALLPAPER_PATH)
        conf.SetOption("use_wallpaper",str(self.use_wallpaper_list))
        conf.SetOption("font",self.font)
        conf.SetOption("color",self.color)
        conf.SetOption("notice",str(self.notice))
        conf.SetOption("alwaysTop",str(self.alwaysTop))
        (xsize, ysize) = mainWindow.get_size()
        _save_pad = self._shadow_padding if self._shadow_enabled else 0
        xsize = max(1, xsize - 2 * _save_pad)
        ysize = max(1, ysize - 2 * _save_pad)
        _display = Gdk.Display.get_default()
        _is_wayland = bool(_display and "wayland" in _display.get_name().lower())
        # Do not overwrite the last valid coordinates with Wayland's placeholder
        # (often 0,0). GNOME Shell companion extension owns Wayland geometry.
        if not _is_wayland:
            xpos, ypos = mainWindow.get_position()
            conf.SetOption("x_pos", xpos)
            conf.SetOption("y_pos", ypos)
        conf.SetOption("x_size",xsize)
        conf.SetOption("y_size",ysize)
        conf.SetOption("weekOffset",self.weekOffset)
        conf.SetOption("sound",self.sound)
        conf.SetOption("skin",self.skin)
        conf.SetOption("windowDecorate", self.windowDecorate)
        conf.SetOption("annotationType", self.annotationType)
        conf.SetOption("soundCutOut", self.soundCutOut)
        conf.SetOption("calloutSize", self.calloutSize)
        conf.SetOption("drawFrame",self.drawFrame)
        conf.SetOption("lineWidth",self.lineWidth)
        conf.SetOption("round",self.round)
        conf.SetOption("roundWindow",self.roundWindow)
        conf.Write()

    def showMenu(self,widget, event):
        '''
        ポップアップメニュー表示
        右クリックでメニュー表示
        左クリックで壁紙切り替え
        '''
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            #右クリック
            self.context_menu.popup(None, None, None,None, event.button, event.time)
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            #左クリック
            self._changeWallPaper()

    def on_quit(self,widget):
        '''
        アプリケーション終了
        '''
        self._saveConf()
        Gtk.main_quit()

    def on_miNotice_toggled(self,widget):
        '''
        時報切り替え
        '''
        self.notice = widget.get_active()

    def on_miTop_toggled(self,widget):
        '''
        常に前面に表示切り替え
        '''
        self.alwaysTop = widget.get_active()
        mainWindow = self.wMain.get_object("Main")
        mainWindow.set_keep_above(self.alwaysTop)

    def _update_custom_shadow(self, mainWindow=None):
        """Reserve transparent outer padding and redraw the custom Cairo shadow."""
        try:
            if mainWindow is None:
                mainWindow = self.wMain.get_object("Main")
            self._shadow_enabled = not self.windowDecorate
            pad = self._shadow_padding if self._shadow_enabled else 0
            pict = self.wMain.get_object("daPict")
            pict.set_margin_start(pad)
            pict.set_margin_end(pad)
            pict.set_margin_top(pad)
            pict.set_margin_bottom(pad)
            if hasattr(self, "shadowArea"):
                self.shadowArea.queue_draw()
            pict.queue_draw()
        except Exception:
            logging.exception("独自ウィンドウ影の更新に失敗しました")

    def on_shadowArea_draw(self, widget, cr):
        """Draw a soft, GNOME-like drop shadow behind the wallpaper.

        The shadow is made from nested filled rounded rectangles, not stroked
        outlines.  This avoids the dark hairline seen in the previous build
        and produces a smooth falloff similar to Mutter's normal window shadow.
        The GtkOverlay paints the wallpaper above this canvas, hiding the
        inner part of the shadow while the RGBA margins remain transparent.
        """
        if not self._shadow_enabled:
            cr.save()
            cr.set_operator(cairo.OPERATOR_CLEAR)
            cr.paint()
            cr.restore()
            return True

        width = float(widget.get_allocated_width())
        height = float(widget.get_allocated_height())
        pad = float(self._shadow_padding)
        image_w = max(1.0, width - 2.0 * pad)
        image_h = max(1.0, height - 2.0 * pad)
        radius = float(getattr(self, "round", 10) if self.roundWindow else 3)
        radius = max(1.0, min(radius, image_w / 2.0, image_h / 2.0))

        cr.save()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.set_antialias(cairo.ANTIALIAS_BEST)

        # Build a gradual alpha falloff.  Large, very faint silhouettes form
        # the diffuse outer halo; smaller silhouettes deepen only near the
        # wallpaper edge.  A slight downward offset mimics a natural desktop
        # window shadow without creating a hard black border.
        layers = 40
        max_spread = max(1.0, pad - 1.0)
        for i in range(layers, 0, -1):
            t = float(i) / float(layers)  # 1 at outer edge, 0 near image edge
            spread = t * max_spread
            alpha = 0.0060 + (1.0 - t) * 0.0200
            x = pad - spread
            y = pad + 4.0 - spread
            w = image_w + 2.0 * spread
            h = image_h + 2.0 * spread
            r = min(radius + spread, w / 2.0, h / 2.0)
            self.roundedrec(cr, x, y, w, h, r, 1, False)
            cr.close_path()
            cr.set_source_rgba(0.0, 0.0, 0.0, alpha)
            cr.fill()

        cr.restore()
        return True

    def on_miDecorate_toggled(self, widget):
        """タイトルバー（ウィンドウ装飾）の表示を切り替える。

        Waylandでは、表示済みGtkWindowに対するset_decorated()の変更が
        コンポジターへ反映されないことがある。いったんunrealizeしてから
        装飾状態を設定し直し、新しいsurfaceとして表示する。
        """
        previous_decorated = self.windowDecorate
        previous_pad = 0 if previous_decorated else self._shadow_padding
        self.windowDecorate = widget.get_active()
        mainWindow = self.wMain.get_object("Main")
        self._update_custom_shadow(mainWindow)

        # 初期化中（まだrealizeされていない状態）はプロパティだけ設定する。
        if not mainWindow.get_realized():
            mainWindow.set_decorated(self.windowDecorate)
            return

        width, height = mainWindow.get_size()
        image_width = max(1, width - 2 * previous_pad)
        image_height = max(1, height - 2 * previous_pad)
        was_visible = mainWindow.get_visible()

        # GTK/Wayland cannot reliably report a toplevel's global position:
        # get_position() commonly returns a stale/placeholder coordinate because
        # Wayland intentionally does not expose global window coordinates.
        # Reapplying that value after unmapping the window can make the compositor
        # put the window back at its previous placement. Only preserve coordinates
        # on X11, where they are meaningful. On Wayland, let the compositor retain
        # its own placement across the decoration-surface recreation.
        display = Gdk.Display.get_default()
        display_name = display.get_name().lower() if display is not None else ""
        is_wayland = "wayland" in display_name
        old_position = None if is_wayland else mainWindow.get_position()

        # Recreate the native surface so Wayland receives the new decoration mode.
        # Do not attempt to move the Wayland window here: GTK cannot provide a
        # reliable global position on Wayland. The GNOME Shell companion tracks
        # the replacement Meta.Window and reapplies the saved frame position.
        # Preserve the GTK client size across the surface recreation.
        mainWindow.hide()
        mainWindow.unrealize()
        mainWindow.set_decorated(self.windowDecorate)
        mainWindow.realize()
        new_pad = self._shadow_padding if self._shadow_enabled else 0
        mainWindow.resize(image_width + 2 * new_pad, image_height + 2 * new_pad)
        if old_position is not None:
            mainWindow.move(int(old_position[0]), int(old_position[1]))

        if was_visible:
            mainWindow.show_all()
        self._update_custom_shadow(mainWindow)
        mainWindow.queue_draw()
        GLib.idle_add(self._refreshWallpaperAfterDecoration)

    def _refreshWallpaperAfterDecoration(self):
        """再表示後に壁紙を描き直す。"""
        if hasattr(self, "pixbuf2") and self.pixbuf2 is not None:
            pict = self.wMain.get_object("daPict")
            if pict is not None:
                pict.queue_draw()
        return GLib.SOURCE_REMOVE
        
    def on_miMicro_activate(self,widget):
        '''
        表示サイズ変更：最小
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(280 + 2 * (self._shadow_padding if self._shadow_enabled else 0),88 + 2 * (self._shadow_padding if self._shadow_enabled else 0))
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miSmall_activate(self,widget):
        '''
        表示サイズ変更：小
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(320 + 2 * (self._shadow_padding if self._shadow_enabled else 0),180 + 2 * (self._shadow_padding if self._shadow_enabled else 0))
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miMidium_activate(self,widget):
        '''
        表示サイズ変更：中
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(400 + 2 * (self._shadow_padding if self._shadow_enabled else 0),225 + 2 * (self._shadow_padding if self._shadow_enabled else 0))
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miLarge_activate(self,widget):
        '''
        表示サイズ変更：大
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(480 + 2 * (self._shadow_padding if self._shadow_enabled else 0),270 + 2 * (self._shadow_padding if self._shadow_enabled else 0))
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miBig_activate(self,widget):
        '''
        表示サイズ変更：特大
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(640 + 2 * (self._shadow_padding if self._shadow_enabled else 0),360 + 2 * (self._shadow_padding if self._shadow_enabled else 0))
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miCalloutSize_activate(self, widget):
        '''
        吹き出しサイズ変更
        '''
        self.calloutSize = widget.get_child().get_text()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def checkPrefix(self, wallpaper):
        '''
        壁紙名にプレフィックスが存在するかどうかのチェック
        '''
        #ファイル名取得
        basename = os.path.basename(wallpaper)
        if basename.upper().find("--UL--") == 0:
            return True
        if basename.upper().find("--LL--") == 0:
            return True
        if basename.upper().find("--UR--") == 0:
            return True
        if basename.upper().find("--LR--") == 0:
            return True
        if basename.upper().find("--DR--") == 0:
            return True
        if basename.upper().find("--DL--") == 0:
            return True
        return False

    def tryIndex(self, l, x, default=False):
        return l.index(x) if x in l else default

    def renameWallpaper(self, wallpaper, type):
        '''
        壁紙に吹き出しプレフィックスを追加
        '''
        dirname, basename = os.path.split(wallpaper)
        if self.checkPrefix(basename):
            basename = basename[6:]
        # 吹出位置 
        # 右下：0
        # 右上：1
        # 左下：2
        # 左上：3
        if type == 3:
            basename = "--UL--" + basename
        if type == 2:
            basename = "--LL--" + basename
        if type == 1:
            basename = "--UR--" + basename
        if type == 0:
            basename = "--LR--" + basename
        path = os.path.join(dirname, basename)
        try:
            os.rename(wallpaper, path)
            self.wlist[self.sw] = path
            idx = self.tryIndex(self.use_wallpaper_list,wallpaper,-1)
            if idx >= 0:
                self.use_wallpaper_list[idx] = path
            idx = self.tryIndex(self.wallpaper_list,wallpaper,-1)
            if idx >= 0:
                self.wallpaper_list[idx] = path
        except Exception as e:
            error_dialog = Gtk.MessageDialog(
                type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                message_format=e)
            error_dialog.set_title(_('File Rename Error'))
            error_dialog.run()
            print(e)
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))
            error_dialog.destroy()

    def deletePrefixWallpaper(self, wallpaper):
        '''
        壁紙の吹き出しプレフィックスを削除
        '''
        dirname, basename = os.path.split(wallpaper)
        if self.checkPrefix(basename):
            basename = basename[6:]
            path = os.path.join(dirname, basename)
            os.rename(wallpaper, path)
            self.wlist[self.sw] = path
            idx = self.use_wallpaper_list.index(wallpaper)
            if idx >= 0:
                self.use_wallpaper_list[idx] = path
            idx = self.wallpaper_list.index(wallpaper)
            if idx >= 0:
                self.wallpaper_list[idx] = path

    def on_miRemovePrefix_activate(self,widget):
        '''
        プレフィックスを削除してデフォルト位置に吹き出し表示
        '''
        wallpaper = self.wlist[self.sw]
        self.deletePrefixWallpaper(wallpaper)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miTopLeft_activate(self,widget):
        '''
        吹き出し位置切り替え：左上
        '''
        if self.eventCancel:
            return
        # self.annotationType = 3
        wallpaper = self.wlist[self.sw]
        self.renameWallpaper(wallpaper, 3)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miTopRight_activate(self,widget):
        '''
        吹き出し位置切り替え：右上
        '''
        if self.eventCancel:
            return
        # self.annotationType = 1
        wallpaper = self.wlist[self.sw]
        self.renameWallpaper(wallpaper, 1)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miBottomLeft_activate(self,widget):
        '''
        吹き出し位置切り替え：左下
        '''
        if self.eventCancel:
            return
        # self.annotationType = 2
        wallpaper = self.wlist[self.sw]
        self.renameWallpaper(wallpaper, 2)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miBottomRight_activate(self,widget):
        '''
        吹き出し位置切り替え：右下
        '''
        if self.eventCancel:
            return
        # self.annotationType = 0
        wallpaper = self.wlist[self.sw]
        self.renameWallpaper(wallpaper, 0)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_Main_size_allocate(self,widget,event):
        '''
        画面サイズ変更イベント
        '''
        # GTK may emit size-allocate before the wallpaper list is initialized.
        # Ignore the event until a valid wallpaper selection is available.
        if not self.userResize:
            return
        if not getattr(self, "wlist", None):
            return
        if not isinstance(getattr(self, "sw", None), int):
            return
        if self.sw < 0 or self.sw >= len(self.wlist):
            return
        self._buildWallPaper(self.wlist[self.sw])
        self._setWallpaper("/tmp/moeclock.png")

    def on_Main_window_state_event(self, widget, event):
        '''
        画面状態変更イベント
        最小化した際にタスクバーに表示するかどうかの切り替え
        '''
        mainWindow = self.wMain.get_object("Main")
        if event.new_window_state & Gdk.WindowState.ICONIFIED:
            self.iconifed = True
        else:
            self.iconifed = False
        # Do not toggle skip_taskbar_hint here: the window must remain
        # represented in the desktop taskbar/dock while it is running.
        mainWindow.set_skip_taskbar_hint(False)

    def on_Main_focus_in_event(self,widget,event):
        '''
        フォーカス取得イベント
        '''
        #mainWindow = self.wMain.get_object("Main")
        # if mainWindow.get_decorated() == False:
        #     mainWindow.set_decorated(True)
        # mainWindow.set_titlebar = self.defaultHeaderBar

    def on_Main_focus_out_event(self,widget,event):
        '''
        フォーカス失効イベント
        '''
        #mainWindow = self.wMain.get_object("Main")
        # if self.windowDecorate == False:
            # mainWindow.set_decorated(False)
            # mainWindow.set_titlebar = self.customHeaderBar


    def on_Main_configure_event(self,widget,event):
        print (event)

    def showAboutDialog(self,*arguments, **keywords):
        '''
        このアプリについてダイアログ表示
        '''
        if os.path.exists("/usr/share/moeclock/moeclock.png") == True:
            imagePath = "/usr/share/moeclock/moeclock.png"
        elif os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/moeclock.png") == True:
            imagePath = os.path.dirname(os.path.abspath(__file__)) + "/moeclock.png"
        self.logo = Gtk.Image()
        self.logo.set_from_file(imagePath)
        self.logo_pixbuf = self.logo.get_pixbuf()
        about = Gtk.AboutDialog()
        # "萌え時計",VERSION,"MIT","1分ごとに画像を変更し時間を通知します。",["かおりん"],["かおりん"],"かおりん",self.logo_pixbuf
        about.set_program_name(_("Moe Clock"))
        about.set_version(__VERSION__)
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_license(
            "Program MIT License\nCopyright (c) 2019 Kaoru.Konno\n" + 
            _("Skin/Icon by TOY(http://moebuntu.web.fc2.com/) is licensed under a Creative Commons Attribution 3.0 Unported License.  \n") +
            _("Time signal audio file Copyright (c) 2011 Sachika.Souno All Rights Reserved. \n") + 
            _("* Modification of the time signal file and redistribution as a single unit are not permitted."))
        about.set_comments(_("Change the image every minute and notify the time."))
        about.set_authors([_("Kaorin@")])
        about.set_documenters([_("Kaorin@")])
        about.set_logo(self.logo_pixbuf)
        about.connect("response", self.on_about_close)
        about.show()

    # destroy the aboutdialog
    def on_about_close(self, action, parameter):
        action.destroy()
    
    def properties(self,widget):
        self.preferences.show()

    def timeout_callback(self,event):
        '''
        時計用タイムアウトイベント
        時刻表示/時報
        '''
        d = datetime.datetime.today()
        if self.min != d.minute:
            self._changeWallPaper()
        mainWindow = self.wMain.get_object("Main")
        if self.iconifed :
            dateStr = d.strftime(_("Moe Clock - %H:%M:%S"))
            mainWindow.set_title(dateStr)
        else:
            mainWindow.set_title(_("Moe Clock"))
        if self.notice :
            if d.minute == 0 and self.noticeFlag:
                if os.path.exists(self.sound) :
                   self.timeout3 = GLib.timeout_add(500,self.sound_callback,self)
                self.noticeFlag = False
            if d.minute > 0:
                self.noticeFlag = True
        return True

    def chanegSize_callback(self,event):
        '''
        画面サイズ変更タイムアウトイベント
        '''
        if len(self.wlist) > 0:
            self._buildWallPaper(self.wlist[self.sw])
            self._setWallpaper("/tmp/moeclock.png")

    def sound_callback(self,event):
        '''
        時報タイムアウトイベント
        '''
        if self.soundCutOut:
            # 先頭がカットされる場合S/PDIF等
            # 一度無音の音声ファイルを再生する
            soundPath = os.path.join(WHERE_AM_I, "sound", "nosound.wav")
            if not os.path.exists(soundPath):
                soundPath = "/usr/share/moeclock/sound/nosound.wav"
            if os.path.exists(soundPath):
                self.execCommand([SOUND_PLAY, soundPath])
        if os.path.isfile(self.sound):
            self.execCommand([SOUND_PLAY, self.sound])

    def _buildWallPaper(self,wallpaper):
        '''
        画像生成
        '''
        try:
            logging.debug("_buildWallPaper")
            logging.debug("wallpaper:"+wallpaper)
            print ("wallpaper:"+wallpaper)
            mainWindow = self.wMain.get_object("Main")
            (xsize,ysize) = mainWindow.get_size()
            #ファイル名取得
            basename = os.path.basename(wallpaper)
            #壁紙生成
            pixbufWall = GdkPixbuf.Pixbuf.new_from_file(wallpaper)
            x = float(pixbufWall.get_width())
            y = float(pixbufWall.get_height())
            aspect = y / x
            pixbufWall = pixbufWall.scale_simple(xsize, int(xsize*aspect),GdkPixbuf.InterpType.BILINEAR )
            #枠生成
            pixbufFrame = None
            path = self.skin + '/style.css'
            if os.path.exists(path) == True:
                self.set_style()
            elif self.drawFrame == False:
                path = self.skin + '/frame.png'
                if os.path.exists(path) == False:
                    path = os.path.dirname(os.path.abspath(__file__)) + "/" + self.skin + '/frame.png'
                pixbufFrame = GdkPixbuf.Pixbuf.new_from_file(path)
                pixbufFrame = pixbufFrame.scale_simple(xsize, int(xsize*aspect),GdkPixbuf.InterpType.BILINEAR )
            #吹き出し生成
            anoType = self.annotationType
            # 吹出位置 
            # 右下：0
            # 右上：1
            # 左下：2
            # 左上：3
            # ファイル名の先頭に特殊文字が含まれている場合、吹き出し位置を変更する
            if basename.upper().find("--UL--") == 0:
                anoType = 3
            if basename.upper().find("--LL--") == 0:
                anoType = 2
            if basename.upper().find("--UR--") == 0:
                anoType = 1
            if basename.upper().find("--LR--") == 0:
                anoType = 0
            path = self.skin + '/callout.json'
            if os.path.exists(path) == True:
                calloutJson = open(path,"r")
                jsonDic = json.load(calloutJson)
                anoType = jsonDic['callout_positon']
            path = self.skin + '/annotation.svg'
            if os.path.exists(path) == False:
                path = os.path.dirname(os.path.abspath(__file__)) + "/" + self.skin + '/annotation.svg'
            svg = Rsvg.Handle.new_from_file(path)
            # librsvg 2.52+ exposes intrinsic pixel dimensions through this API.
            if hasattr(svg, "get_intrinsic_size_in_pixels"):
                has_size, width, height = svg.get_intrinsic_size_in_pixels()
            else:
                has_size, width, height = False, 0, 0
            if not has_size:
                dimensions = svg.get_dimensions()
                width = dimensions.width
                height = dimensions.height
            # 吹き出し拡大
            scale = float(self.calloutSize.replace("%","")) / 100;
            ssvg = cairo.SVGSurface(None, width * scale, height * scale)
            s2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width * scale), int(height * scale))
            svgctx = cairo.Context(ssvg)
            svgctx.scale(scale, scale)
            if hasattr(svg, "render_document"):
                viewport = Rsvg.Rectangle()
                viewport.x = 0
                viewport.y = 0
                viewport.width = width
                viewport.height = height
                svg.render_document(svgctx, viewport)
            else:
                svg.render_cairo(svgctx)
            ctx = cairo.Context(s2)
            ctx.save()
            # if anoType == 0:
            #     ctx.scale(scale, scale)
            if anoType == 1:
                m = cairo.Matrix(yy=-1, y0=s2.get_height())
                ctx.transform(m)
            if anoType == 2:
                m = cairo.Matrix(xx=-1, x0=s2.get_width())
                ctx.transform(m)
            if anoType == 3:
                m = cairo.Matrix(yy=-1, xx=-1, x0=s2.get_width(),y0=s2.get_height())
                ctx.transform(m)

            ctx.set_source_surface(ssvg,0, 0)
            ctx.paint()
            ctx.restore()
            x1 = width * scale
            y1 = height * scale
            # 日付時刻描画
            d = datetime.datetime.today()
            yearStr = _('%s') % (d.year,)
            dateStr = d.strftime("%m/%d")
            timeStr = d.strftime("%H:%M")
            weekStr = WEEKString[d.weekday()]
            self.min = d.minute
            col = parse_color(self.color)
            ctx.set_source_rgb(col.red, col.green, col.blue)
            ctx.select_font_face(self.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            print (self.font)
            ctx.set_font_size(16 * scale)
            calloutXsize = 115
            calloutYsize = 100
            ofsX = x1 - calloutXsize * scale
            ofsY = y1 - calloutYsize * scale
            yearYofs = 15 * scale
            dateYofs = 35 * scale
            timeYofs = 60 * scale
            nowYOfs = 80 * scale
            if anoType == 1 or anoType == 3:
                ofsY = 15 * scale
            if anoType == 2 or anoType == 3:
                ofsX = -3 * scale
            # 年描画
            (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(yearStr)
            ctx.move_to(((calloutXsize * scale) - width)/2 + ofsX, yearYofs + ofsY)
            ctx.show_text(yearStr)
            # 月日描画
            (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(dateStr)
            ctx.move_to(((calloutXsize * scale) - width)/2 + ofsX, dateYofs + ofsY)
            ctx.show_text(dateStr)
            # 週描画
            ctx.set_font_size(10 * scale)
            ctx.move_to(((calloutXsize * scale) - width)/2 + ofsX + (self.weekOffset * scale) + width, dateYofs + ofsY)
            ctx.show_text(weekStr)
            # 時刻描画
            ctx.set_font_size(22 * scale)
            (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(timeStr)
            ctx.move_to(((calloutXsize * scale) - width)/2 + ofsX, timeYofs + ofsY)
            ctx.show_text(timeStr)
            # メッセージ描画
            ctx.set_font_size(15 * scale)
            if d.minute == 0:
                (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents("になったよ!")
                ctx.move_to(((calloutXsize * scale) - width)/2 + ofsX, nowYOfs + ofsY)
                ctx.show_text(_("Just Now!"))
            else:
                (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents("だよ!")
                ctx.move_to(((calloutXsize * scale) - width)/2 + ofsX, nowYOfs + ofsY)
                ctx.show_text(_("Now!"))

            #合成開始
            s1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbufWall.get_width(), pixbufWall.get_height())
            ctx = cairo.Context(s1)
            Gdk.cairo_set_source_pixbuf(ctx, pixbufWall, 0, 0)
            ctx.paint()
            s4 = None
            if pixbufFrame != None:
                s4 = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbufFrame.get_width(), pixbufFrame.get_height())
                ctx4 = cairo.Context(s4)
                Gdk.cairo_set_source_pixbuf(ctx4, pixbufFrame, 0, 0)
                ctx4.paint()

            path = self.skin + '/logo.png'
            if os.path.exists(path) == False:
                 path = os.path.dirname(os.path.abspath(__file__)) + "/" + self.skin + '/logo.png'
            s3 = cairo.ImageSurface.create_from_png(path)
            x3 = s3.get_width()
            y3 = s3.get_height()
            if anoType == 0:
                ctx.set_source_surface(s2,xsize-x1,(xsize*aspect)-y1)
            if anoType == 1:
                ctx.set_source_surface(s2,xsize-x1,0)
            if anoType == 2:
                ctx.set_source_surface(s2,0,(xsize*aspect)-y1)
            if anoType == 3:
                ctx.set_source_surface(s2,0,0)
            ctx.paint()
            if anoType == 2:
                ctx.set_source_surface(s3,xsize-x3,(xsize*aspect)-y3)
            else:
                ctx.set_source_surface(s3,0,(xsize*aspect)-y3)
            ctx.paint()
            if s4 != None:
                ctx.set_source_surface(s4,0,0)
                ctx.paint()
            # The frame is drawn in on_daPict_draw after the wallpaper pass.
            s1.write_to_png('/tmp/moeclock.png')
            del s1
            del s2
            del s3
            if s4 != None:
                del s4
            del pixbufWall
            del pixbufFrame
            gc.collect()
            return True
        except Exception as e:
            print(e)
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))
            # ファイルが壊れている場合があるので削除しておく
            try:
                os.remove('/tmp/moeclock.png')
            except OSError:
                pass
            return False

    def _applyWindowShape(self):
        """Compatibility hook: refresh Cairo alpha clipping instead of X11 shape."""
        try:
            pict = self.wMain.get_object("daPict")
            if pict is not None:
                pict.queue_draw()
        except Exception:
            logging.exception("角丸描画の更新に失敗しました")
        return GLib.SOURCE_REMOVE

    def execCommand(self,command):
        '''
        コマンド実行
        '''
        if isinstance(command, str):
            command = shlex.split(command)
        logging.debug("実行コマンド: %s", command)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        try:
            ret = subprocess.run(command, check=False)
        except FileNotFoundError:
            logging.error("コマンドが見つかりません: %s", command[0])
            return None
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        print (ret)             #実行結果のデバッグ用プリント
        return ret

    def roundedrec(self,context,x,y,w,h,r = 10,line_width = 4, border = True):
        "Draw a rounded rectangle"
        #   A****BQ
        #  H      C
        #  *      *
        #  G      D
        #   F****E
        context.set_line_width(line_width)
        context.move_to(x+r,y)                      # Move to A
        context.line_to(x+w-r,y)                    # Straight line to B
        context.curve_to(x+w,y,x+w,y,x+w,y+r)       # Curve to C, Control points are both at Q
        context.line_to(x+w,y+h-r)                  # Move to D
        context.curve_to(x+w,y+h,x+w,y+h,x+w-r,y+h) # Curve to E
        context.line_to(x+r,y+h)                    # Line to F
        context.curve_to(x,y+h,x,y+h,x,y+h-r)       # Curve to G
        context.line_to(x,y+r)                      # Line to H
        context.curve_to(x,y,x,y,x+r,y)             # Curve to A
        context.move_to(x,y)
        if border:
            context.line_to(x+w,y)
            context.line_to(x+w,y)
            context.line_to(x+w,y+h)
            context.line_to(x,y+h)
            context.line_to(x,y)

        return

    def set_style(self):
        """Change Gtk+ Style
        """
        provider = Gtk.CssProvider()
        # Demo CSS kindly provided by Numix project
        provider.load_from_path(join(WHERE_AM_I, self.skin, 'style.css'))
        screen = Gdk.Screen.get_default()
        if screen is None:
            return
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

class RenameDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, _("Callout position change"), parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label(_("Do you want to save the changed callout position in the image?"))
        # 画像に吹き出し位置を保存
        self.changeFilename = Gtk.CheckButton(_("Save callout location in image"))
        self.changeFilename.set_active(True)
        # デフォルトの吹き出し位置を変更
        self.calloutDefault = Gtk.CheckButton(_("Change default callout position"))
        self.calloutDefault.set_active(True)
        box = self.get_content_area()
        box.add(label)
        box.add(self.changeFilename)
        box.add(self.calloutDefault)
        self.show_all()

if __name__ == '__main__':
    moeclock()
    Gtk.main()
