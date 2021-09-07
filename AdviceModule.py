# -*- coding: utf-8 -*-
import os
import json
import CBE

class AdviceModule(CBE.CBEModule):
    def __init__(self):
        self.adviceCMD = None

    def GetDefaultConfig(self):
        tempDict = {
            "AD_CMDName": "advice",
            "AD_CMDCooldown": 30,
            "AD_CMDIsGlobal": True,
            "AD_CMDUsage": "!advice (Cost: 300)",
            "AD_CMDDescription": "Shows you a valuable advice",
            "AD_Cost": 300,
            "AD_FreeForMods": True,
            "AD_NotEnoughCurrency": "$user, you need $cost $currencyname to do this!"
        }
        return tempDict

    def RegisterUI(self):
        self.cbe.AddUIFromFile("UI/AdviceModule_UI.json")
        return 
    
    def RegisterCommands(self):
        cfg = self.cbe.Config
        self.adviceCMD = CBE.CBECommand(cfg["AD_CMDName"], cfg["AD_CMDCooldown"], False, cfg["AD_CMDIsGlobal"], cfg["AD_CMDUsage"], cfg["AD_CMDDescription"], self.GetAdvice)
        self.cbe.AddCommand(self.adviceCMD)
        return
    
    def RegisterHelp(self):
        return

    def ReloadSettings(self, jsonData):
        self.cbe.CBEDebugLog("ReloadSettings", "AdviceModule")
        self.cbe.RemoveCommand(self.adviceCMD.cmd)
        self.RegisterCommands()
    
    def GetAdvice(self, data):
        self.cbe.CBEDebugLog("GetAdvice", "AdviceModule")
        points = self.cbe.GetPoints(data.User)
        cost = self.cbe.Config["AD_Cost"]
        isBroadcaster = (data.UserName.lower() == self.cbe.GetChannelName().lower())
        if points >= cost or isBroadcaster:
            response = self.cbe.GetRequest("https://api.adviceslip.com/advice", {})
            parsed = json.loads(response)
            self.cbe.CBEDebugLog(str(parsed), "AdviceModule")
            self.cbe.CBEDebugLog(str(parsed["response"]), "AdviceModule")
            status = parsed["status"]
            parsed = json.loads(parsed["response"])
            self.cbe.CBEDebugLog(str(parsed["slip"]), "AdviceModule")
            self.cbe.CBEDebugLog(str(parsed["slip"]["advice"]), "AdviceModule")
            if status == 200:
                if not isBroadcaster:
                    self.cbe.RemovePoints(data.User, data.UserName, cost)
                self.cbe.SendTwitchMessage(parsed["slip"]["advice"])
            else:
                self.cbe.SendTwitchMessage("Error while fetching advice!")
        else:
            poorMessage = CBE.stemp(self.cbe.Config["AD_NotEnoughCurrency"]).safe_substitute(user=data.UserName, cost=cost, currencyname=self.cbe.GetCurrencyName())
            self.cbe.SendTwitchMessage(poorMessage)