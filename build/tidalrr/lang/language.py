#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   language.py
@Time    :   2020/08/19
@Author  :   Yaronzz
@Version :   1.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''

from tidalrr.lang.arabic import LangArabic
from tidalrr.lang.chinese import LangChinese
from tidalrr.lang.croatian import LangCroatian
from tidalrr.lang.czech import LangCzech
from tidalrr.lang.danish import LangDanish
from tidalrr.lang.dutch import LangDutch
from tidalrr.lang.english import LangEnglish
from tidalrr.lang.filipino import LangFilipino
from tidalrr.lang.french import LangFrench
from tidalrr.lang.german import LangGerman
from tidalrr.lang.hungarian import LangHungarian
from tidalrr.lang.italian import LangItalian
from tidalrr.lang.norwegian import LangNorwegian
from tidalrr.lang.polish import LangPolish
from tidalrr.lang.portuguese import LangPortuguese
from tidalrr.lang.russian import LangRussian
from tidalrr.lang.spanish import LangSpanish
from tidalrr.lang.turkish import LangTurkish
from tidalrr.lang.ukrainian import LangUkrainian
from tidalrr.lang.vietnamese import LangVietnamese
from tidalrr.lang.korean import LangKorean
from tidalrr.lang.japanese import LangJapanese

_ALL_LANGUAGE_ = [
    ['English', LangEnglish()],
    ['中文', LangChinese()],
    ['Turkish', LangTurkish()],
    ['Italian', LangItalian()],
    ['Czech', LangCzech()],
    ['Arabic', LangArabic()],
    ['Russian', LangRussian()],
    ['Filipino', LangFilipino()],
    ['Croatian', LangCroatian()],
    ['Spanish', LangSpanish()],
    ['Portuguese', LangPortuguese()],
    ['Ukrainian', LangUkrainian()],
    ['Vietnamese', LangVietnamese()],
    ['French', LangFrench()],
    ['German', LangGerman()],
    ['Danish', LangDanish()],
    ['Hungarian', LangHungarian()],
    ['Korean', LangKorean()],
    ['Japanese', LangJapanese()],
    ['Dutch', LangDutch()],
    ['Polish', LangPolish()],
    ['Norwegian', LangNorwegian()],
]

class Language(object):
    def __init__(self) -> None:
        self.select = LangEnglish()

    def __toInt__(self, str):
        try:
            return int(str)
        except:
            return 0
    
    def setLang(self, index):
        index = self.__toInt__(index)
        if index >= 0 and index < len(_ALL_LANGUAGE_):
            self.select = _ALL_LANGUAGE_[index][1]
        else:
            self.select = LangEnglish()

    def getLangName(self, index):
        index = self.__toInt__(index)
        if index >= 0 and index < len(_ALL_LANGUAGE_):
            return _ALL_LANGUAGE_[index][0]
        return ""

    def getLangChoicePrint(self):
        array = []
        index = 0
        while True:
            name = self.getLangName(index)
            if name == "":
                break
            array.append('\'' + str(index) + '\'-' + name)
            index += 1
        return ','.join(array)


LANG = Language()
