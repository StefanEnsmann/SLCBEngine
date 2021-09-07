# -*- coding: utf-8 -*-
import os
import codecs
import json
import collections
import CBE

class ResponseModule(CBE.CBEModule):
    def __init__(self, cbe, id):
        super(ResponseModule, self).__init__(cbe)
        self.LastResponse = 0.
        self.id = id

    def CheckConfig(self):
        tempDict = {}
        tempDict["Response_" + str(self.id) + "_Phrase"] = "F"
        tempDict["Response_" + str(self.id) + "_Cooldown"] = 120
        for key in tempDict.keys():
            if key not in self.cbe.Config.keys():
                self.cbe.Config[key] = tempDict[key]
        return
    
    def RegisterUI(self):
        try:
            with codecs.open(os.path.join(self.cbe.Path, "ResponseModule_UI.json"), encoding='utf-8-sig', mode='r') as file:
                tempUI = json.load(file, encoding='utf-8-sig', object_pairs_hook=collections.OrderedDict)
                oldkeys = [key for key in tempUI]
                for key in oldkeys:
                    nkey = key.replace("Response_", "Response_" + str(self.id) + "_", 1)
                    tempUI[key]["group"] = tempUI[key]["group"].replace("Response", "Response " + str(self.id), 1)
                    tempUI[nkey] = tempUI[key]
                    del tempUI[key]

                self.cbe.AddUI(tempUI)
        except Exception as e:
            self.cbe.ExceptionList.append("LoadUI: " + str(e))
        return
    
    def RegisterCommands(self):
        return
    
    def RegisterHelp(self):
        return

    def Execute(self, data):
        if data.IsChatMessage() and data.Message.upper().startswith(self.cbe.Config["Response_" + str(self.id) + "_Phrase"].upper()) and len(data.Message) < len(self.cbe.Config["Response_" + str(self.id) + "_Phrase"]) + 2 and ((self.cbe.GetBotLifetime() - self.LastResponse) >= self.cbe.Config["Response_" + str(self.id) + "_Cooldown"] or self.LastResponse == 0.):
            self.cbe.SendTwitchMessage(data.Message[:len(self.cbe.Config["Response_" + str(self.id) + "_Phrase"])])
            self.LastResponse = self.cbe.GetBotLifetime()

    def Unload(self):
        self.LastResponse = 0.
        return

    def ReloadSettings(self, jsonData):
        self.CheckConfig()
        self.LastResponse = 0.
        return