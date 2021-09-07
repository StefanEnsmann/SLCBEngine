# -*- coding: utf-8 -*-
#region importing custom modules ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
import CBE
import json
import string
import os
#endregion

# necessary
Counter_List = {}
Counter_File = "CSWcounters.json"
Counter_Formatted_File = "CSWcounters.txt"

# load UI
CBE.LoadUI("ChatbotCounterModule_UI.json")

# backup command name
_cmdName = ""

def CounterCheckConfig():
    tempDict = {}
    tempDict["Counter_CMDName"] = "counters"
    tempDict["Counter_CMDCooldown"] = 10
    tempDict["Counter_CMDIsGlobal"] = True
    tempDict["Counter_CMDUsage"] = "!counters [add <countername> [format]|delete <countername> confirm]"
    tempDict["Counter_CMDDescription"] = "Shows all available commands"
    tempDict["Counter_String_CounterJoin"] = ", "
    tempDict["Counter_CMDModifyPermissions"] = "moderator"
    tempDict["Counter_String_AvailableCounters"] = "Currently available counters: $list"
    tempDict["Counter_CounterCooldown"] = 10
    tempDict["Counter_String_AddedCounter"] = "Added counter !$counter"
    tempDict["Counter_String_DeletedCounter"] = "Deleted counter !$counter"
    tempDict["Counter_String_Help"] = "!$counter [+ [<n>]|- [<n>]|set <n>] (Cooldown $cooldown seconds)"
    tempDict["Counter_String_WholeNumber"] = "You have to provide a whole number"
    tempDict["Counter_String_AlreadyExists"] = "This counter already exists"
    tempDict["Counter_String_CommandExists"] = "There is already a command with this name"
    tempDict["Counter_String_NonASCII"] = "The counter name may only contain ascii-letters from a-z"
    tempDict["Counter_String_ConfirmNeeded"] = "You have to confirm the deletion"
    tempDict["Counter_String_DefaultFormat"] = "$counter today: $today ($total total)"
    tempDict["Counter_String_AccessError"] = "Error accessing counters"
    for key in tempDict.keys():
        if key not in CBE.Config.keys():
            CBE.Config[key] = tempDict[key]
    return
CBE.CheckConfigCallbacks.append(CounterCheckConfig)

def GetCounterHelp(counter):
    return CBE.stemp(CBE.Config["Counter_String_Help"]).safe_substitute(counter=counter, cooldown=CBE.Config["Counter_CounterCooldown"])

def InternalCounterHelp(data):
    arg0 = data.GetParam(1)
    if arg0.startswith("!"):
        arg0 = arg0[1:]
    if arg0 in Counter_List.keys():
        CBE.SendTwitchMessage(GetCounterHelp(arg0))
        return True
    return False
CBE.HelpCallbacks.append(InternalCounterHelp)

def LoadCounters():
    global Counter_List, _cmdName
    try:
        with open(os.path.join(CBE.Path, Counter_File), "r") as ctf:
            Counter_List = json.load(ctf)
    except IOError as e:
        CBE.CBELog("Could not open " + Counter_File + ": " + str(e))

def WriteFormattedCounters():
    try:
        with open(os.path.join(CBE.Path, Counter_Formatted_File), "w") as ctf:
            for cntr in sorted(Counter_List.keys()):
                ctf.write(str.capitalize(cntr) + ": " + str(Counter_List[cntr]["today"]) + " (Ges. " + str(Counter_List[cntr]["today"] + Counter_List[cntr]["total"]) + ")\n")
                #ctf.write(CBE.stemp(Counter_List[cntr]["format"]).safe_substitute(counter=cntr, today=str(Counter_List[cntr]["today"]), total=str(Counter_List[cntr]["total"] + Counter_List[cntr]["today"])) + "\n")
    except IOError as e:
        CBE.CBELog("Could not write to " + Counter_Formatted_File + ": " + str(e))

