# -*- coding: utf-8 -*-
import codecs
import collections
import datetime
import json
import os
import string
import time
from CBEModule import CBEBaseFeatures, CBEModule

stemp = string.Template

def WorkaroundReloadSettings(cbeInstance):
    cbeInstance.CBEDebugLog("WorkaroundReloadSettings", "CBE")
    try:
        with codecs.open(os.path.join(cbeInstance.Path, cbeInstance.ConfigFile), encoding='utf-8-sig', mode='r') as file:
            load = json.load(file, encoding='utf-8-sig')
            dumps = json.dumps(load, ensure_ascii=False)
            cbeInstance.ReloadSettings(dumps)
    except Exception as e:
        cbeInstance.CBELogException("WorkaroundReloadSettings: " + str(e), "CBE")
    pass

def GetWorkaroundUI():
    return json.loads('{"btnWorkaround": {"type": "button", "label": "Reload Settings", "tooltip": "Manually reloads settings for CBE", "function": "WorkaroundReloadSettings", "wsevent": "EVENT_RELOAD_SETTINGS", "group": "ReloadSettings"}}')

class CBECommand(object):
    """A wrapper class for any command that gets registered at the Chatbot Engine."""
    def __init__(self, cmd, cd, args, glbl, usage, desc, callback):
        """
        Initialises a CBECommand instance with the given values.
        cmd: Command name (string)
        cd: Command cooldown (int)
        args: Has this command arguments? (bool)
        glbl: Is the cooldown global or user based? (bool)
        usage: A general usage description for this command (string)
        desc: A description of what this command does (string)
        """
        self.cmd = cmd
        self.cd = cd
        self.args = args
        self.glbl = glbl
        self.usage = usage
        self.desc = desc
        self.callback = callback

