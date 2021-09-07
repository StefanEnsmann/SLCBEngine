# -*- coding: utf-8 -*-
# modules
import os
import codecs
import time
import CBE

class Joke(CBE.CBEModule):
    Joke_NextJokeTime = -1
    _cmdName = ""

    Joke_File = "jokes.txt"
    Joke_List = []

    def CheckConfig(self):
        tempDict = {}
        tempDict["Joke_CommandName"] = "joke"
        tempDict["Joke_CommandCooldown"] = 120
        tempDict["Joke_CommandIsGlobalCooldown"] = True
        tempDict["Joke_CommandUsage"] = "!joke"
        tempDict["Joke_CommandDescription"] = "Gives you a joke"
        
        tempDict["Joke_UseTimer"] = False
        tempDict["Joke_JokeInterval"] = 27 * 60
        tempDict["Joke_NoJokeAvailable"] = "There are no jokes in the database"
        for key in tempDict.keys():
            if key not in self.cbe.Config.keys():
                self.cbe.Config[key] = tempDict[key]
        return

    def RegisterUI(self):
        self.cbe.AddUIFromFile("JokeModule_UI.json")
        return
    
    def RegisterCommands(self):
        self._cmdName = self.cbe.Config["Joke_CommandName"]
        self.cbe.AddCommand(self.cbe.Config["Joke_CommandName"], "Joke_CommandCooldown", "Joke_CommandIsGlobalCooldown", False, "Joke_CommandUsage", "Joke_CommandDescription", self.ProcessJoke)
        return
    
    def RegisterHelp(self):
        return

    def Init(self):
        self.LoadJokes()
        self.Joke_NextJokeTime = self.cbe.Config["Joke_JokeInterval"]

    def Tick(self):
        if self.cbe.Config["Joke_UseTimer"] and len(self.Joke_List) > 0 and (self.cbe.GetStreamDuration() > self.Joke_NextJokeTime):
            self.Joke_NextJokeTime += self.cbe.Config["Joke_JokeInterval"]
            self.SendJoke()
        return

    def ScriptToggled(self, state):
        self.Joke_NextJokeTime = self.cbe.Config["Joke_JokeInterval"]
        if state:
            self.LoadJokes()

    def Unload(self):
        self.LoadJokes()

    def ReloadSettings(self, jsonData):
        if self._cmdName != self.cbe.Config["Joke_CommandName"]:
            self.cbe.RemoveCommand(self._cmdName)
            self.RegisterCommands()
            self.Joke_NextJokeTime = self.cbe.GetStreamDuration() + self.cbe.Config["Joke_JokeInterval"]

    def ProcessJoke(self, data):
        if len(self.Joke_List) > 0:
            self.SendJoke()
            self.Joke_NextJokeTime = self.cbe.GetStreamDuration() + self.cbe.Config["Joke_JokeInterval"]
        else:
            self.cbe.SendTwitchMessage(self.cbe.Config["Joke_NoJokeAvailable"])
        return True

    def LoadJokes(self):
        try:
            with codecs.open(os.path.join(self.cbe.Path, self.Joke_File), encoding="utf-8-sig", mode="r") as jf:
                content = jf.readlines()
                self.Joke_List = [joke.strip() for joke in content]
        except:
            self.Joke_List = []
    
    def SendJoke(self):
        self.cbe.SendTwitchMessage(self.Joke_List[self.cbe.GetRandom(0, len(self.Joke_List))])