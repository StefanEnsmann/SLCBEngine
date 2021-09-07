# What it is
A Chatbot Engine (CBE) for the standalone Streamlabs Chatbot (SLCB)

# What it does
The CBE provides advanced functionality for managing several features like commands or other things in a (semi-)controlled environment. The user is able to register several modules to the base engine. Each module has access to the general SLCB-API via the CBE without the need to implement them all again for each module.

# How to use
Download the latest version from the [https://github.com/StefanEnsmann/CBE/releases](releases) page. Put the contents of the .zip file (namely `CBE.py`, `CBEModule.py` and `UI`) besides your base script (e.g. `Main_StreamlabsSystem.py`) in the Scripts folder for SLCB. Instantiate the engine and hook it into the functions called by SLCB (see minimal example below).

In the current version of SLCB there is a bug that prevents `ReloadSettings(jsonData)` from being called. With the function `WorkaroundReloadSettings()` you can trigger the CBE version of `ReloadSettings(jsonData)` with a button click in the script UI in SLCB after clicking on "Save Settings".

# Example
```python
# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import CBE
from TestModule import *

Parent = None # prevents an error in IDEs but does not break bot functionality

ScriptName = "Example Chatbot"
Website = "https://github.com/StefanEnsmann/CBE"
Description = "Example Chatbot"
Creator = "Zensmann"
Version = "1.0"

cbeInstance = CBE.ChatBotEngine(ScriptName)
# register your modules here
cbeInstance.RegisterModule(TestModule())
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
```