class ChatBotEngine(object):
    """
    A Chatbot Engine for Streamlabs Chatbot
    """
    def __init__(self, scriptName):
        self.ChatBotParent = None
        self.ScriptName = None
        self.Path = None
        self.UI = None

        self.ModuleList = []
        self.Commands = {}

        self.PreInitExceptionList = []
        self.PreInitLogList = []

        self.HelpCallbacks = []
        
        self.ConfigFile = "Data/CBE_config.json"
        self.Config = {}

        self.TimeStartingBot = -1.
        self.TimeGoingLive = -1.
        self.Path = os.path.dirname(__file__)
        self.ScriptName = scriptName
        self.UI = collections.OrderedDict()
        self.UI["output_file"] = self.ConfigFile

        try:
            with codecs.open(os.path.join(self.Path, self.ConfigFile), encoding='utf-8-sig', mode='r') as file:
                self.Config = json.load(file, encoding='utf-8-sig')
        except Exception as e:
            self.CBELogException("LoadConfig: " + str(e), "CBE")
        
        self.CheckConfigInternal(self.GetDefaultConfig())
        self.AddUIFromFile("UI/CBE_UI.json")
        self.RegisterModule(CBEBaseFeatures())
        return
    
    def GetDefaultConfig(self):
        tempDict = {}
        tempDict["CBE_ChatColor"] = "OrangeRed"
        tempDict["CBE_UseChatColor"] = True
        tempDict["CBE_DebugMode"] = False

        tempDict["CBE_String_UnknownParameter"] = "Unknown parameter: $param"
        tempDict["CBE_String_MissingParameter"] = "Missing parameter"
        tempDict["CBE_String_CommandAccessError"] = "Error accessing commands"
        tempDict["CBE_String_CooldownOnCooldown"] = "!$command is still on cooldown for $cooldown seconds"
        tempDict["CBE_String_CooldownOnUserCooldown"] = "!$command is still on cooldown for you for $cooldown seconds"
        return tempDict
    
    def CheckConfigInternal(self, configToCheck):
        for key in configToCheck.keys():
            if key not in self.Config.keys():
                self.Config[key] = configToCheck[key]

    def RegisterModule(self, module):
        if isinstance(module, CBEModule):
            module.cbe = self

            self.CheckConfigInternal(module.GetDefaultConfig())

            module.RegisterCommands()
            module.RegisterUI()
            module.RegisterHelp()
            self.ModuleList.append(module)
        return

    def AddUI(self, json):
        self.UI.update(json)
        return

    def AddUIFromFile(self, filename):
        try:
            with codecs.open(os.path.join(self.Path, filename), encoding='utf-8-sig', mode='r') as file:
                tempUI = json.load(file, encoding='utf-8-sig', object_pairs_hook=collections.OrderedDict)
                self.AddUI(tempUI)
        except Exception as e:
            self.CBELogException("AddUIFromFile: " + str(e), "CBE")
        return
    
    def LoadUIFromFile(self, filename):
        try:
            with codecs.open(os.path.join(self.Path, filename), encoding='utf-8-sig', mode='r') as file:
                tempUI = json.load(file, encoding='utf-8-sig', object_pairs_hook=collections.OrderedDict)
                return tempUI
        except Exception as e:
            self.CBELogException("LoadUIFromFile: " + str(e), "CBE")
    
    def AddCommand(self, command):
        self.Commands[command.cmd] = command
        self.CBEDebugLog("Available commands (" + str(len(self.Commands.keys())) + "): " + ", ".join([k + "(" + self.Commands[k].cmd + ")" for k in self.Commands.keys()]))
        return
    
    def RemoveCommand(self, commandName):
        del self.Commands[commandName]
        self.CBEDebugLog("Available commands (" + str(len(self.Commands.keys())) + "): " + ", ".join([k + "(" + self.Commands[k].cmd + ")" for k in self.Commands.keys()]))
        return

    def Finalize(self):
        self.AddUI(GetWorkaroundUI())
        try:
            with codecs.open(os.path.join(self.Path, "UI_Config.json"), encoding='utf-8-sig', mode='w') as file:
                json.dump(self.UI, file, encoding='utf-8-sig')
        except Exception as e:
            self.CBELogException("WriteUI: " + str(e), "CBE")
        return

    # -----------------------------------------------------------------------------------------------------------------------------------------------

    def GetStreamDuration(self):
        return (time.time() - self.TimeGoingLive) if self.TimeGoingLive != -1. else 0.

    def GetBotLifetime(self):
        return (time.time() - self.TimeStartingBot)
    
    def CBEDebugLog(self, message, scriptName=None):
        if (self.Config["CBE_DebugMode"]):
            self.Log("DEBUG:\n" + message)

    def CBELogException(self, message, scriptName=None):
        if self.ChatBotParent is None:
            self.PreInitExceptionList.append((message, scriptName))
        else:
            self.Log(message, "ER@" + scriptName)
    
    def PrintDataObject(self, data):
        s = "User: " + data.User
        s += "\nUserName: " + data.UserName
        s += "\nMessage: " + data.Message
        s += "\nRawData: " + data.RawData
        s += "\nService: " + data.Service
        s += "\nIsChatMessage(): " + str(data.IsChatMessage())
        s += "\nIsRawData(): " + str(data.IsRawData())
        s += "\nIsFromTwitch(): " + str(data.IsFromTwitch())
        s += "\nIsFromYoutube(): " + str(data.IsFromYoutube())
        s += "\nIsFromMixer(): " + str(data.IsFromMixer())
        s += "\nIsFromDiscord(): " + str(data.IsFromDiscord())
        s += "\nIsWhisper(): " + str(data.IsWhisper())
        s += "\nGetParamCount(): " + str(data.GetParamCount())
        for i in range(data.GetParamCount()):
            s += "\nGetParam(" + str(i) + "): " + str(data.GetParam(i))
        return s

    # -----------------------------------------------------------------------------------------------------------------------------------------------
    
    def CBEAddCooldown(self, data, command):
        if self.Commands[command].glbl:
            self.AddCooldown(self.ScriptName, command, self.Commands[command].cd)
        else:
            self.AddUserCooldown(self.ScriptName, command, data.User, self.Commands[command].cd)
        return

    def CBEIsOnCooldown(self, data, command):
        return self.IsOnCooldown(self.ScriptName, command) if self.Commands[command].glbl else self.IsOnUserCooldown(self.ScriptName, command, data.User)

    def CBEGetCooldown(self, data, command):
        return self.GetCooldownDuration(self.ScriptName, command) if self.Commands[command].glbl else self.GetUserCooldownDuration(self.ScriptName, command, data.User)
    
    def ProcessCommandCooldown(self, data, cmd):
        if self.GetDisplayName(data.User) != self.GetChannelName():
            cd = self.CBEGetCooldown(data, cmd)
            if self.CBEIsOnCooldown(data, cmd):
                if self.Commands[cmd].glbl:
                    self.SendTwitchMessage(stemp(self.Config["CBE_String_CooldownOnCooldown"]).safe_substitute(command=cmd, cooldown=str(cd)))
                else:
                    self.SendTwitchMessage(stemp(self.Config["CBE_String_CooldownOnUserCooldown"]).safe_substitute(command=cmd, cooldown=str(cd)), self.GetDisplayName(data.User))
                return False
        return True
    
    def GetCommandHelp(self, cmd):
        if cmd in self.Commands.keys():
            cmdict = self.Commands[cmd]
            d = dict(command=cmd, usage=cmdict.usage, cooldown=str(cmdict.cd), description=cmdict.desc, isGlobal=cmdict.glbl, hasArgs=cmdict.args)
            return stemp(self.Config["CBE_String_Help"]).safe_substitute(d)
        else:
            return stemp(self.Config["CBE_String_HelpUnknown"]).safe_substitute(command=cmd)

    # -----------------------------------------------------------------------------------------------------------------------------------------------

    # this is called as soon as the script loads like at the start of the bot or reloading the script
    def Init(self):
        self.CBEDebugLog("Init", "CBE")
        for e in self.PreInitExceptionList:
            self.CBELogException(e[0], e[1])
        self.PreInitExceptionList = []
        for e in self.PreInitLogList:
            self.Log(e[0], e[1])
        self.PreInitLogList = []

        self.TimeGoingLive = -1.
        self.TimeStartingBot = time.time()
        self.SendStreamMessage("/color " + self.Config["CBE_ChatColor"])
        for module in self.ModuleList:
            module.Init()
        return

    # this is called as soon as a message arrives in the chat
    def Execute(self, data):
        if (self.Config["CBE_DebugMode"]):
            self.CBEDebugLog(self.PrintDataObject(data))
        if data.IsChatMessage() and data.Message.startswith("!"):
            self.CBEDebugLog("Execute: " + data.Message, "CBE")
            if self.Commands is None:
                self.SendTwitchMessage(self.Config["CBE_String_CommandAccessError"])
            else:
                for command in self.Commands.keys():
                    if ((self.Commands[command].args and data.GetParam(0) == "!" + command) or (not self.Commands[command].args and data.Message == "!" + command)):
                        if self.ProcessCommandCooldown(data, command) and self.Commands[command].callback(data):
                            self.CBEAddCooldown(data, command)
                            break
        for module in self.ModuleList:
            module.Execute(data)
        return

    # this is called every "frame" of the bot regardless of the input
    def Tick(self):
        if self.TimeGoingLive == -1. and (self.IsLive() or self.Config["CBE_DebugMode"]):
            self.TimeGoingLive = time.time()
        for module in self.ModuleList:
            module.Tick()
        return

    # this is called when the script is toggled in the bot ui
    def ScriptToggled(self, state):
        self.CBEDebugLog("ScriptToggled", "CBE")
        self.TimeGoingLive = -1.
        self.TimeStartingBot = time.time()
        for module in self.ModuleList:
            module.ScriptToggled(state)
        return

    # this is called when the script gets reloaded, deactivated or the bot gets closed
    def Unload(self):
        self.CBEDebugLog("Unload", "CBE")
        for module in self.ModuleList:
            module.Unload()
        return

    # this may be used to create custom parameters
    def Parse(self, parseString, userid, username, targetid, targetname, message):
        self.CBEDebugLog("Parse", "CBE")
        for module in self.ModuleList:
            parseString = module.Parse(parseString, userid, username, targetid, targetname, message)
        return parseString

    # this is called when the user clicks on the save button in the scripts tab
    def ReloadSettings(self, jsonData):
        self.CBEDebugLog("ReloadSettings", "CBE")
        self.CBEDebugLog(jsonData, "...")
        self.Config = json.loads(jsonData)
        self.CheckConfigInternal(self.GetDefaultConfig())
        self.SendStreamMessage("/color " + self.Config["CBE_ChatColor"])
        
        for module in self.ModuleList:
            module.ReloadSettings(jsonData)
        return

    # -----------------------------------------------------------------------------------------------------------------------------------------------
    # chaining of streamlabs chatbot api
    def AddPoints(self, userid, username, amount):
        return self.ChatBotParent.AddPoints(userid, username, amount)

    def AddPointsAll(self, data):
        return self.ChatBotParent.AddPointsAll(data)

    def AddPointsAllAsync(self, data, callback):
        return self.ChatBotParent.AddPointsAllAsync(data, callback)

    def RemovePoints(self, userid, username, amount):
        return self.ChatBotParent.RemovePoints(userid, username, amount)

    def RemovePointsAll(self, data):
        return self.ChatBotParent.RemovePointsAll(data)

    def RemovePointsAllAsync(self, data, callback):
        return self.ChatBotParent.RemovePointsAllAsync(data, callback)

    def GetPoints(self, userid):
        return self.ChatBotParent.GetPoints(userid)

    def GetHours(self, userid):
        return self.ChatBotParent.GetHours(userid)

    def GetRank(self, userid):
        return self.ChatBotParent.GetRank(userid)

    def GetTopCurrency(self, top):
        return self.ChatBotParent.GetTopCurrency(top)

    def GetTopHours(self, top):
        return self.ChatBotParent.GetTopHours(top)

    def GetPointsAll(self, userids):
        return self.ChatBotParent.GetPointsAll(userids)

    def GetRanksAll(self, userids):
        return self.ChatBotParent.GetRanksAll(userids)

    def GetHoursAll(self, userids):
        return self.ChatBotParent.GetHoursAll(userids)

    def GetCurrencyUsers(self, userids):
        return self.ChatBotParent.GetCurrencyUsers(userids)

    def SendStreamMessage(self, message):
        self.ChatBotParent.SendStreamMessage(message)

    def SendStreamWhisper(self, target, message):
        self.ChatBotParent.SendStreamMessage(target, message)

    def SendDiscordMessage(self, message):
        self.ChatBotParent.SendDiscordMessage(message)

    def SendDiscordDM(self, target, message):
        self.ChatBotParent.SendDiscordDM(target, message)

    def SendTwitchMessage(self, msg, whisper=None):
        msgs = []
        if len(msg) > 444:
            i = 0
            while len(msg) > i * 444:
                msgs.append(msg[i*444:min((i+1)*444, len(msg))])
                i += 1
        else:
            msgs = [msg]
        for m in msgs:
            if whisper is None:
                self.ChatBotParent.SendStreamMessage((("/me " if self.Config["CBE_UseChatColor"] else "") + m))
            else:
                self.ChatBotParent.SendStreamWhisper(whisper, m)

    def BroadcastWsEvent(self, eventName, jsonData):
        self.ChatBotParent.BroadcastWsEvent(eventName, jsonData)

    def HasPermission(self, userid, permission, info):
        return self.ChatBotParent.HasPermission(userid, permission, info)

    def GetViewerList(self):
        return self.ChatBotParent.GetViewerList()

    def GetActiveUsers(self):
        return self.ChatBotParent.GetActiveUsers()

    def GetRandomActiveUser(self):
        return self.ChatBotParent.GetRandomActiveUser()

    def GetDisplayName(self, userid):
        return self.ChatBotParent.GetDisplayName(userid)

    def GetDisplayNames(self, userids):
        return self.ChatBotParent.GetDisplayNames(userids)

    def AddCooldown(self, scriptName, command, seconds):
        self.ChatBotParent.AddCooldown(scriptName, command, seconds)

    def IsOnCooldown(self, scriptName, command):
        return self.ChatBotParent.IsOnCooldown(scriptName, command)

    def GetCooldownDuration(self, scriptName, command):
        return self.ChatBotParent.GetCooldownDuration(scriptName, command)

    def AddUserCooldown(self, scriptName, command, userid, seconds):
        self.ChatBotParent.AddUserCooldown(scriptName, command, userid, seconds)

    def IsOnUserCooldown(self, scriptName, command, userid):
        return self.ChatBotParent.IsOnUserCooldown(scriptName, command, userid)

    def GetUserCooldownDuration(self, scriptName, command, userid):
        return self.ChatBotParent.GetUserCooldownDuration(scriptName, command, userid)

    def SetOBSCurrentScene(self, sceneName, callback=None):
        self.ChatBotParent.SetOBSCurrentScene(sceneName, callback)

    def SetOBSSourceRender(self, source, render, sceneName=None, callback=None):
        self.ChatBotParent.SetOBSSourceRender(source, render, sceneName, callback)

    def StopOBSStreaming(self, callback=None):
        self.ChatBotParent.StopOBSStreaming(callback)

    def GetOBSSpecialSources(self, callback):
        self.ChatBotParent.GetOBSSpecialSources(callback)

    def SetOBSVolume(self, source, volume, callback=None):
        self.ChatBotParent.SetOBSVolume(source, volume, callback)

    def GetOBSMute(self, source, callback):
        self.ChatBotParent.GetOBSMute(source, callback)

    def SetOBSMute(self, source, mute, callback=None):
        self.ChatBotParent.SetOBSMute(source, mute, callback)

    def ToggleOBSMute(self, source, callback=None):
        self.ChatBotParent.ToggleOBSMute(source, callback)

    def GetRequest(self, url, headers):
        return self.ChatBotParent.GetRequest(url, headers)

    def PostRequest(self, url, headers, content, isJsonContent=True):
        return self.ChatBotParent.PostRequest(url, headers, content, isJsonContent)

    def DeleteRequest(self, url, headers):
        return self.ChatBotParent.DeleteRequest(url, headers)

    def PutRequest(self, url, header, content, isJsonContent=True):
        return self.ChatBotParent.PutRequest(url, header, content, isJsonContent)

    def IsLive(self):
        return self.ChatBotParent.IsLive()

    def GetRandom(self, vmin, vmax):
        return self.ChatBotParent.GetRandom(vmin, vmax)

    def GetStreamingService(self):
        return self.ChatBotParent.GetStreamingService()

    def GetChannelName(self):
        return self.ChatBotParent.GetChannelName()

    def GetCurrencyName(self):
        return self.ChatBotParent.GetCurrencyName()

    def Log(self, message, scriptName=None):
        message = datetime.datetime.now().isoformat(" ") + "\n" + message
        if self.ChatBotParent is None:
            self.PreInitLogList.append((message, scriptName))
        else:
            self.ChatBotParent.Log((self.ScriptName if scriptName is None else scriptName), message)

    def PlaySound(self, filePath, volume):
        return self.ChatBotParent.PlaySound(filePath, volume)

    def GetQueue(self, vmax):
        return self.ChatBotParent.GetQueue(vmax)

    def GetSongQueue(self, vmax):
        return self.ChatBotParent.GetSongQueue(vmax)

    def GetSongPlaylist(self, vmax):
        return self.ChatBotParent.GetSongPlaylist(vmax)

    def GetNowPlaying(self):
        return self.ChatBotParent.GetNowPlaying()