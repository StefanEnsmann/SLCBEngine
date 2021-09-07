# -*- coding: utf-8 -*-
# modules
import CBE
import os
import json
import datetime
import locale

class CSW(CBE.CBEModule):
    def __init__(self):
        self.CSWUsers = []
        self.Headers = {'Authorization': 'Bearer FDF7u89fdC998875c8d7f'}
        self._lastLinkedUser = None
        self.CSWEventsFile = "Text/CSWEvents.txt"
        self.CSWEventsFileOneLine = "Text/CSWEventsOneLine.txt"
        self.CSWEventsFileMultiLine = "Text/CSWEventsMultiLine.txt"
        self.NextWriteTime = 0.
        self.ParseEventsVersion = 2

        #self.cmdCMD = None
        #self.linkCMD = None
        self.eventsCMD = None

    def RegisterCommands(self):
        self.cbe.CBEDebugLog("RegisterCommands", "CSW")
        cfg = self.cbe.Config
        #self.cmdCMD = CBE.CBECommand(cfg["CSW_CMDName"], cfg["CSW_CMDCooldown"], True, cfg["CSW_CMDIsGlobal"], cfg["CSW_CMDUsage"], cfg["CSW_CMDDescription"], self.ProcessCSW)
        #self.linkCMD = CBE.CBECommand(cfg["CSW_LinkName"], cfg["CSW_LinkCooldown"], True, cfg["CSW_LinkIsGlobal"], cfg["CSW_LinkUsage"], cfg["CSW_LinkDescription"], self.ProcessCSWLink)
        self.eventsCMD = CBE.CBECommand(cfg["CSW_EventsName"], cfg["CSW_EventsCooldown"], False, cfg["CSW_EventsIsGlobal"], cfg["CSW_EventsUsage"], cfg["CSW_EventsDescription"], self.ProcessEvents)
        #self.cbe.AddCommand(self.cmdCMD)
        #self.cbe.AddCommand(self.linkCMD)
        self.cbe.AddCommand(self.eventsCMD)
        return

    def RegisterUI(self):
        self.cbe.CBEDebugLog("RegisterUI", "CSW")
        self.cbe.AddUIFromFile("UI/CSWModule_UI.json")
        return

    def RegisterHelp(self):
        self.cbe.CBEDebugLog("RegisterHelp", "CSW")
        return

    # these methods will ALWAYS be called when the module is registered at the chatbot
    def GetDefaultConfig(self):
        self.cbe.CBEDebugLog("GetDefaultConfig", "CSW")
        tempDict = {
            "CSW_CMDName": "csw",
            "CSW_CMDCooldown": 300,
            "CSW_CMDIsGlobal": False,
            "CSW_CMDUsage": "!csw [list]",
            "CSW_CMDDescription": "Zeigt die Mitglieder der CSW-Elite, die im Chat anwesend sind. Der Parameter \"list\" zeigt die gesamte CSW-Elite.",
            "CSW_CMDComplete": "Die CSW-Elite ist vollständig anwesend!",
            "CSW_CMDNobody": "Von der CSW-Elite ist leider noch keiner da...",
            "CSW_CMDJoin": ", ",
            "CSW_CMDCurrent": "Die aktuelle CSW-Elite: $list",
            "CSW_CMDMissing": "Es fehlen: $list",
            "CSW_CMDPresent": "Von der CSW-Elite sind folgende Leute anwesend: $list.",
            "CSW_CMDNotWritten": "Noch nicht geschrieben haben: $list.",
            "CSW_CMDPresentButNotWritten": "Von der CSW-Elite sind folgende Leute anwesend: $list.",

            "CSW_LinkName": "cswlink",
            "CSW_LinkCooldown": 300,
            "CSW_LinkIsGlobal": False,
            "CSW_LinkUsage": "!cswlink [own]",
            "CSW_LinkDescription": "Zeigt den Link zum Twitch-Kanal von Mitgliedern der CSW-Elite. Der Parameter \"own\" zeigt den Link zum eigenen Kanal, fall der Nutzer der CSW-Elite angehört",
            "CSW_LinkLessThanTwo": "Aktuell sind weniger als 2 Leute Mitglied der CSW-Elite...",
            "CSW_LinkString": "Hey, besucht mal den Kanal von $user: $link",

            "CSW_EventsName": "events",
            "CSW_EventsCooldown": 120,
            "CSW_EventsIsGlobal": True,
            "CSW_EventsUsage": "!events",
            "CSW_EventsDescription": "Zeigt die nächsten Termine des CSW-Streamings an",
            "CSW_EventsMax": 120,
            "CSW_EventsJoin": " ||| ",
            "CSW_EventsNoMore": "Aktuell sind noch keine weiteren Termine geplant",
            "CSW_EventsError": "Kann aktuell nicht auf Termine zugreifen...",
            "CSW_EventsTimedUpdate": 600
        }
        return tempDict

    # these methods can be hooked in the chatbot callbacks and are only called, if the corresponding members are set to true
    def Init(self):
        self.cbe.CBEDebugLog("Init", "CSW")
        self.LoadCSWElite()
        return

    def Tick(self):
        if self.cbe.GetBotLifetime() > self.NextWriteTime:
            self.NextWriteTime += self.cbe.Config["CSW_EventsTimedUpdate"]
            nextEvents = self.LoadEvents()
            self.WriteEvents(nextEvents)
        return

    def ReloadSettings(self, jsonData):
        self.cbe.CBEDebugLog("ReloadSettings", "CSW")
        self.NextWriteTime = 0.
        #self.cbe.RemoveCommand(self.cmdCMD.cmd)
        #self.cbe.RemoveCommand(self.linkCMD.cmd)
        self.cbe.RemoveCommand(self.eventsCMD.cmd)
        self.RegisterCommands()

    def ScriptToggled(self, state):
        self.cbe.CBEDebugLog("ScriptToggled", "CSW")
        self.NextWriteTime = 0.
        if state == True:
            self.LoadCSWElite()

    def LoadCSWElite(self):
        self.cbe.CBEDebugLog("LoadCSWElite", "CSW")
        try:
            val = eval(self.cbe.GetRequest("https://streaming.ensmann.de/streamers", self.Headers))
            self.CSWUsers = eval(val["response"])
        except Exception as e:
            self.cbe.CBELogException("Loading CSW elite failed: " + str(e), "CSWModule")
        return

    def ProcessCSW(self, data):
        self.cbe.CBEDebugLog("ProcessCSW", "CSW")
        if data.GetParamCount() > 1:
            if data.GetParam(1) == "list":
                self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["CSW_CMDCurrent"]).safe_substitute(list=self.cbe.Config["CSW_CMDJoin"].join([self.cbe.GetDisplayName(user) for user in self.CSWUsers])))
            else:
                self.cbe.SendTwitchMessage(self.cbe.Config["self.cbe_String_MissingParameter"]).safe_substitute(param=data.GetParam(1))
                return False
        else:
            currentViewers = self.cbe.GetViewerList()
            currentActiveViewers = self.cbe.GetActiveUsers()
            cswViewers = []
            cswActiveViewers = []
            cswMissingViewers = []
            for user in self.CSWUsers:
                if self.cbe.GetDisplayName(user) == self.cbe.GetChannelName():
                    continue
                elif user in currentViewers:
                    cswViewers.append(user)
                elif user in currentActiveViewers:
                    cswActiveViewers.append(user)
                else:
                    cswMissingViewers.append(user)
            msg = ""
            if len(cswActiveViewers) > 0:
                msg += CBE.stemp(self.cbe.Config["CSW_CMDPresent"]).safe_substitute(list=self.cbe.Config["CSW_CMDJoin"].join([self.cbe.GetDisplayName(user) for user in cswActiveViewers]))
            if len(cswViewers) > 0:
                if len(cswActiveViewers) > 0:
                    msg += " " + CBE.stemp(self.cbe.Config["CSW_CMDNotWritten"]).safe_substitute(list=self.cbe.Config["CSW_CMDJoin"].join([self.cbe.GetDisplayName(user) for user in cswViewers]))
                else:
                    msg += CBE.stemp(self.cbe.Config["CSW_CMDPresentButNotWritten"]).safe_substitute(list=self.cbe.Config["CSW_CMDJoin"].join([self.cbe.GetDisplayName(user) for user in cswViewers]))
            if len(cswMissingViewers) > 0:
                if len(cswActiveViewers) > 0 or len(cswViewers) > 0:
                    msg += " " + CBE.stemp(self.cbe.Config["CSW_CMDMissing"]).safe_substitute(list=self.cbe.Config["CSW_CMDJoin"].join([self.cbe.GetDisplayName(user) for user in cswMissingViewers]))
                else:
                    msg +=self.cbe.Config["CSW_CMDNobody"]
            else:
                msg += " " + self.cbe.Config["CSW_CMDComplete"]
            self.cbe.SendTwitchMessage(msg)
        return True

    def ProcessCSWLink(self, data):
        self.cbe.CBEDebugLog("ProcessCSWLink", "CSW")
        def GetRandom():
            cswRandom = None
            while cswRandom is None or (self.cbe.GetDisplayName(cswRandom) == self.cbe.GetChannelName()) or (self._lastLinkedUser is not None and cswRandom == self._lastLinkedUser and len(self.CSWUsers) > 2):
                # repeat while the random name is the broadcasters name or it is the same as the last linked name and there is a third name left
                cswRandom = self.CSWUsers[self.cbe.GetRandom(0, len(self.CSWUsers))]
            return cswRandom
        if len(self.CSWUsers) > 1:
            cswRandom = None
            if data.GetParamCount() > 1:
                if data.GetParam(1) == "own":
                    if data.User in self.CSWUsers:
                        cswRandom = data.User
                    else:
                        cswRandom = GetRandom()
                elif data.GetParam(1) in self.CSWUsers:
                    cswRandom = data.GetParam(1)
                else:
                    self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["self.cbe_String_UnknownParameter"]).safe_substitute(param=data.GetParam(1)))
                    return
            else:
                cswRandom = GetRandom()
            self._lastLinkedUser = cswRandom
            self.cbe.SendTwitchMessage(CBE.stemp(self.cbe.Config["CSW_LinkString"]).safe_substitute(user=self.cbe.GetDisplayName(cswRandom), link="https://www.twitch.tv/" + cswRandom))
        else:
            self.cbe.SendTwitchMessage(self.cbe.Config["CSW_LinkLessThanTwo"])
            return False
        return True

    def LoadEvents(self):
        self.cbe.CBEDebugLog("LoadEvents", "CSW")
        def cm(x, y):
            val = 0
            if self.ParseEventsVersion == 1:
                val = 1 if x[1] > y[1] else (-1 if x[1] < y[1] else 0)
            else:
                val = 1 if x[2] > y[2] else (-1 if x[2] < y[2] else 0)
            return val
        try:
            val = self.cbe.GetRequest("https://streaming.ensmann.de/streamplan", self.Headers)
            js = json.loads(eval(val)["response"])
            nextEvents = []
            now = datetime.datetime.now()
            for item in js["items"]:
                startTime = datetime.datetime.strptime(item["start"]["dateTime"][:19], "%Y-%m-%dT%H:%M:%S")
                if now < startTime:
                    if self.ParseEventsVersion == 1:
                        nextEvents.append((item["summary"], startTime))
                    elif self.ParseEventsVersion == 2:
                        nextEvents.append((item["summary"], item["description"], startTime))
                    else:
                        self.cbe.CBELogException("ParseEventsVersion not recognized: " + str(self.ParseEventsVersion), "CSWModule")
                        nextEvents.append((item["summary"], startTime))
                    if len(nextEvents) == self.cbe.Config["CSW_EventsMax"]:
                        break
            nextEvents.sort(cmp=cm)
            return nextEvents
        except Exception as e:
            self.cbe.CBELogException("Loading events failed: " + str(e), "CSWModule")
            self.cbe.SendTwitchMessage(self.cbe.Config["CSW_EventsError"])
            return None

    def WriteEvents(self, eventsList):
        locale.setlocale(locale.LC_TIME, "de_DE")
        self.cbe.CBEDebugLog("WriteEvents", "CSW")
        def writeUTF8(ctf, s):
            ctf.write(s.encode('utf-8'))
        maxStreamerNameLength = 2
        spaceUntilTitle = 0
        titleSep = 3
        maxTitleWidth = 25
        if eventsList is not None:
            for event in eventsList:
                evStreamer = event[0].split(":", 1)[0].strip()
                maxStreamerNameLength = max(maxStreamerNameLength, len(evStreamer))
            spaceUntilTitle = maxStreamerNameLength + 15 + titleSep
            try:
                with open(os.path.join(self.cbe.Path, self.CSWEventsFileOneLine), "w") as ctfol:
                    with open(os.path.join(self.cbe.Path, self.CSWEventsFile), "w") as ctf:
                        with open(os.path.join(self.cbe.Path, self.CSWEventsFileMultiLine), "w") as ctfml:
                            for event in eventsList:
                                evDate = ""
                                evStreamer = ""
                                evTitle = None
                                if self.ParseEventsVersion == 1:
                                    splts = event[0].split(":", 1)
                                    evDate = event[1].strftime("%d.%m. %H:%M")
                                    evStreamer = splts[0].strip()
                                    if len(splts) > 1:
                                        evTitle = splts[1].strip()
                                elif self.ParseEventsVersion == 2:
                                    evDate = event[2].strftime("%d.%m. %H:%M")
                                    evStreamer = event[0].strip()
                                    evTitle = event[1].strip()
                                else:
                                    self.cbe.CBELogException("ParseEventsVersion not recognized: " + str(self.ParseEventsVersion), "CSWModule")
                                    return
                                if evTitle is None:
                                    writeUTF8(ctf, evDate + " - " + evStreamer + "\n")
                                    writeUTF8(ctfol, evDate + " - " + evStreamer + " ||| ")
                                    writeUTF8(ctfml, evDate + " - " + evStreamer + "\n")
                                else:
                                    writeUTF8(ctf, evDate + " - " + evStreamer + "\n  > " + evTitle + "\n")
                                    writeUTF8(ctfol, evDate + " - " + evStreamer + " > " + evTitle + " ||| ")

                                    writeUTF8(ctfml, evDate + " - " + evStreamer + (maxStreamerNameLength - len(evStreamer) + titleSep) * " ")
                                    titleSplits = evTitle.split(" ")
                                    count = 0
                                    for s in titleSplits:
                                        addSpace = True if count != 0 else False
                                        if count + len(s) + (1 if addSpace else 0) <= maxTitleWidth:
                                            writeUTF8(ctfml, (" " if addSpace else "") + s)
                                            count += len(s) + (1 if addSpace else 0)
                                        else:
                                            writeUTF8(ctfml, "\n" + spaceUntilTitle * " " + s)
                                            count = len(s)
                                    writeUTF8(ctfml, "\n")
                                    #writeUTF8(ctfml, evDate + " - " + evStreamer + (maxStreamerNameLength - len(evStreamer) + titleSep) * " " + evTitle + "\n")
                            if len(eventsList) == 0:
                                writeUTF8(ctf, self.cbe.Config["CSW_EventsNoMore"])
                                writeUTF8(ctfol, self.cbe.Config["CSW_EventsNoMore"] + "              ")
                                writeUTF8(ctfml, self.cbe.Config["CSW_EventsNoMore"])
            except IOError as e:
                self.cbe.CBELogException("Could not write to " + self.CSWEventsFile + ": " + str(e), "CSWModule")

    def ProcessEvents(self, data):
        self.cbe.CBEDebugLog("ProcessEvents", "CSW")
        nextEvents = self.LoadEvents()
        if nextEvents is not None and len(nextEvents) > 0:
            eventStrings = []
            for event in nextEvents:
                if self.ParseEventsVersion == 1:
                    eventStrings.append(event[1].strftime("%d. %b %H:%M") + " Uhr: " + event[0])
                elif self.ParseEventsVersion == 2:
                    eventStrings.append(event[2].strftime("%d. %b %H:%M") + " Uhr: " + event[0] + ": " + event[1])
                else:
                    self.cbe.CBELogException("ParseEventsVersion not recognized: " + str(self.ParseEventsVersion), "CSWModule")
                    self.cbe.SendTwitchMessage("Parsing error")
                    return False
            self.cbe.SendTwitchMessage(self.cbe.Config["CSW_EventsJoin"].join(eventStrings))
            self.WriteEvents(nextEvents)
        elif nextEvents is not None:
            self.cbe.SendTwitchMessage(self.cbe.Config["CSW_EventsNoMore"])
        else:
            return False
        return True