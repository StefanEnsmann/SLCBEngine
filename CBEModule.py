# -*- coding: utf-8 -*-
import CBE

class CBEModule(object):
    cbe = None
    
    def Init(self):
        return
    def Execute(self, data):
        return
    def Tick(self):
        return
    def Parse(self, parseString, userid, username, targetid, targetname, message):
        return parseString
    def ReloadSettings(self, jsonData):
        return
    def Unload(self):
        return
    def ScriptToggled(self, state):
        return

    # these methods will ALWAYS be called when the module is registered at the chatbot
    def GetDefaultConfig(self):
        raise NotImplementedError
    def RegisterCommands(self):
        raise NotImplementedError
    def RegisterUI(self):
        raise NotImplementedError
    def RegisterHelp(self):
        raise NotImplementedError

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CBEBaseFeatures(CBEModule):
    def __init__(self):
        self.UI_File = "UI/CBEModule_UI.json"
        self.commandsCMD = None
        self.cooldownCMD = None
        self.helpCMD = None
        return

    def RegisterCommands(self):
        self.cbe.CBEDebugLog("RegisterCommands", "CBEBaseFeatures")
        cfg = self.cbe.Config
        self.commandsCMD = CBE.CBECommand(cfg["CBE_CommandsName"], cfg["CBE_CommandsCooldown"], False, cfg["CBE_CommandsIsGlobal"], cfg["CBE_CommandsUsage"], cfg["CBE_CommandsDescription"], self.ProcessCommands)
        self.cooldownCMD = CBE.CBECommand(cfg["CBE_CooldownName"], cfg["CBE_CooldownCooldown"], False, cfg["CBE_CooldownIsGlobal"], cfg["CBE_CooldownUsage"], cfg["CBE_CooldownDescription"], self.ProcessCooldown)
        self.helpCMD = CBE.CBECommand(cfg["CBE_HelpName"], cfg["CBE_HelpCooldown"], True, cfg["CBE_HelpIsGlobal"], cfg["CBE_HelpUsage"], cfg["CBE_HelpDescription"], self.ProcessHelp)
        
        self.cbe.AddCommand(self.commandsCMD)
        self.cbe.AddCommand(self.cooldownCMD)
        self.cbe.AddCommand(self.helpCMD)
        return

    def RegisterUI(self):
        self.cbe.CBEDebugLog("RegisterUI", "CBEBaseFeatures")
        self.cbe.AddUIFromFile(self.UI_File)

    def RegisterHelp(self):
        self.cbe.CBEDebugLog("RegisterHelp", "CBEBaseFeatures")
        return

    def GetDefaultConfig(self):
        self.cbe.CBEDebugLog("GetDefaultConfig", "CBEBaseFeatures")
        tempDict = {}

        tempDict["CBE_CommandsName"] = "commands"
        tempDict["CBE_CommandsCooldown"] = 10
        tempDict["CBE_CommandsIsGlobal"] = True
        tempDict["CBE_CommandsUsage"] = "!commands"
        tempDict["CBE_CommandsDescription"] = "Shows all available commands"
        tempDict["CBE_String_CommandJoin"] = ", "

        tempDict["CBE_CooldownName"] = "cooldown"
        tempDict["CBE_CooldownCooldown"] = 30
        tempDict["CBE_CooldownIsGlobal"] = True
        tempDict["CBE_CooldownUsage"] = "!cooldown"
        tempDict["CBE_CooldownDescription"] = "Shows current status of all commands"
        tempDict["CBE_String_CooldownFormat"] = "!$command ($cooldown s)"
        tempDict["CBE_String_CooldownNoCommandsOnCooldown"] = "There are no commands on cooldown"
        tempDict["CBE_String_CooldownCurrentlyOnCooldown"] = "Currently on cooldown: $list"
        tempDict["CBE_String_CooldownCurrentlyOnUserCooldown"] = "Currently on cooldown for you: $list"
        tempDict["CBE_String_CooldownJoin"] = " ||| "

        tempDict["CBE_HelpName"] = "help"
        tempDict["CBE_HelpCooldown"] = 10
        tempDict["CBE_HelpIsGlobal"] = True
        tempDict["CBE_HelpUsage"] = "!help <command>"
        tempDict["CBE_HelpDescription"] = "Shows help for the given command"
        tempDict["CBE_String_Help"] = "$usage (Cooldown $cooldown seconds): $description"
        tempDict["CBE_String_HelpUnknown"] = "$command is no known command"
        return tempDict
    
    def ReloadSettings(self, jsonData):
        self.cbe.CBEDebugLog("ReloadSettings", "CBEBaseFeatures")
        self.cbe.RemoveCommand(self.commandsCMD.cmd)
        self.cbe.RemoveCommand(self.cooldownCMD.cmd)
        self.cbe.RemoveCommand(self.helpCMD.cmd)
        self.RegisterCommands()

    def ProcessCommands(self, data):
        self.cbe.CBEDebugLog("ProcessCommands", "CBEBaseFeatures")
        self.cbe.SendTwitchMessage(self.cbe.Config["CBE_String_CommandJoin"].join([self.cbe.Commands[key].usage for key in sorted(self.cbe.Commands.keys())]))
        return True
    
    def ProcessHelp(self, data):
        self.cbe.CBEDebugLog("ProcessHelp", "CBEBaseFeatures")
        if data.GetParamCount() > 1:
            arg0 = data.GetParam(1)
            if arg0.startswith("!"):
                arg0 = arg0[1:]
            if arg0 in self.cbe.Commands.keys():
                self.cbe.SendTwitchMessage(self.cbe.GetCommandHelp(arg0))
                return True

            for helpCallback in self.cbe.HelpCallbacks:
                if helpCallback(data):
                    return True
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["CBE_String_UnknownParameter"]).safe_substitute(param=data.GetParam(1)))
        else:
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["CBE_String_MissingParameter"]).safe_substitute())
        return False

    def ProcessCooldown(self, data):
        self.cbe.CBEDebugLog("ProcessCooldown", "CBEBaseFeatures")
        onCooldown = []
        onUserCooldown = []
        for command in sorted(self.cbe.Commands.keys()):
            if self.cbe.CBEIsOnCooldown(data, command):
                if self.cbe.Commands[command].glbl:
                    onCooldown.append(CBE.stemp(self.cbe.Config["CBE_String_CooldownFormat"]).safe_substitute(command=command, cooldown=str(self.cbe.CBEGetCooldown(data, command))))
                else:
                    onUserCooldown.append(CBE.stemp(self.cbe.Config["CBE_String_CooldownFormat"]).safe_substitute(command=command, cooldown=str(self.cbe.CBEGetCooldown(data, command))))
        if len(onCooldown) == 0:
            self.cbe.SendTwitchMessage(self.cbe.Config["CBE_String_CooldownNoCommandsOnCooldown"])
        else:
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["CBE_String_CooldownCurrentlyOnCooldown"]).safe_substitute(list=self.cbe.Config["CBE_String_CooldownJoin"].join(onCooldown)))
        if len(onUserCooldown) > 0:
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["CBE_String_CooldownCurrentlyOnUserCooldown"]).safe_substitute(list=self.cbe.Config["CBE_String_CooldownJoin"].join(onUserCooldown)), self.cbe.GetDisplayName(data.User))
        return True