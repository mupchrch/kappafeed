import socket
from time import sleep

class IrcConnection(object):

    def __init__(self, oauthToken, userName):
        self.oauthToken = oauthToken
        self.userName = userName
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, serverAddress, portNumber, useTags):
        #irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((serverAddress, portNumber))

        self.sendMsg('PASS %s' % self.oauthToken)
        self.sendMsg('NICK %s' % self.userName)
        self.sendMsg('USER %s %s %s :%s' %
                 (self.userName, serverAddress, self.userName, self.userName))

        if useTags:
            sleep(1)
            self.sendMsg('CAP REQ :twitch.tv/tags')

    def getIrc(self):
        return self.irc

    def sendMsg(self, msg):
        self.irc.send(msg + '\r\n')
