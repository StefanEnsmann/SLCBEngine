# -*- coding: utf-8 -*-
import CBE

class DummyCommand(CBE.CBEModule):
    def __init__(self, id):
        self.id = id
        self.UI_File = "UI/DummyCommand_UI.json"
        self.dummyCMD = None
        return

    def RegisterCommands(self):
        self.cbe.CBEDebugLog("RegisterCommands", "DummyCommand")
        cfg = self.cbe.Config
        self.dummyCMD = CBE.CBECommand(cfg["Dummy_CMDName" + str(self.id)], cfg["Dummy_CMDCooldown" + str(self.id)], False, cfg["Dummy_CMDIsGlobal" + str(self.id)], cfg["Dummy_CMDUsage" + str(self.id)], cfg["Dummy_CMDDescription" + str(self.id)], self.ProcessDummy)
        
        self.cbe.AddCommand(self.dummyCMD)
        return

    def RegisterUI(self):
        self.cbe.CBEDebugLog("RegisterUI", "DummyCommand")
        json = self.cbe.LoadUIFromFile(self.UI_File)
        for k in json.keys():
            json[k]["group"] = json[k]["group"] + " " + str(self.id)
            json[k + str(self.id)] = json[k]
            del json[k]
        self.cbe.AddUI(json)

    def RegisterHelp(self):
        self.cbe.CBEDebugLog("RegisterHelp", "DummyCommand")
        return

    def GetDefaultConfig(self):
        self.cbe.CBEDebugLog("GetDefaultConfig", "DummyCommand")
        tempDict = {}

        tempDict["Dummy_CMDName" + str(self.id)] = "Insert command name here"
        tempDict["Dummy_CMDCooldown" + str(self.id)] = 10
        tempDict["Dummy_CMDIsGlobal" + str(self.id)] = False
        tempDict["Dummy_CMDUsage" + str(self.id)] = "Insert command usage here"
        tempDict["Dummy_CMDDescription" + str(self.id)] = "Insert command description here"

        return tempDict
    
    def ReloadSettings(self, jsonData):
        self.cbe.CBEDebugLog("ReloadSettings", "DummyCommand")
        self.cbe.RemoveCommand(self.dummyCMD.cmd)
        self.RegisterCommands()
    
    def ProcessDummy(self, data):
        return