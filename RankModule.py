# -*- coding: utf-8 -*-
import CBE

class RankModule(CBE.CBEModule):
    _cmdName = ""

    def CheckConfig(self):
        tempDict = {
            "Rank_CMDName": "rank",
            "Rank_CMDCooldown": 60,
            "Rank_CMDIsGlobal": False,
            "Rank_CMDUsage": "!rank [userid]",
            "Rank_CMDDescription": "Shows the rank for the given user in the leaderboard (or the own, if none given)",
            "Rank_CMDResponse": "$name is in place $rank with $currency $currencyname",
            "Rank_CMDNoCurrencyYet": "$name has no $currencyname yet...",
            "Rank_CMDFetchNumber": 100
        }
        for key in tempDict.keys():
            if key not in self.cbe.Config.keys():
                self.cbe.Config[key] = tempDict[key]
        return

    def RegisterHelp(self):
        return

    def RegisterCommands(self):
        self._cmdName = self.cbe.Config["Rank_CMDName"]
        self.cbe.AddCommand(self.cbe.Config["Rank_CMDName"], "Rank_CMDCooldown", "Rank_CMDIsGlobal", True, "Rank_CMDUsage", "Rank_CMDDescription", self.ProcessRank)
        return

    def RegisterUI(self):
        self.cbe.AddUIFromFile("RankModule_UI.json")
        return

    def ReloadSettings(self, jsonData):
        self.CheckConfig()
        if self._cmdName != self.cbe.Config["Rank_CMDName"]:
            self.cbe.RemoveCommand(self._cmdName)
            self.RegisterCommands()

    def ProcessRank(self, data):
        usr = data.User
        if data.GetParamCount() > 1:
            usr = data.GetParam(1).lower()
        usrname = self.cbe.GetDisplayName(usr)
        currency = self.cbe.GetPoints(usr)
        if currency > 0:
            rank = ">" + str(self.cbe.Config["Rank_CMDFetchNumber"])
            dic = self.cbe.GetTopCurrency(self.cbe.Config["Rank_CMDFetchNumber"])
            listed = [(key, dic[key]) for key in dic.keys()]
            listed.sort(cmp=lambda x,y: 1 if x[1] > y[1] else (0 if x[1] == y[1] else -1), reverse=True)
            pos = 0
            for elem in listed:
                pos += 1
                if elem[0] == usr:
                    rank = str(pos)
                    break
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["Rank_CMDResponse"]).safe_substitute(name=usrname, rank=str(rank), currency=str(currency), currencyname=self.cbe.GetCurrencyName()))
        else:
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["Rank_CMDNoCurrencyYet"]).safe_substitute(name=usrname, currencyname=self.cbe.GetCurrencyName()))
        return True