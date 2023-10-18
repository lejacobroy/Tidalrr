#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   enums.py
@Time    :   2020/08/08
@Author  :   Yaronzz
@Version :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''
from enum import Enum


class AudioQuality(Enum):
    Normal = 0
    High = 1
    HiFi = 2
    Master = 3
    Max = 4

class Type(Enum):
    Album = 0
    Track = 1
    Playlist = 3
    Artist = 4
    Mix = 5
    Null = 6