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
            #self.ircLogger.log('Sending capability request...')
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
                    #displayName = ''
                    #take the tags off the front
                    if msg[0] == '@':
                        tags = {}
                        rawTags, msg = msg[1:].split(' ', 1)
                        rawTags = rawTags.split(';')
                        for rawTag in rawTags:
                            tag, value = rawTag.split('=', 1)
                            tags[tag] = value

                        color = tags['color']
                        subscriber = tags['subscriber']
                        turbo = tags['turbo']
                        userType = tags['user-type']
                        #displayName = tags['display-name']

                        rawEmotes = tags['emotes']
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

    #scans all channels for the emote 'emoteNum' for a period of time 'timeLen'
    def channelScan(self, emoteNum, timeLen):
        #self.ircLogger.log('Scanning for emote number %s...' % emoteNum)

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
                                actionStr = ''
                                twitchUser = msg.prefix[:msg.prefix.find('!')]
                                twitchChannel = msg.args[0]
                                twitchMsg = msg.args[1].rstrip('\r\n')
                                uTwitchMsg = twitchMsg.decode('utf-8')
                                #check if this is an action msg
                                if uTwitchMsg[:7] == '\x01ACTION':
                                    uTwitchMsg = uTwitchMsg.strip('\x01')
                                    actionStr, uTwitchMsg = uTwitchMsg.split(' ', 1)

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

                                #add 'ACTION' to front of msg if it is action
                                uTwitchMsg = actionStr + ' ' + uTwitchMsg
                                #send to clients
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
                        #self.ircLogger.log('Received PING.')
                        #self.ircLogger.log('Sending PONG...')
                        self.sendMsg('PONG %s' % msg.args[0])
            #check to see if restart necessary
            if (time.time() - scanStartTime) >= timeLen:
                break

    #joins or parts a channel according to the action string
    def joinPartChannel(self, action, channel):
        #self.ircLogger.log('%sing #%s...' % (action, channel))
        self.sendMsg('%s #%s' % (action, channel))
        chanJoinPartTime = time.time()
        numJoinPartAttempts = 0

        buffer = ''
        while True:
            buffer += self.recMsgs()
            if buffer:
                messages, buffer = self.parseMessages(buffer)
                for msg in messages:
                    if msg.command == action:
                        if msg.args[0][1:] == channel:
                            #self.ircLogger.log('%sed #%s.' % (action, channel))
                            return True
            if (time.time() - chanJoinPartTime) >= 1:
                numJoinPartAttempts += 1
                if numJoinPartAttempts == 3:
                    self.ircLogger.log('Failed to %s channel #%s.' % (action, channel))
                    return False
                self.sendMsg('%s #%s' % (action, channel))
                chanJoinPartTime = time.time()
        return False
