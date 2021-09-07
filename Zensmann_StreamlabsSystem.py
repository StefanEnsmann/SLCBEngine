# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import CBE
import CSWModule
import DummyCommandModule
import DiscordPointsModule
import ShowImageModule
import MediaKeysModule
import AdviceModule

Parent = None # prevents an error in IDEs but does not break bot functionality

# necessary information -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ScriptName = "Zensmann Chatbot"
Website = "https://streaming.ensmann.de"
Description = "Chatbot for Zensmann's Twitch channel"
Creator = "Zensmann"
Version = "2.0"

cbeInstance = CBE.ChatBotEngine(ScriptName)
cbeInstance.RegisterModule(CSWModule.CSW())
#cbeInstance.RegisterModule(DummyCommandModule.DummyCommand(0)) #!multi
cbeInstance.RegisterModule(DummyCommandModule.DummyCommand(1)) #!rules / !nuzlocke
cbeInstance.RegisterModule(DummyCommandModule.DummyCommand(2)) #!discord
cbeInstance.RegisterModule(DummyCommandModule.DummyCommand(3)) #!twitter
cbeInstance.RegisterModule(DummyCommandModule.DummyCommand(4)) #!deckel
cbeInstance.RegisterModule(DummyCommandModule.DummyCommand(5)) #!youtube
cbeInstance.RegisterModule(DummyCommandModule.DummyCommand(6)) #!duell
cbeInstance.RegisterModule(ShowImageModule.ShowImageModule())
cbeInstance.RegisterModule(MediaKeysModule.MediaKeysModule())
cbeInstance.RegisterModule(AdviceModule.AdviceModule())
cbeInstance.Finalize()

def Init():
    cbeInstance.ChatBotParent = Parent
    cbeInstance.Init()

def Execute(data):
    cbeInstance.Execute(data)

def Tick():
    cbeInstance.Tick()

def ScriptToggled(state):
    cbeInstance.ScriptToggled(state)

def Unload():
    cbeInstance.Unload()

def Parse(parseString, userid, username, targetid, targetname, message):
    return cbeInstance.Parse(parseString, userid, username, targetid, targetname, message)

def ReloadSettings(jsonData):
    cbeInstance.ReloadSettings(jsonData)

def WorkaroundReloadSettings():
    CBE.WorkaroundReloadSettings(cbeInstance)