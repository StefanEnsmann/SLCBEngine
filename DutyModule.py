# -*- coding: utf-8 -*-
import CBE

class Duty(CBE.CBEModule):
    def __init__(self):
        self.Duties = []
        self.Amounts = []

    def RegisterCommands(self):
        self.cbe.Log("RegisterCommands", "Duty")
        cfg = self.cbe.Config
        self.cmdCMD = CBE.CBECommand(cfg["Duty_CMDName"], cfg["Duty_Cooldown"], True, cfg["Duty_IsGlobal"], cfg["Duty_Usage"], cfg["Duty_Description"], self.ProcessDuty)
        self.cbe.AddCommand(self.cmdCMD)
        return

    def RegisterUI(self):
        self.cbe.Log("RegisterUI", "Duty")
        self.cbe.AddUIFromFile("UI/DutyModule_UI.json")
        return

    def RegisterHelp(self):
        self.cbe.Log("RegisterHelp", "Duty")
        return

    # these methods will ALWAYS be called when the module is registered at the chatbot
    def GetDefaultConfig(self):
        self.cbe.Log("GetDefaultConfig", "Duty")
        tempDict = {
            "Duty_CMDName": "duty",
            "Duty_Cooldown": 1800,
            "Duty_IsGlobal": True,
            "Duty_Usage": "!duty",
            "Duty_Description": "Generates a duty the streamer has to do",
            "Duty_Response": "Streamer has to {amount} {duty}",
            "Duty_Duties": "Duty 1;Duty 2;Duty 3",
            "Duty_Amounts": "1;2;3;4",
        }
        return tempDict
    
    def ProcessDuty(self, data):
        if len(self.Duties) > 0 and len(self.Amounts) > 0:
            n_duty = self.cbe.GetRandom(0, len(self.Duties))
            n_amount = self.cbe.GetRandom(0, len(self.Amounts))
            s = self.cbe.Config["Duty_Response"].replace("{duty}", self.Duties[n_duty]).replace("{amount}", self.Amounts[n_amount])
            self.cbe.SendTwitchMessage(s)
        else:
            self.cbe.LogException("No Duties or no Amounts defined: " + str(self.Duties) + " " + str(self.Amounts), "Duty")
            return False
        return True
    
    def Init(self):
        self.ParseParams()

    def ParseParams(self):
        if self.cbe.Config["Duty_Duties"] == "":
            self.cbe.LogException("Duty string is empty!", "Duty")
            self.Duties = []
        else:
            self.Duties = self.cbe.Config["Duty_Duties"].split(";")
            
        if self.cbe.Config["Duty_Amounts"] == "":
            self.cbe.LogException("Amounts string is empty!", "Duty")
            self.Amounts = []
        else:
            self.Amounts = self.cbe.Config["Duty_Amounts"].split(";")

    def ReloadSettings(self, jsonData):
        self.cbe.RemoveCommand(self.cmdCMD.cmd)
        self.RegisterCommands()
        self.ParseParams()
