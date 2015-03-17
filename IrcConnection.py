import Logger
import IrcMessage
import server

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

    #TODO(mike): break this method up so it is not as massive?
    def parseMessages(self, messages):
        prefix = ''
        trailing = []
        command = 'UNKNOWN'
        args = []
        splitLines = []
        parsedMsgs = []
        originalMsg = ''

        while True:
            if '\r\n' in messages:
                line, messages = messages.split('\r\n', 1)
                splitLines.append(line)
            else:
                break

        for msg in splitLines:
            originalMsg = msg
            try:
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
                                    emotes.append((emote, int(startIndex), int(endIndex)))
                        #need to sort emotes by start index
                        #have to do in order because of offset
                        emotes.sort(key=lambda x: x[1])

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
                    elif msg[:4] == 'PING':
                        command, args = msg.split(' ')

                    parsedMsg = IrcMessage.IrcMessage(color, emotes, subscriber,
                                                  turbo, userType, prefix,
                                                  command, args)
                    parsedMsgs.append(parsedMsg)
            except Exception,e:
                self.ircLogger.log('Parse error: %s' % str(e))
                self.ircLogger.log('MSG: %s' % originalMsg)

        return (parsedMsgs, messages)

    #TODO(mike): check this method to see if it can be done cleaner (threads?)
    def joinChannels(self, channels):
        self.ircLogger.log('Joining channels...')
        for channel in channels:
            joinStatus = self.joinChannel(channel)
            if not joinStatus:
                channels.remove(channel)
        return channels

    def joinChannel(self, channel):
        self.ircLogger.log('Joining #%s...' % channel)
        numJoinAttempts = 0
        channelStartTime = time.time()

        self.sendMsg('JOIN #%s' % channel)

        buffer = ''
        while True:
            buffer += self.recMsgs()
            if buffer:
                messages, buffer = self.parseMessages(buffer)
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

    def channelScan(self, emoteNum):
        self.ircLogger.log('Scanning for emote number %s...' % emoteNum)

        buffer = ''
        scanStartTime = time.time()
        while True:
            buffer += self.recMsgs()
            if buffer:
                messages, buffer = self.parseMessages(buffer)
                for msg in messages:
                    emoteCount = 0
                    if msg.command == 'PRIVMSG':
                        #search for Kappa
                        for emo in msg.emotes:
                            if emo[0] == emoteNum:
                                twitchUser = msg.prefix[:msg.prefix.find('!')]
                                twitchChannel = msg.args[0]
                                twitchMsg = msg.args[1].rstrip('\r\n')
                                uTwitchMsg = twitchMsg.decode('utf-8')
                                #replace all emoticons
                                offset = 0
                                for emoteInfo in msg.emotes:
                                    emote, start, end = emoteInfo
                                    startIndex = start + offset
                                    endIndex = (end + 1) + offset
                                    htmlInsert = ''
                                    if emote == emoteNum:
                                        htmlInsert = '<img class="emoticon" src="http://kappafeed.tv/static/images/kappa-md.png" alt="Kappa"></img>'
                                        emoteCount += 1
                                    else:
                                        htmlInsert = '<img class="emoticon" src="http://static-cdn.jtvnw.net/emoticons/v1/' + emote + '/1.0" alt="' + uTwitchMsg[startIndex:endIndex] + '"></img>'
                                    uTwitchMsg = uTwitchMsg[:startIndex] + htmlInsert + uTwitchMsg[endIndex:]
                                    offset += (len(htmlInsert) - (endIndex - startIndex))
                                #send to server
                                try:
                                    server.sendToClients(
                                        {'channel'.decode('utf-8'):
                                         twitchChannel.decode('utf-8'),
                                         'user'.decode('utf-8'):
                                            {'name'.decode('utf-8'):
                                            twitchUser.decode('utf-8'),
                                            'color'.decode('utf-8'):
                                            msg.color.decode('utf-8')},
                                         'msg'.decode('utf-8'):
                                            {'content'.decode('utf-8'):
                                            uTwitchMsg.decode('utf-8'),
                                            'emoteCount'.decode('utf-8'):
                                            emoteCount}})
                                except:
                                    pass
                                break
                    elif msg.command == 'PING':
                        self.ircLogger.log('Received PING.')
                        self.ircLogger.log('Sending PONG...')
                        self.sendMsg('PONG %s' % msg.args[0])
            #check to see if restart necessary
            if (time.time() - scanStartTime) >= 3600:
                break

    #returns True if all channels parted, False otherwise
    def partChannels(self, channels):
        self.ircLogger.log('Parting channels...')
        numParted = 0
        channelsNotParted = []
        for channel in channels:
            self.sendMsg('PART %s' % channel)
            channelPartTime = time.time()
            numPartAttempts = 0
            buffer = ''
            while True:
                buffer += self.recMsgs()
                if buffer:
                    messages, buffer = self.parseMessages(buffer)
                    for msg in messages:
                        if msg.command == 'PART':
                            if msg.args[0] == channel:
                                self.ircLogger.log('Parted #%s.' % channel)
                                numParted += 1
                                break
                if (time.time() - channelPartTime) >= 1:
                    numPartAttempts += 1
                    if numPartAttempts == 3:
                        self.ircLogger.log('Failed to part channel %s.' % channel)
                        channelsNotParted.append(channel)
                        break
                    self.sendMsg('PART %s' % channel)
                    channelPartTime = time.time()
        return channelsNotParted
