# -*- coding: utf-8 -*-
import os
import json
import CBE

class TwitterModule(CBE.CBEModule):
    def __init__(self, cbe, name):
        super(TwitterModule, self).__init__(cbe)
        self.useTick = True
        self.Interval = 5
        self.NextFetchTime = 0.
        self.OutputFile = "TwitterFollowers.txt"
        self.Headers = {'Authorization': 'Bearer FDF7u89fdC998875c8d7f'}
        self.Url = "https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names=" + name

    def CheckConfig(self):
        return

    def RegisterUI(self):
        return
    
    def RegisterCommands(self):
        return
    
    def RegisterHelp(self):
        return

    def Tick(self):
        if self.cbe.GetBotLifetime() > self.NextFetchTime:
            followers = json.loads(eval(self.cbe.GetRequest(self.Url, self.Headers))["response"])[0]["followers_count"]
            with open(os.path.join(self.cbe.Path, self.OutputFile), "w") as ctf:
                ctf.write(str(followers).encode('utf-8'))
            self.NextFetchTime = self.cbe.GetBotLifetime() + self.Interval
            try:
                pass
            except Exception as e:
                self.cbe.Log(str(e), "TwitterModule")
        return