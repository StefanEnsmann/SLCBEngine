# -*- coding: utf-8 -*-
import os
import json
from urlparse import urlparse
import CBE

class ShowImageModule(CBE.CBEModule):
    def GetDefaultConfig(self):
        return {}

    def RegisterUI(self):
        return 
    
    def RegisterCommands(self):
        return
    
    def RegisterHelp(self):
        return

    def Init(self):
        #self.cbe.BroadcastWsEvent("SHOWIMAGE_CONFIG", json.dumps({}))
        return

    def Execute(self, data):
        self.cbe.CBEDebugLog(data.Message, "ShowImageModule")
        for i in range(data.GetParamCount()):
            param = data.GetParam(i)
            self.cbe.CBEDebugLog(param + " " + str(self.IsURL(param)) + " " + str(self.IsImage(param)), "ShowImageModule")
            if self.IsURL(param) and self.IsImage(param):
                self.cbe.BroadcastWsEvent("SHOWIMAGE_IMAGE_IN", json.dumps({"url": param}))
        return
    
    def IsURL(self, param):
        par = urlparse(param)
        return par.scheme != "" and par.netloc != "" and par.path != ""
    
    def IsImage(self, param):
        return (param.endswith(".gif") or param.endswith(".png") or param.endswith(".jpg") or param.endswith(".jpeg"))