def InternalCounterInit():
    global _cmdName
    LoadCounters()
    _cmdName = CBE.Config["Counter_CMDName"]
    CBE.Commands[CBE.Config["Counter_CMDName"]] = {"cd": "Counter_CMDCooldown", "global": "Counter_CMDIsGlobal", "hasArgs": True, "func": ProcessCounters, "usage": "Counter_CMDUsage", "desc": "Counter_CMDDescription"}
    WriteFormattedCounters()
    return
CBE.InitCallbacks.append(InternalCounterInit)

def InternalCounterExecute(data):
    if data.IsChatMessage() and data.Message.startswith("!"):
        if Counter_List is None:
            CBE.SendTwitchMessage(CBE.Config["Counter_String_AccessError"])
        else:
            for counter in Counter_List.keys():
                if data.Message.startswith("!" + counter) and (data.GetParamCount() > 1 and CBE.ProcessCommandCooldown(data, counter + "_set") or data.GetParamCount() == 1):
                    if CBE.ProcessCommandCooldown(data, counter + "_show"):
                        ProcessCounter(data, counter)
                        return
    return
CBE.ExecuteCallbacks.append(InternalCounterExecute)

def InternalCounterUnload():
    SaveCounters()
    return
CBE.UnloadCallbacks.append(InternalCounterUnload)

def InternalCounterReloadSettings(jsonData):
    global _cmdName
    if _cmdName != CBE.Config["Counter_CMDName"]:
        CBE.Commands[CBE.Config["Counter_CMDName"]] = CBE.Commands[_cmdName]
        del CBE.Commands[_cmdName]
        _cmdName = CBE.Config["Counter_CMDName"]
CBE.ReloadSettingsCallbacks.append(InternalCounterReloadSettings)

#region counter processing ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def AddCounter(cntr, format):
    global Counter_List

    if Counter_List is None:
        CBE.SendTwitchMessage(CBE.Config["Counter_String_AccessError"])
    else:
        Counter_List[cntr] = {"today": 0, "total": 0, "format": CBE.Config["Counter_String_DefaultFormat"] if format is None else format}
        CBE.SendTwitchMessage(CBE.stemp(CBE.Config["Counter_String_AddedCounter"]).safe_substitute(counter=cntr))
    return

def DeleteCounter(cntr):
    global Counter_List

    if Counter_List is None:
        CBE.SendTwitchMessage(CBE.Config["Counter_AccessError"])
    else:
        del Counter_List[cntr]
        CBE.SendTwitchMessage(CBE.stemp(CBE.Config["Counter_String_DeletedCounter"]).safe_substitute(counter=cntr))
    return

def SaveCounters():
    global Counter_List

    if Counter_List is None:
        CBE.SendTwitchMessage(CBE.Config["Counter_String_AccessError"])
    else:
        for counter in Counter_List:
            Counter_List[counter]["total"] += Counter_List[counter]["today"]
            Counter_List[counter]["today"] = 0
        with open(os.path.join(CBE.Path, Counter_File), "w") as ctf:
            json.dump(Counter_List, ctf)
    return

def ProcessCounter(data, cntr):
    global Counter_List

    if Counter_List is None:
        CBE.SendTwitchMessage(CBE.Config["Counter_String_AccessError"])
    else:
        if data.GetParamCount() > 1:
            if data.GetParam(1) == "+":
                val = 1
                if data.GetParamCount() > 2:
                    if data.GetParam(2).isdigit():
                        val = int(data.GetParam(2))
                    else:
                        CBE.SendTwitchMessage(CBE.stemp(CBE.Config["Counter_String_WholeNumber"]).safe_substitute())
                        return
                Counter_List[cntr]["today"] += val
                CBE.CBEAddCooldown(data, cntr + "_set", CBE.Config["Counter_CounterCooldown"])
            elif data.GetParam(1) == "-":
                val = 1
                if data.GetParamCount() > 2:
                    if data.GetParam(2).isdigit():
                        val = int(data.GetParam(2))
                    else:
                        CBE.SendTwitchMessage(CBE.stemp(CBE.Config["Counter_String_WholeNumber"]).safe_substitute())
                        return
                Counter_List[cntr]["today"] = max(Counter_List[cntr]["today"] - val, 0)
                CBE.CBEAddCooldown(data, cntr + "_set", CBE.Config["Counter_CounterCooldown"])
            elif data.GetParam(1) == "set":
                if data.GetParamCount() > 2 and data.GetParam(2).isdigit():
                    Counter_List[cntr]["today"] = int(data.GetParam(2))
                    CBE.CBEAddCooldown(data, cntr + "_set", CBE.Config["Counter_CounterCooldown"])
                else:
                    CBE.SendTwitchMessage(CBE.stemp(CBE.Config["Counter_String_WholeNumber"]).safe_substitute())
                    return
            else:
                CBE.SendTwitchMessage(CBE.stemp(CBE.Config["CBE_String_UnknownParameter"]).safe_substitute(param=data.GetParam(1)))
                return
        else:
            CBE.CBEAddCooldown(data, cntr + "_show", CBE.Config["Counter_CounterCooldown"])
        WriteFormattedCounters()
        CBE.SendTwitchMessage(CBE.stemp(Counter_List[cntr]["format"]).safe_substitute(counter=cntr, today=str(Counter_List[cntr]["today"]), total=str(Counter_List[cntr]["total"] + Counter_List[cntr]["today"])))
    return

