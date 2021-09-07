# -*- coding: utf-8 -*-
import os
import json
import CBE

class DiscordPointsModule(CBE.CBEModule):
    def __init__(self):
        self.useExecute = True

    def GetDefaultConfig(self):
        return {}

    def RegisterUI(self):
        return 
    
    def RegisterCommands(self):
        return
    
    def RegisterHelp(self):
        return

    def Execute(self, data):
        currencyName = self.cbe.GetCurrencyName()
        currency = self.cbe.GetPoints(data.User)
        self.cbe.CBEDebugLog("Discord " + currencyName + " " + str(currency), "DiscordPointsModule")
        if (data.IsFromDiscord() and data.Message == "!" + currencyName.lower()):
            if (data.IsWhisper()):
                self.cbe.SendDiscordDM(data.User, "Du hast " + str(currency) + " " + currencyName)
            else:
                self.cbe.SendDiscordMessage(data.UserName + " hat " + str(currency) + " " + currencyName)
        return