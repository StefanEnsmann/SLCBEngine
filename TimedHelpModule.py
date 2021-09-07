# -*- coding: utf-8 -*-
import CBE

class TimedHelp(CBE.CBEModule):
    TimedHelp_LastHelpTime = -1

    def __init__(self, cbe):
        super(TimedHelp, self).__init__(cbe)
        self.useTick = True
        self.useScriptToggled = True

    def CheckConfig(self):
        tempDict = {"TimedHelp_Interval": 17 * 60, "TimedHelp_Message": "$help (!commands for a list of all commands)"}
        for key in tempDict.keys():
            if key not in self.cbe.Config.keys():
                self.cbe.Config[key] = tempDict[key]
        return

    def RegisterHelp(self):
        return

    def RegisterCommands(self):
        return

    def RegisterUI(self):
        self.cbe.AddUIFromFile("TimedHelpModule_UI.json")
        return
    
    def Tick(self):
        if self.cbe.GetBotLifetime() - self.TimedHelp_LastHelpTime > self.cbe.Config["TimedHelp_Interval"]:
            self.TimedHelp_LastHelpTime = self.cbe.GetBotLifetime()
            cmd = self.cbe.Commands.keys()[self.cbe.GetRandom(0, len(self.cbe.Commands.keys()))]
            while len(self.cbe.Commands.keys()) > 1 and cmd == self.cbe.Config["CBE_CommandsName"]:
                cmd = self.cbe.Commands.keys()[self.cbe.GetRandom(0, len(self.cbe.Commands.keys()))]
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["TimedHelp_Message"]).safe_substitute(help=self.cbe.GetCommandHelp(cmd)))
        return

    def ScriptToggled(self, state):
        self.TimedHelp_LastHelpTime = 0.
        return