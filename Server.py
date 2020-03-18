import sys
from time import sleep, localtime

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class ClientChannel(Channel):
    """
    This is the server representation of a connected client.
    """
    def __init__(self, *args, **kwargs):
        self.nickname = "anonymous"
        Channel.__init__(self, *args, **kwargs)
    
    def Close(self):
        self._server.DelPlayer(self)

    def Network_ReadyToPlay(self,data):
        self._server.SendToOthersR({"ready": data["ready"], "who":self.nickname})

        
    def Network_BombDropped(self, data):
        self._server.SendToOthersB({"bomb": data["bomb"],  "who": self.nickname})

    def Network_Touched(self, data):
        self._server.SendToOthersT({"touched": data["touched"], "bomb": data["bomb"], "B":data["B"], "who": self.nickname})

    def Network_nickname(self, data):
        self.nickname = data["nickname"]
        self._server.PrintPlayers()
        self.Send({"action":"start"})

class MyServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = {}
        print('Server launched')
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print("New Player connected")
        self.players[player] = True
 
    def PrintPlayers(self):
        print("players' nicknames :",[p.nickname for p in self.players])
  
    def DelPlayer(self, player):
        print("Deleting Player " + player.nickname + " at "+str(player.addr))
        del self.players[player]

    def SendToOthersR(self, data):
        [p.Send({"action":"ReadyToPlay","ready": data["ready"]}) for p in self.players if p.nickname != data["who"]]
        
    def SendToOthersB(self, data):
        [p.Send({"action":"BombDropped","bomb": data["bomb"]}) for p in self.players if p.nickname != data["who"]]

    def SendToOthersT(self, data):
        [p.Send({"action":"Touched","touched": data["touched"], "bomb": data["bomb"], "B":data["B"]}) for p in self.players if p.nickname != data["who"]]

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.001)

# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
else:
    host, port = sys.argv[1].split(":")
    s = MyServer(localaddr=(host, int(port)))
    s.Launch()