def ProcessCounters(data):
    if Counter_List is None:
        CBE.SendTwitchMessage(CBE.Config["Counter_String_AccessError"])
    else:
        if data.GetParamCount() > 1 and CBE.HasPermission(data.User, "moderator", data.User):
            if data.GetParam(1) == "add":
                if data.GetParamCount() > 2:
                    if data.GetParam(2) in Counter_List.keys():
                        CBE.SendTwitchMessage(CBE.Config["Counter_String_AlreadyExists"])
                    elif data.GetParam(2) in CBE.Commands.keys():
                        CBE.SendTwitchMessage(CBE.Config["Counter_String_CommandExists"])
                    else:
                        lower = data.GetParam(2).lower()
                        for c in lower:
                            if c not in string.ascii_lowercase:
                                CBE.SendTwitchMessage(CBE.Config["Counter_String_NonASCII"])
                                return
                        format = CBE.Config["Counter_String_DefaultFormat"]
                        if data.GetParamCount() > 3:
                            format = " ".join([data.GetParam(i) for i in range(3, data.GetParamCount())])
                        AddCounter(lower, format)
                        CBE.CBEAddCooldown(data, CBE.Config["Counter_CMDName"], CBE.Config["Counter_CMDCooldown"], CBE.Config["Counter_CMDIsGlobal"])
                else:
                    CBE.SendTwitchMessage(CBE.Config["CBE_String_MissingParameter"])
            elif data.GetParam(1) == "delete":
                if data.GetParamCount() > 2:
                    if data.GetParam(2).lower() in Counter_List.keys():
                        if data.GetParamCount() == 4 and data.GetParam(3) == "confirm":
                            DeleteCounter(data.GetParam(2).lower())
                            CBE.CBEAddCooldown(data, CBE.Config["Counter_CMDName"], CBE.Config["Counter_CMDCooldown"], CBE.Config["Counter_CMDIsGlobal"])
                        else:
                            CBE.SendTwitchMessage(CBE.Config["Counter_String_ConfirmNeeded"])
                    else:
                        CBE.SendTwitchMessage(CBE.stemp(CBE.Config["CBE_String_UnknownParameter"]).safe_substitute(param=data.GetParam(2)))
                else:
                    CBE.SendTwitchMessage(CBE.Config["CBE_String_MissingParameter"])
            else:
                CBE.SendTwitchMessage(CBE.stemp(CBE.Config["CBE_String_UnknownParameter"]).safe_substitute(param=data.GetParam(1)))
        else:
            CBE.SendTwitchMessage(CBE.stemp(CBE.Config["Counter_String_AvailableCounters"]).safe_substitute(list=CBE.Config["Counter_String_CounterJoin"].join(sorted(Counter_List.keys()))))
            CBE.CBEAddCooldown(data, CBE.Config["Counter_CMDName"], CBE.Config["Counter_CMDCooldown"], CBE.Config["Counter_CMDIsGlobal"])
    WriteFormattedCounters()
    return
#endregion