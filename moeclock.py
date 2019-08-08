#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf
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

WALLPAPER_PATH = "/home/kaoru/themes/BackGround/used-wallpaper"
VERSION="1.3.0.3"
NAME="moeclock"
WEEKString=(u'（月）',u'（火）',u'（水）',u'（木）',u'（金）',u'（土）',u'（日）',)
APP = 'moeclock'
WHERE_AM_I = abspath(dirname(__file__))
LOCALE_DIR = join(WHERE_AM_I, 'locale')

usecompiz = True

class ConfigXML:
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
                    "sound": os.path.dirname(os.path.abspath(__file__)) + "/sound.wav"}
    AppName = "moeclock"
    ConfigPath = "/.config/moeclock.xml"
    Options = {}    #オプション値の辞書
    domobj = None

    def __init__(self, read):
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
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                text = str(node.data)
                text = text.rstrip(" \t\n")
                text = text.lstrip(" \t\n")
                rc = rc + text
        return rc

    def GetOption(self, optName ):
        if optName == "password":
            return str(base64.b64decode(self.Options[optName]))
        else:
            try:
                return str(self.Options[optName])
            except:
                return str(self.OptionList[optName])

    def SetOption(self, optName, value ):
        if optName == "password":
            val = base64.b64encode(value)
            self.Options[optName] = val
        else:
            self.Options[optName] = value

    def Write(self):
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

    wallpaper_list = []
    use_wallpaper_list = []
    #timeout_interval = 10
    timeout_interval = 1
    min = -1
    pixbuf2 = None
    userResize = True
    iconifed = False
    noticeFlag = True
    notice = True

    def __init__(self):
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
        self.sound = conf.GetOption("sound")
        if len(uselist) > 0:
            use_wallpaper_list = eval(uselist)
        #メインウィンドウを作成
        self.wMain = Gtk.Builder()
        self.wMain.set_translation_domain(APP)
        self.wMain.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/moeclock.glade")
        #Create our dictionay and connect it
        dicMain = { "on_daPict_button_press_event" : self.showMenu,
                    "on_miSetting_activate" : self.properties,
                    "on_miExit_activate" : self.on_quit,
                    "on_miInfo_activate" : self.showAboutDialog,
                    "on_miNotice_toggled" : self.on_miNotice_toggled,
                    "on_miTop_toggled" : self.on_miTop_toggled,
                    "on_miMicro_activate" : self.on_miMicro_activate,
                    "on_miSmall_activate" : self.on_miSmall_activate,
                    "on_miMidium_activate" : self.on_miMidium_activate,
                    "on_miLarge_activate" : self.on_miLarge_activate,
                    "on_miBig_activate" : self.on_miBig_activate,
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
        self.colorSelect.set_color(Gdk.color_parse(self.color))
        self.fontSelect = self.wTree.get_object ("fntSelect")
        self.fontSelect.set_font_name(self.font)
        self.fontSelect.set_show_size(False)
        self.fontSelect.set_show_style(False)
        self.sbWeekOffset = self.wTree.get_object("sbWeekOffset")
        self.sbWeekOffset.set_value(self.weekOffset)
        self.fcSkin = self.wTree.get_object ("fcSkin")
        self.fcSkin.set_filename(self.skin+"/")
        self.fcSkin.set_current_folder(self.skin+"/")
        self.fcSound = self.wTree.get_object ("fcSound")
        self.fcSound.set_filename(self.sound)
        #フィルタの作成
        self.allFilter = Gtk.FileFilter()
        self.waveFilter = Gtk.FileFilter()

        self.allFilter.set_name("全てのファイル")
        self.allFilter.add_pattern("*")

        self.waveFilter.set_name("音声ファイル")
        self.waveFilter.add_pattern("*.wav")

        self.fcSound.add_filter(self.waveFilter)
        self.fcSound.add_filter(self.allFilter)
        self.fcSound.set_filter(self.waveFilter)

        self.preferences = preferencesDialog
        #Create our dictionay and connect it
        dic = { "on_BTN_OK_clicked" : self.on_BTN_OK_clicked,
                   "on_BTN_CANCEL_clicked" : self.on_BTN_CANCEL_clicked,
                   "on_btnPlay_clicked" : self.on_btnPlay_clicked,
                   "on_properties_delete_event" : self.on_properties_delete_event,
                   "on_fcSkin_file_set" : self.on_fcSkin_file_set
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
        global WALLPAPER_PATH
        WALLPAPER_PATH = self.selectedFolder.get_filename()
        print (WALLPAPER_PATH)
        tmp = self.fontSelect.get_font_name().split(' ')
        if len(tmp) > 1:
            tmp = tmp[:-1]
        self.font = ' '.join(tmp)
        print ("font:"+self.font)
        self.color = "#%02X%02X%02X" % (int(self.colorSelect.get_color().red / 256),int(self.colorSelect.get_color().green / 256),int(self.colorSelect.get_color().blue / 256))
        self.weekOffset = self.sbWeekOffset.get_value_as_int()
        soundFile = self.fcSound.get_filename()
        if len(soundFile) > 0:
            self.sound = soundFile
        self.skin = self.fcSkin.get_filename()
        self._saveConf()
        self.preferences.hide()
        GLib.source_remove(self.timeout)
        self._buildWallPaper(self.wlist[self.sw])
        self._setWallpaper("/tmp/moeclock.png")
        self.timeout = GLib.timeout_add_seconds(int(self.timeout_interval),self.timeout_callback,self)

    def on_BTN_CANCEL_clicked(self,widget):
        self.selectedFolder.set_filename(WALLPAPER_PATH+"/")
        self.preferences.hide()

    def on_btnPlay_clicked(self,widget):
        if os.path.exists(self.sound) :
            soundFile = self.fcSound.get_filename()
            cmdStr = "aplay " + soundFile
            self.execCommand(cmdStr)

    def on_fcSkin_file_set(self,widget):
        skin = self.fcSkin.get_filename()
        if os.path.exists(skin + "/color_setting.txt") :
            for line in open(skin + "/color_setting.txt", 'r'):
                line = line.strip('\n')
                if len(line) > 0:
                    self.colorSelect.set_color(Gdk.color_parse(line))

    def on_properties_delete_event(self,widget,event):
        widget.hide()
        return Gtk.TRUE

    def on_daPict_draw(self,widget, cr, event=None):
        if self.pixbuf2:
            pict = self.wMain.get_object("daPict")
            # gc = pict.style.fg_gc[Gtk.StateFlags.NORMAL]
            # pict.window.draw_pixbuf(gc, self.pixbuf2, 0, 0, 0, 0, -1, -1)
            # cr = pict.get_window().cairo_create()
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf2, 0, 0)
            cr.paint()
            # cr.fill()
            self.userResize = True

    def _setWallpaper(self,WallpaperLocation):
        try:
            mainWindow = self.wMain.get_object("Main")
            pict = self.wMain.get_object("daPict")
            (xsize,ysize) = mainWindow.get_size()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(WallpaperLocation)
            x = float(pixbuf.get_width())
            y = float(pixbuf.get_height())
            aspect = y / x
            if self.pixbuf2 != None:
                del self.pixbuf2
            self.pixbuf2 = pixbuf.scale_simple(xsize, int(xsize*aspect),2 )
            del pixbuf
            # gc = pict.style.fg_gc[Gtk.StateFlags.NORMAL]
            # pict.window.draw_pixbuf(gc, self.pixbuf2, 0, 0, 0, 0, -1, -1)
            cr = pict.get_window().cairo_create()
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf2, 0, 0)
            cr.paint()
            # cr.fill()
            self.userResize = False
            mainWindow.resize(xsize,int(xsize*aspect))
            pict.queue_draw()
            return True
        except Exception as e:
            print(e)
            return False

    def _changeWallPaper(self):
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
        conf.Write()

    def showMenu(self,widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            #右クリック
            self.context_menu.popup(None, None, None,None, event.button, event.time)
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            #左クリック
            self._changeWallPaper()

    def on_quit(self,widget):
        self._saveConf()
        Gtk.main_quit()

    def on_miNotice_toggled(self,widget):
        self.notice = widget.get_active()

    def on_miTop_toggled(self,widget):
        self.alwaysTop = widget.get_active()
        mainWindow = self.wMain.get_object("Main")
        mainWindow.set_keep_above(self.alwaysTop)

    def on_miMicro_activate(self,widget):
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(280,88)
        while Gtk.events_pending():
            Gtk.main_iteration(1)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miSmall_activate(self,widget):
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(320,180)
        while Gtk.events_pending():
            Gtk.main_iteration(1)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miMidium_activate(self,widget):
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(400,225)
        while Gtk.events_pending():
            Gtk.main_iteration(1)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miLarge_activate(self,widget):
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(480,270)
        while Gtk.events_pending():
            Gtk.main_iteration(1)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_miBig_activate(self,widget):
        mainWindow = self.wMain.get_object("Main")
        mainWindow.resize(640,360)
        while Gtk.events_pending():
            Gtk.main_iteration(1)
        self.timeout2 = GLib.timeout_add(100,self.chanegSize_callback,self)

    def on_Main_size_allocate(self,widget,event):
        if self.userResize :
            self._buildWallPaper(self.wlist[self.sw])
            self._setWallpaper("/tmp/moeclock.png")

    def on_Main_window_state_event(self, widget, event):
        mainWindow = self.wMain.get_object("Main")
        if event.new_window_state & Gdk.WindowState.ICONIFIED:
            mainWindow.set_skip_taskbar_hint(False)
            self.iconifed = True
        else:
            mainWindow.set_skip_taskbar_hint(True)
            self.iconifed = False

    def on_Main_focus_in_event(self,widget,event):
        mainWindow = self.wMain.get_object("Main")
        if usecompiz:
            mainWindow.set_decorated(True)

    def on_Main_focus_out_event(self,widget,event):
        mainWindow = self.wMain.get_object("Main")
        if usecompiz:
            mainWindow.set_decorated(False)

    def on_Main_configure_event(self,widget,event):
        print (event)

    def showAboutDialog(self,*arguments, **keywords):
        if os.path.exists("/usr/share/moeclock/moeclock.png") == True:
            imagePath = "/usr/share/moeclock/moeclock.png"
        elif os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/moeclock.png") == True:
            imagePath = os.path.dirname(os.path.abspath(__file__)) + "/moeclock.png"
        self.logo = Gtk.Image()
        self.logo.set_from_file(imagePath)
        self.logo_pixbuf = self.logo.get_pixbuf()
        about = Gtk.AboutDialog()
        # "萌え時計",VERSION,"GPLv3","1分ごとに画像を変更し時間を通知します。",["かおりん"],["かおりん"],"かおりん",self.logo_pixbuf
        about.set_program_name("萌え時計")
        about.set_version(VERSION)
        about.set_license("GPLv2")
        about.set_comments("1分ごとに画像を変更し時間を通知します。")
        about.set_authors(["かおりん"])
        about.set_documenters(["かおりん"])
        about.set_logo(self.logo_pixbuf)
        about.connect("response", self.on_about_close)
        about.show()

    # destroy the aboutdialog
    def on_about_close(self, action, parameter):
        action.destroy()
    
    def properties(self,widget):
        self.preferences.show()

    def timeout_callback(self,event):
        d = datetime.datetime.today()
        if self.min != d.minute:
            self._changeWallPaper()
        mainWindow = self.wMain.get_object("Main")
        if self.iconifed :
            dateStr = d.strftime("萌え時計 - %H:%M:%S")
            mainWindow.set_title(dateStr)
        else:
            mainWindow.set_title("萌え時計")
        if self.notice :
            if d.minute == 0 and self.noticeFlag:
                if os.path.exists(self.sound) :
                   self.timeout3 = GLib.timeout_add(500,self.sound_callback,self)
                self.noticeFlag = False
            if d.minute > 0:
                self.noticeFlag = True
        return True

    def chanegSize_callback(self,event):
        self._buildWallPaper(self.wlist[self.sw])
        self._setWallpaper("/tmp/moeclock.png")

    def sound_callback(self,event):
        cmdStr = "aplay "+ self.sound
        self.execCommand(cmdStr)

    def _buildWallPaper(self,wallpaper):
        try:
            logging.debug("_buildWallPaper")
            logging.debug("wallpaper:"+wallpaper)
            print ("wallpaper:"+wallpaper)
            mainWindow = self.wMain.get_object("Main")
            (xsize,ysize) = mainWindow.get_size()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(wallpaper)
            x = float(pixbuf.get_width())
            y = float(pixbuf.get_height())
            aspect = y / x
            pixbuf2 = pixbuf.scale_simple(xsize, int(xsize*aspect),GdkPixbuf.InterpType.BILINEAR )
            del pixbuf
            pixbuf2.savev("/tmp/moeclockWall.png", "png", ["compression"], ["9"])
            del pixbuf2
            if os.path.exists(self.skin + '/frame.png') == False:
                 os.path.dirname(os.path.abspath(__file__)) + "/" + self.skin + '/frame.png'
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.skin + '/frame.png')
            pixbuf2 = pixbuf.scale_simple(xsize, int(xsize*aspect),GdkPixbuf.InterpType.BILINEAR )
            pixbuf2.savev("/tmp/moeclockFrame.png", "png", ["compression"], ["9"])
            del pixbuf
            del pixbuf2
            d = datetime.datetime.today()
            yearStr = '%sねん' % (d.year,)
            dateStr = d.strftime("%m/%d")
            timeStr = d.strftime("%H:%M")
            weekStr = WEEKString[d.weekday()]
            self.min = d.minute
            if os.path.exists(self.skin + '/annotation.png') == False:
                 os.path.dirname(os.path.abspath(__file__)) + "/" + self.skin + '/annotation.png'
            s1 = cairo.ImageSurface.create_from_png(self.skin + '/annotation.png')
            x1 = s1.get_width()
            y1 = s1.get_height()
            ctx = cairo.Context(s1)
            col = Gdk.color_parse(self.color)
            ctx.set_source_rgb(col.red_float, col.green_float, col.blue_float)
            ctx.select_font_face(self.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            print (self.font)
            ctx.set_font_size(16)
            ofsX = x1 - 144
            ofsY = y1 - 144
            (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(yearStr)
            ctx.move_to(144 / 2 + 10 - width/2 + ofsX, 60 + ofsY)
            ctx.show_text(yearStr)
            (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(dateStr)
            ctx.move_to(144 / 2 + 10 - width/2 + ofsX, 80 + ofsY)
            ctx.show_text(dateStr)
            ctx.set_font_size(10)
            ctx.move_to(144 / 2 + self.weekOffset + width + ofsX, 80 + ofsY)
            ctx.show_text(weekStr)
            ctx.set_font_size(22)
            (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents(timeStr)
            ctx.move_to(144 / 2 +10 - width/2 + ofsX, 105 + ofsY)
            ctx.show_text(timeStr)
            ctx.set_font_size(15)
            if d.minute == 0:
                (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents("になったよ!")
                ctx.move_to(144 / 2 +10 - width/2 + ofsX, 125 + ofsY)
                ctx.show_text("になったよ!")
            else:
                (x_bearing, y_bearing, width, height, x_advance, y_advance) = ctx.text_extents("だよ!")
                ctx.move_to(144 / 2 +10 - width/2 + ofsX, 125 + ofsY)
                ctx.show_text("だよ!")
            s1.write_to_png('/tmp/moeclockTmp.png')
            del s1

            #合成開始
            s1 = cairo.ImageSurface.create_from_png('/tmp/moeclockWall.png')
            s2 = cairo.ImageSurface.create_from_png('/tmp/moeclockTmp.png')
            if os.path.exists(self.skin + '/logo.png') == False:
                 os.path.dirname(os.path.abspath(__file__)) + "/" + self.skin + '/logo.png'
            s3 = cairo.ImageSurface.create_from_png(self.skin + '/logo.png')
            x3 = s3.get_width()
            y3 = s3.get_height()
            s4 = cairo.ImageSurface.create_from_png('/tmp/moeclockFrame.png')
            ctx = cairo.Context(s1)
            ctx.set_source_surface(s2,xsize-x1,(xsize*aspect)-y1)
            ctx.paint()
            ctx.set_source_surface(s3,0,(xsize*aspect)-y3)
            ctx.paint()
            ctx.set_source_surface(s4,0,0)
            ctx.paint()
            s1.write_to_png('/tmp/moeclock.png')
            del s1
            del s2
            del s3
            del s4
            return True
        except Exception as e:
            print(e)
            return False


    def execCommand(self,command):
        print (command)   #受け渡されたコマンドのデバッグ用プリント
        while Gtk.events_pending():
            Gtk.main_iteration(1)
        ret = subprocess.run(command, shell=True)
        while Gtk.events_pending():
            Gtk.main_iteration(1)
        print (ret)             #実行結果のデバッグ用プリント
        return ret

def init_translation():
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    locale.bindtextdomain(APP, LOCALE_DIR)
    gettext.bindtextdomain(APP, LOCALE_DIR)
    gettext.textdomain(APP)
    _ = gettext.gettext
    
    print('Using locale directory: {}'.format(LOCALE_DIR))

if __name__ == '__main__':
    ret = subprocess.run('ps -A | grep compiz', shell=True)
    if ret.stdout == None:
        usecompiz = False
    init_translation()
    moeclock()
    Gtk.main()
