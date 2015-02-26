import Logger

import socket
import time

class IrcConnection(object):

    def __init__(self, oauthToken, userName):
        self.oauthToken = oauthToken
        self.userName = userName
        self.ircSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ircLogger = Logger.Logger('irc')

    def connect(self, serverAddress, portNumber, useTags):
        self.ircSocket.connect((serverAddress, portNumber))

        self.sendMsg('PASS %s' % self.oauthToken)
        self.sendMsg('NICK %s' % self.userName)
        self.sendMsg('USER %s %s %s :%s' %
                 (self.userName, serverAddress, self.userName, self.userName))

        connResponse = self.recMsg()
        if connResponse:
            self.ircLogger.log(connResponse)

        if useTags:
            time.sleep(1)
            self.ircLogger.log('Sending capability request...')
            self.sendMsg('CAP REQ :twitch.tv/tags')
            capResponse = self.recMsg()
            if capResponse:
                self.ircLogger.log(capResponse)

    #def getIrc(self):
    #    return self.irc

    def sendMsg(self, msg):
        self.ircSocket.send(msg + '\r\n')

    def recMsg(self):
        return self.ircSocket.recv(1024)

    def printRaw(self):
        self.ircLogger.log('Printing incoming messages...')
        while True:
            rec = self.recMsg()
            if rec:
                self.ircLogger.log(rec)

    #TODO(mike): update this to work with message tags
    def parseMessages(self, messages):
        prefix = ''
        trailing = []
        command = 'UNKNOWN'
        args = []
        parsedMsgs = []

        try:
            separatedMsgs = messages.split('\r\n')
            for msg in separatedMsgs:
                if not msg:
                    self.ircLogger.log('Empty line.')
                elif msg[0] == ':':
                    prefix, msg = msg[1:].split(' ', 1)
                    if msg.find(' :') != -1:
                        msg, trailing = msg.split(' :', 1)
                        args = msg.split()
                        args.append(trailing)
                    else:
                        args = msg.split()

                    if len(args) == 0:
                        self.ircLogger.log('No command in IRC message.')
                    else:
                        command = args.pop(0)

                    parsedMsgs.append((prefix, command, args))
                elif msg[0] == '@':
                    self.ircLogger.log('Tagged message found.')
        except Exception,e:
            self.ircLogger.log('Error in parseMsg.')
            self.ircLogger.log(e)

        return parsedMsgs

    #TODO(mike): check this method to see if it can be done cleaner (threads?)
    def joinChannels(self, channels):
        self.ircLogger.log('Joining channels...')
        for channel in channels:
            joinStatus = self.joinChannel(channel)
            if not joinStatus:
                channels.remove(channel)
        return channels

    def joinChannel(self, channel):
        self.ircLogger.log('Joining %s...' % channel)
        numJoinAttempts = 0
        channelStartTime = time.time()

        self.sendMsg('JOIN #%s' % channel)

        while True:
            joinResponse = self.recMsg()
            if joinResponse:
                messages = self.parseMessages(joinResponse)
                for msg in messages:
                    prefix, command, args = msg
                    if command == 'JOIN':
                        if args[0][1:] == channel:
                            self.ircLogger.log('Joined #%s.' % channel)
                            return True
                if time.time() - channelStartTime >= 1:
                    numJoinAttempts += 1
                    if numJoinAttempts == 3:
                        self.ircLogger.log('Failed to join #%s.' % channel)
                        return False
                    channelStartTime = time.time()
                    self.sendMsg('JOIN #%s' % channel)
        return False
