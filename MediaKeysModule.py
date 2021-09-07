# -*- coding: utf-8 -*-
import os
import json
import CBE
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

class MediaKeysModule(CBE.CBEModule):
    def __init__(self):
        self.nextCMD = None

    def GetDefaultConfig(self):
        tempDict = {
            "MK_CMDName": "next",
            "MK_CMDCooldown": 30,
            "MK_CMDIsGlobal": True,
            "MK_CMDUsage": "!next (Cost: 100)",
            "MK_CMDDescription": "Plays the next song in the playlist",
            "MK_Cost": 100,
            "MK_FreeForMods": True,
            "MK_NotEnoughCurrency": "$user, you need $cost $currencyname to do this!",
            "MK_Paid": "$user pays $cost $currencyname to skip this song!",
            "MK_ModSkips": "$user does not pay $cost $currencyname due to the mod status!"
        }
        return tempDict

    def RegisterUI(self):
        self.cbe.AddUIFromFile("UI/MediaKeysModule_UI.json")
        return 
    
    def RegisterCommands(self):
        cfg = self.cbe.Config
        self.nextCMD = CBE.CBECommand(cfg["MK_CMDName"], cfg["MK_CMDCooldown"], False, cfg["MK_CMDIsGlobal"], cfg["MK_CMDUsage"], cfg["MK_CMDDescription"], self.ProcessNext)
        self.cbe.AddCommand(self.nextCMD)
        return
    
    def RegisterHelp(self):
        return

    def ReloadSettings(self, jsonData):
        self.cbe.CBEDebugLog("ReloadSettings", "MediaKeysModule")
        self.cbe.RemoveCommand(self.nextCMD.cmd)
        self.RegisterCommands()
    
    def ProcessNext(self, data):
        self.cbe.CBEDebugLog("SENDING MEDIA KEY", "MediaKeysModule")
        points = self.cbe.GetPoints(data.User)
        cost = self.cbe.Config["MK_Cost"]
        isMod = self.cbe.HasPermission(data.User, "moderator", "") or self.cbe.HasPermission(data.User, "broadcaster", "")
        if points >= cost or isMod:
            PressKey(0xB0)
            ReleaseKey(0xB0)
            if not isMod:
                self.cbe.RemovePoints(data.User, data.UserName, cost)
                self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["MK_Paid"]).safe_substitute(user=data.UserName, cost=cost, currencyname=self.cbe.GetCurrencyName()))
            else:
                self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["MK_ModSkips"]).safe_substitute(user=data.UserName, cost=cost, currencyname=self.cbe.GetCurrencyName()))
        else:
            poorMessage = CBE.stemp(self.cbe.Config["MK_NotEnoughCurrency"]).safe_substitute(user=data.UserName, cost=cost, currencyname=self.cbe.GetCurrencyName())
            self.cbe.SendTwitchMessage(poorMessage)