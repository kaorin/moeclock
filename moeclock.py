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

WALLPAPER_PATH = "/home/kaoru/themes/BackGround/used-wallpaper"
__VERSION__="1.5.1.2"
NAME="moeclock"
APP = 'moeclock'
WHERE_AM_I = abspath(dirname(__file__))
LOCALE_DIR = join(WHERE_AM_I, 'locale')

SOUND_PLAY="paplay"

try:
    locale.setlocale(locale.LC_ALL, '')
except:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

print('Using locale directory: {}'.format(LOCALE_DIR))

WEEKString=[ _('(Mon)'), _('(Tue)'), _('(Wed)'), _('(Thu)'), _('(Fri)'), _('(Sat)'), _('(Sun)'),]

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
    ConfigPath = "/.config/moeclock.xml"
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
                self.domobj = minidom.parse(os.path.abspath(os.path.expanduser("~") + self.ConfigPath))
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
            file = codecs.open(os.path.abspath(os.path.expanduser("~") + self.ConfigPath), 'wb', encoding='utf-8')
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
        self.notice = eval(conf.GetOption("notice"))
        self.alwaysTop = eval(conf.GetOption("alwaysTop"))
        self.weekOffset = eval(conf.GetOption("weekOffset"))
        self.skin = conf.GetOption("skin")
        self.windowDecorate = eval(conf.GetOption("windowDecorate"))
        self.annotationType = eval(conf.GetOption("annotationType"))
        self.soundCutOut = eval(conf.GetOption("soundCutOut"))
        self.sound = conf.GetOption("sound")
        self.calloutSize = conf.GetOption("calloutSize")
        self.drawFrame = eval(conf.GetOption("drawFrame"))
        self.roundWindow = eval(conf.GetOption("roundWindow"))
        if len(uselist) > 0:
            self.use_wallpaper_list = eval(uselist)
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
        mainWindow.move(int(xpos),int(ypos))
        if int(xsize) > 10 and int(ysize) > 10 :
            self.userResize = False
        mainWindow.resize(int(xsize),int(ysize))
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
            if os.path.exists("/usr/share/moeclock/sound/nosound.wav") == True:
                soundPath = "/usr/share/moeclock/sound/nosound.wav"
            elif os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/sound/nosound.wav") == True:
                soundPath = os.path.dirname(os.path.abspath(__file__)) + "/sound/nosound.wav"
            cmdStr = SOUND_PLAY + " "+ soundPath
            self.execCommand(cmdStr)
        if os.path.exists(self.sound) :
            soundFile = self.fcSound.get_filename()
            cmdStr = SOUND_PLAY + " " + soundFile
            self.execCommand(cmdStr)

    def on_fcSkin_file_set(self,widget):
        '''
        スキン選択
        '''
        skin = self.fcSkin.get_filename()
        if os.path.exists(skin + "/color_setting.txt") :
            for line in open(skin + "/color_setting.txt", 'r'):
                line = line.strip('\n')
                if len(line) > 0:
                    self.colorSelect.set_color(Gdk.color_parse(line))

    def on_cbSoundCutOut_toggled(self, wiget):
        '''
        音声の先頭が切れる場合の対応を行うかどうか
        '''
        self.soundCutOut = self.cbSoundCutOut.get_active()

    def on_properties_delete_event(self,widget,event):
        widget.hide()
        return Gtk.TRUE

    def on_daPict_draw(self,widget, cr, event=None):
        '''
        画面表示イベントハンドラ
        '''
        if self.pixbuf2:
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf2, 0, 0)
            cr.paint()
            self.userResize = True

    def _setWallpaper(self,WallpaperLocation):
        '''
        壁紙設定
        '''
        try:
            mainWindow = self.wMain.get_object("Main")
            pict = self.wMain.get_object("daPict")
            # path = self.skin + '/style.css'
            # if os.path.exists(path) == True and self.drawFrame == False:
            #     pict.set_visible(False)
            (xsize,ysize) = mainWindow.get_size()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(WallpaperLocation)
            x = float(pixbuf.get_width())
            y = float(pixbuf.get_height())
            aspect = y / x
            self.pixbuf2 = pixbuf.scale_simple(xsize, int(xsize*aspect),2 )
            cr = pict.get_window().cairo_create()
            Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
            cr.paint()
            self.userResize = False
            mainWindow.resize(xsize,int(xsize*aspect))
            if self.roundWindow:
                region = self.createRegion(self.pixbuf2)
                mainWindow.shape_combine_region(region)
            else:
                mainWindow.shape_combine_region(None)
            pict.queue_draw()
            del pixbuf
            gc.collect()
            return True
        except Exception as e:
            print(e)
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))
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
        (xpos, ypos) = mainWindow.get_position()
        (xsize, ysize) = mainWindow.get_size()
        conf.SetOption("x_pos",xpos)
        conf.SetOption("y_pos",ypos)
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

    def on_miDecorate_toggled(self,widget):
        '''
        タイトルバー表示切り替え
        実際はウィンドウ装飾を切り替える
        '''
        self.windowDecorate = widget.get_active()
        mainWindow = self.wMain.get_object("Main")
        mainWindow.set_decorated(self.windowDecorate)
        (xsize, ysize) = mainWindow.get_size()
        mainWindow.resize(xsize,40)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)
        
    def on_miMicro_activate(self,widget):
        '''
        表示サイズ変更：最小
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(280,88)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miSmall_activate(self,widget):
        '''
        表示サイズ変更：小
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(320,180)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miMidium_activate(self,widget):
        '''
        表示サイズ変更：中
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(400,225)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miLarge_activate(self,widget):
        '''
        表示サイズ変更：大
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(480,270)
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miBig_activate(self,widget):
        '''
        表示サイズ変更：特大
        '''
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(640,360)
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
        if self.userResize :
            self._buildWallPaper(self.wlist[self.sw])
            self._setWallpaper("/tmp/moeclock.png")

    def on_Main_window_state_event(self, widget, event):
        '''
        画面状態変更イベント
        最小化した際にタスクバーに表示するかどうかの切り替え
        '''
        mainWindow = self.wMain.get_object("Main")
        if event.new_window_state & Gdk.WindowState.ICONIFIED:
            mainWindow.set_skip_taskbar_hint(False)
            self.iconifed = True
        else:
            mainWindow.set_skip_taskbar_hint(True)
            self.iconifed = False

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
            if os.path.exists("/usr/share/moeclock/sound/nosound.wav") == True:
                soundPath = "/usr/share/moeclock/sound/nosound.wav"
            elif os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/sound/nosound.wav") == True:
                soundPath = os.path.dirname(os.path.abspath(__file__)) + "/sound/nosound.wav"
            cmdStr = SOUND_PLAY + " " + soundPath
            self.execCommand(cmdStr)
        cmdStr = SOUND_PLAY + " " + self.sound
        self.execCommand(cmdStr)

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
            width = svg.props.width
            height = svg.props.height
            # 吹き出し拡大
            scale = float(self.calloutSize.replace("%","")) / 100;
            s2 = cairo.SVGSurface(None, width * scale, height * scale)
            ctx = cairo.Context(s2)
            ctx.save()
            if anoType == 0:
                ctx.scale(scale, scale)
            if anoType == 1:
                ctx.translate(0, height * scale)
                ctx.scale(scale, -scale)
            if anoType == 2:
                ctx.translate(width * scale, 0)
                ctx.scale(-scale, scale)
            if anoType == 3:
                ctx.translate(width * scale, height * scale)
                ctx.scale(-scale, -scale)
            svg.render_cairo(ctx)
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
            col = Gdk.color_parse(self.color)
            ctx.set_source_rgb(col.red_float, col.green_float, col.blue_float)
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
            if self.drawFrame == True:
                col = Gdk.color_parse(self.color)
                ctx.set_source_rgb(col.red_float, col.green_float, col.blue_float)
                self.roundedrec(ctx, 0, 0, pixbufWall.get_width(), pixbufWall.get_height(), self.round, self.lineWidth)
                ctx.close_path()
                ctx.stroke()
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
            os.remove('/tmp/moeclock.png')
            return False

    def createRegion(self, pixbuf):
        x = pixbuf.get_width()
        y = pixbuf.get_height()
        mask = cairo.ImageSurface(cairo.FORMAT_ARGB32, x, y)
        ctx = cairo.Context(mask)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        ctx.rectangle(0,0,x,y)
        ctx.fill()
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        self.roundedrec(ctx, 0, 0, x, y, self.round, 1, False)
        ctx.close_path()
        ctx.fill_preserve()
        ctx.stroke()
        # デバッグ用
        # mask.write_to_png('/tmp/mask.png')
        region = Gdk.cairo_region_create_from_surface(mask)
        return region

    def execCommand(self,command):
        '''
        コマンド実行
        '''
        print (command)   #受け渡されたコマンドのデバッグ用プリント
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        ret = subprocess.run(command, shell=True)
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
        screen = Gdk.Display.get_default_screen(Gdk.Display.get_default())
        # I was unable to found instrospected version of this
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
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
