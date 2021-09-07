# -*- coding: utf-8 -*-
# modules
import CBE

# necessary
Hydration_NextHydratedTime = -1

# load UI
CBE.LoadUI("ChatbotHydrationModule_UI.json")

# backup command name
_cmdName = ""

def GetWaterString(duration):
    return CBE.stemp(CBE.Config["Hydration_WaterString"]).safe_substitute(amount=str(int(duration / 3600 * CBE.Config["Hydration_WaterPerHour"])))

def GetTimeString(duration):
    seconds = int(duration)
    minutes = seconds / 60
    timeString = "" + ("%02d" % (seconds % 60))
    if minutes > 0:
        hours = minutes / 60
        timeString = ("%02d" % (minutes % 60)) + ":" + timeString
        if hours > 0:
            return str(hours) + ":" + timeString + "h"
        else:
            return timeString + "m"
    else:
        return timeString + "s"
    return timeString

def HydrationLoadConfig():
    tempDict = {}
    tempDict["Hydration_CommandName"] = "hydration"
    tempDict["Hydration_CommandCooldown"] = 120
    tempDict["Hydration_CommandIsGlobalCooldown"] = True
    tempDict["Hydration_CommandUsage"] = "!hydration"
    tempDict["Hydration_CommandDescription"] = "Shows the invitation to drink something"

    tempDict["Hydration_StayHydrated"] = "Stay hydrated! DrinkPurple"
    tempDict["Hydration_StayBeerdrated"] = "Stay beerdrated! HSCheers"
    tempDict["Hydration_Message"] = "$streamer is streaming since $time and should have consumed $amount of water"
    tempDict["Hydration_WaterString"] = "$amount ml"
    
    tempDict["Hydration_WaterPerHour"] = 120
    tempDict["Hydration_BeerdratedChance"] = 20
    tempDict["Hydration_StayHydratedInterval"] = 30 * 60
    for key in tempDict.keys():
        if key not in CBE.Config.keys():
            CBE.Config[key] = tempDict[key]
    return
CBE.CheckConfigCallbacks.append(HydrationLoadConfig)

def HydrationInit():
    global Hydration_NextHydratedTime, _cmdName
    _cmdName = CBE.Config["Hydration_CommandName"]
    CBE.Commands[CBE.Config["Hydration_CommandName"]] = {"cd": "Hydration_CommandCooldown", "global": "Hydration_CommandIsGlobalCooldown", "hasArgs": False, "func": HydrationExecute, "usage": "Hydration_CommandUsage", "desc": "Hydration_CommandDescription"}
    Hydration_NextHydratedTime = CBE.Config["Hydration_StayHydratedInterval"]
CBE.InitCallbacks.append(HydrationInit)

def HydrationExecute(data, timed=False):
    msg = ""
    msg += CBE.Config["Hydration_StayHydrated"] if CBE.GetRandom(0, 100) > CBE.Config["Hydration_BeerdratedChance"] else CBE.Config["Hydration_StayBeerdrated"]
    if CBE.TimeGoingLive > -1:
        msg += " " + CBE.stemp(CBE.Config["Hydration_Message"]).safe_substitute(streamer=CBE.GetChannelName(), time=GetTimeString(CBE.GetStreamDuration()), amount=GetWaterString(CBE.GetStreamDuration()))
    CBE.SendTwitchMessage(msg)
    if not timed:
        CBE.CBEAddCooldown(data, CBE.Config["Hydration_CommandName"], CBE.Config["Hydration_CommandCooldown"], CBE.Config["Hydration_CommandIsGlobalCooldown"])
    return

def HydrationTick():
    global Hydration_NextHydratedTime
    if CBE.GetStreamDuration() > Hydration_NextHydratedTime:
        Hydration_NextHydratedTime += CBE.Config["Hydration_StayHydratedInterval"]
        HydrationExecute(None, True)
    return
CBE.TickCallbacks.append(HydrationTick)

def HydrationToggled(state):
    global Hydration_NextHydratedTime
    Hydration_NextHydratedTime = CBE.Config["Hydration_StayHydratedInterval"]
CBE.ScriptToggledCallbacks.append(HydrationToggled)

def InternalHydrationReloadSettings(jsonData):
    global _cmdName
    if _cmdName != CBE.Config["Hydration_CommandName"]:
        CBE.Commands[CBE.Config["Hydration_CommandName"]] = CBE.Commands[_cmdName]
        del CBE.Commands[_cmdName]
        _cmdName = CBE.Config["Hydration_CommandName"]
CBE.ReloadSettingsCallbacks.append(InternalHydrationReloadSettings)