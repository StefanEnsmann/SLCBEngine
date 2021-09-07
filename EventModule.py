# -*- coding: utf-8 -*-
# modules
import os
import codecs
import datetime
import CBE

# load UI
CBE.LoadUI("ChatbotEventModule_UI.json")

# backup command name
_cmdName = ""

def EventLoadConfig():
    tempDict = {}
    tempDict["Event_CommandName"] = "event"
    tempDict["Event_CommandCooldown"] = 120
    tempDict["Event_CommandIsGlobalCooldown"] = True
    tempDict["Event_CommandUsage"] = "!event"
    tempDict["Event_CommandDescription"] = "Shows the time until a given event"

    tempDict["Event_Start"] = "01-01-1999:10-00"
    tempDict["Event_End"] = "02-01-1999:10-00"
    tempDict["Event_DaysRemainingResponse"] = "There are still $days days until event"
    tempDict["Event_StartsTodayResponse"] = "Event starts today!"
    tempDict["Event_CurrentResponse"] = "Event is currently running!"
    tempDict["Event_OverResponse"] = "Event is over already"

    for key in tempDict.keys():
        if key not in CBE.Config.keys():
            CBE.Config[key] = tempDict[key]
    return
CBE.CheckConfigCallbacks.append(EventLoadConfig)

def EventInit():
    global _cmdName
    _cmdName = CBE.Config["Event_CommandName"]
    CBE.Commands[CBE.Config["Event_CommandName"]] = {"cd": "Event_CommandCooldown", "global": "Event_CommandIsGlobalCooldown", "hasArgs": False, "func": EventExecute, "usage": "Event_CommandUsage", "desc": "Event_CommandDescription"}
CBE.InitCallbacks.append(EventInit)

def EventExecute(data, timed=False):
    try:
        startdate = datetime.datetime.strptime(CBE.Config["Event_Start"], "%d-%m-%Y:%H-%M")
        enddate = datetime.datetime.strptime(CBE.Config["Event_End"], "%d-%m-%Y:%H-%M")
        now = datetime.datetime.now()
        now = datetime.datetime(now.year, now.month, now.day, startdate.hour, startdate.minute, 0, 0)
        if now > startdate and enddate > now:
            CBE.SendTwitchMessage(CBE.Config["Event_CurrentResponse"])
        elif now > startdate:
            CBE.SendTwitchMessage(CBE.Config["Event_OverResponse"])
        elif (startdate - now).days > 0:
            CBE.SendTwitchMessage(CBE.stemp(CBE.Config["Event_DaysRemainingResponse"]).safe_substitute(days=(startdate - now).days))
        else:
            CBE.SendTwitchMessage(CBE.Config["Event_StartsTodayResponse"])
        CBE.CBEAddCooldown(data, CBE.Config["Event_CommandName"], CBE.Config["Event_CommandCooldown"], CBE.Config["Event_CommandIsGlobalCooldown"])
    except Exception as e:
        CBE.Log(CBE.ScriptName, str(e))
        return
    return

def InternalEventReloadSettings(jsonData):
    global _cmdName
    if _cmdName != CBE.Config["Event_CommandName"]:
        CBE.Commands[CBE.Config["Event_CommandName"]] = CBE.Commands[_cmdName]
        del CBE.Commands[_cmdName]
        _cmdName = CBE.Config["Event_CommandName"]
CBE.ReloadSettingsCallbacks.append(InternalEventReloadSettings)