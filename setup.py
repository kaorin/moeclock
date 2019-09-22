#!/usr/bin/env python
# -*- coding: utf-8 -*-

__VERSION__="1.5.1.1"

params = {
        'name': 'moeclock',
        'version': __VERSION__,
        'description': 'moeclock is Desktop Clock',
        'author': 'Kaoru Konno',
        'author_email': 'kaoru.konno@gmail.com',
        'url': 'https://github.com/kaorin/moeclock',
        'scripts': ['moeclock','moeclock_autostart'],
        'data_files': [
            ('share/moeclock',
                ['moeclock.py',
                'moeclock.png',
                'sound.wav',
                'moeclock.glade',
                'moeclockdlg.glade',
                'LICENSE',
                'README.md']),
            ('share/moeclock/locale/ja_JP/LC_MESSAGES',
                ['locale/ja_JP/LC_MESSAGES/moeclock.po',
                'locale/ja_JP/LC_MESSAGES/moeclock.mo',]),
            ('share/moeclock/locale/en_US/LC_MESSAGES',
                ['locale/en_US/LC_MESSAGES/moeclock.po',
                'locale/en_US/LC_MESSAGES/moeclock.mo',]),
            ('share/moeclock/locale/ja/LC_MESSAGES',
                ['locale/ja/LC_MESSAGES/moeclock.po',
                'locale/ja/LC_MESSAGES/moeclock.mo',]),
            ('share/moeclock/locale/en/LC_MESSAGES',
                ['locale/en/LC_MESSAGES/moeclock.po',
                'locale/en/LC_MESSAGES/moeclock.mo',]),
            ('share/moeclock/default',
                ['default/color_setting.txt',
                'default/frame.png',
                'default/logo.png',
                'default/annotation.svg']),
            ('share/moeclock/moeskin_red',
                ['moeskin_red/color_setting.txt',
                'moeskin_red/frame.png',
                'moeskin_red/logo.png',
                'moeskin_red/annotation.svg']),
            ('share/moeclock/moeskin_purple',
                ['moeskin_purple/color_setting.txt',
                'moeskin_purple/frame.png',
                'moeskin_purple/logo.png',
                'moeskin_purple/annotation.svg']),
            ('share/moeclock/moeskin_pink',
                ['moeskin_pink/color_setting.txt',
                'moeskin_pink/frame.png',
                'moeskin_pink/logo.png',
                'moeskin_pink/annotation.svg']),
            ('share/moeclock/moeskin_orange',
                ['moeskin_orange/color_setting.txt',
                'moeskin_orange/frame.png',
                'moeskin_orange/logo.png',
                'moeskin_orange/annotation.svg']),
            ('share/moeclock/moeskin_navy',
                ['moeskin_navy/color_setting.txt',
                'moeskin_navy/frame.png',
                'moeskin_navy/logo.png',
                'moeskin_navy/annotation.svg']),
            ('share/moeclock/moeskin_miku',
                ['moeskin_miku/color_setting.txt',
                'moeskin_miku/frame.png',
                'moeskin_miku/logo.png',
                'moeskin_miku/annotation.svg']),
            ('share/moeclock/moeskin_green',
                ['moeskin_green/color_setting.txt',
                'moeskin_green/frame.png',
                'moeskin_green/logo.png',
                'moeskin_green/annotation.svg']),
            ('share/moeclock/moeskin_bluegreen',
                ['moeskin_bluegreen/color_setting.txt',
                'moeskin_bluegreen/frame.png',
                'moeskin_bluegreen/logo.png',
                'moeskin_bluegreen/style.css',
                'moeskin_bluegreen/annotation.svg']),
            ('share/moeclock/moeskin_blue',
                ['moeskin_blue/color_setting.txt',
                'moeskin_blue/frame.png',
                'moeskin_blue/logo.png',
                'moeskin_blue/annotation.svg']),
            ('share/moeclock/moeskin_yellow',
                ['moeskin_yellow/color_setting.txt',
                'moeskin_yellow/frame.png',
                'moeskin_yellow/logo.png',
                'moeskin_yellow/annotation.svg']),
            ('share/moeclock/moeskin_red_slim',
                ['moeskin_red_slim/color_setting.txt',
                'moeskin_red_slim/frame.png',
                'moeskin_red_slim/logo.png',
                'moeskin_red_slim/annotation.svg']),
            ('share/moeclock/moeskin_purple_slim',
                ['moeskin_purple_slim/color_setting.txt',
                'moeskin_purple_slim/frame.png',
                'moeskin_purple_slim/logo.png',
                'moeskin_purple_slim/annotation.svg']),
            ('share/moeclock/moeskin_pink_slim',
                ['moeskin_pink_slim/color_setting.txt',
                'moeskin_pink_slim/frame.png',
                'moeskin_pink_slim/logo.png',
                'moeskin_pink_slim/annotation.svg']),
            ('share/moeclock/moeskin_orange_slim',
                ['moeskin_orange_slim/color_setting.txt',
                'moeskin_orange_slim/frame.png',
                'moeskin_orange_slim/logo.png',
                'moeskin_orange_slim/annotation.svg']),
            ('share/moeclock/moeskin_navy_slim',
                ['moeskin_navy_slim/color_setting.txt',
                'moeskin_navy_slim/frame.png',
                'moeskin_navy_slim/logo.png',
                'moeskin_navy_slim/annotation.svg']),
            ('share/moeclock/moeskin_green_slim',
                ['moeskin_green_slim/color_setting.txt',
                'moeskin_green_slim/frame.png',
                'moeskin_green_slim/logo.png',
                'moeskin_green_slim/annotation.svg']),
            ('share/moeclock/moeskin_bluegreen_slim',
                ['moeskin_bluegreen_slim/color_setting.txt',
                'moeskin_bluegreen_slim/frame.png',
                'moeskin_bluegreen_slim/logo.png',
                'moeskin_bluegreen_slim/annotation.svg']),
            ('share/moeclock/moeskin_blue_slim',
                ['moeskin_blue_slim/color_setting.txt',
                'moeskin_blue_slim/frame.png',
                'moeskin_blue_slim/logo.png',
                'moeskin_blue_slim/annotation.svg']),
            ('share/moeclock/moeskin_yellow_slim',
                ['moeskin_yellow_slim/color_setting.txt',
                'moeskin_yellow_slim/frame.png',
                'moeskin_yellow_slim/logo.png',
                'moeskin_yellow_slim/annotation.svg']),
            ('share/moeclock/mikunchu',
                ['mikunchu/color_setting.txt',
                'mikunchu/frame.png',
                'mikunchu/logo.png',
                'mikunchu/annotation.svg']),
            ('share/moeclock/moeskin_heart',
                ['moeskin_heart/color_setting.txt',
                'moeskin_heart/frame.png',
                'moeskin_heart/logo.png',
                'moeskin_heart/annotation.svg']),
            ('share/moeclock/moeskin_heart02',
                ['moeskin_heart02/color_setting.txt',
                'moeskin_heart02/frame.png',
                'moeskin_heart02/logo.png',
                'moeskin_heart02/annotation.svg']),
            ('share/moeclock/sound',
                ['sound/nosound.wav',
                'sound/sachika_01.wav',
                'sound/sachika_02.wav',
                'sound/sachika_03.wav',
                'sound/sachika_04.wav',
                'sound/sachika_05.wav',
                'sound/sachika_06.wav',
                'sound/sachika_07.wav',
                'sound/sachika_08.wav',
                'sound/sachika_09.wav',
                'sound/sachika_10.wav',
                'sound/sachika_11.wav']),
            ('share/applications',
				['moeclock.desktop',])],
       'license': 'MIT',
        'download_url': \
            'https://github.com/kaorin/moeclock/archive/master.zip',
        'classifiers': [
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: MIT license(MIT)',
            'Operating System :: OS Independent',
            'Programming Language :: Python']}

from setuptools import setup

# this bit should be the same for both systems
setup(**params)
