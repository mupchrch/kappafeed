import Logger
import IrcMessage

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

        connResponse = self.recMsgs()
        if connResponse:
            self.ircLogger.log(connResponse)

        if useTags:
            time.sleep(1)
            self.ircLogger.log('Sending capability request...')
            self.sendMsg('CAP REQ :twitch.tv/tags')
            capResponse = self.recMsgs()
            if capResponse:
                self.ircLogger.log(capResponse)

    #def getIrc(self):
    #    return self.irc

    def sendMsg(self, msg):
        self.ircSocket.send(msg + '\r\n')

    def recMsgs(self):
        return self.ircSocket.recv(1024)

    def printRaw(self):
        self.ircLogger.log('Printing incoming messages...')
        while True:
            rec = self.recMsgs()
            if rec:
                self.ircLogger.log(rec)

    #TODO(mike): put a try catch somewhere so that multiple messages still
    #            parsed if one is malformed
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
                else:
                    color = ''
                    emotes = []
                    subscriber = ''
                    turbo = ''
                    userType = ''
                    #take the tags off the front
                    if msg[0] == '@':
                        self.ircLogger.log('Tagged message found.')

                        tags, msg = msg[1:].split(' ', 1)
                        color, tags = tags[1:].split(';', 1)
                        color = color[(color.find('=')+1):]

                        rawEmotes, tags = tags.split(';', 1)
                        rawEmotes = rawEmotes[(rawEmotes.find('=')+1):]
                        #check for empty
                        if rawEmotes:
                            splitEmotes = rawEmotes.split('/')
                            for emoteTag in splitEmotes:
                                emote, rawIndices = emoteTag.split(':')
                                splitIndices = rawIndices.split(',')
                                for indices in splitIndices:
                                    startIndex, endIndex = indices.split('-')
                                    emotes.append((emote, startIndex, endIndex))

                        subscriber, tags = tags.split(';', 1)
                        subscriber = subscriber[(subscriber.find('=')+1):]

                        turbo, tags = tags.split(';', 1)
                        turbo = turbo[(turbo.find('=')+1):]

                        userType = tags[(tags.find('=')+1):]

                    #then parse the message
                    if msg[0] == ':':
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

                    parsedMsg = IrcMessage.IrcMessage(color, emotes, subscriber, turbo, userType, prefix, command, args)
                    parsedMsgs.append(parsedMsg)
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
            joinResponse = self.recMsgs()
            if joinResponse:
                messages = self.parseMessages(joinResponse)
                for msg in messages:
                    #prefix, command, args = msg
                    if msg.command == 'JOIN':
                        if msg.args[0][1:] == channel:
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
