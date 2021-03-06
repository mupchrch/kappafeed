import Logger
import IrcConnection
import TwitchApi
import server

import json
import os
from threading import Thread

#TODO(mike): add support for the situation where event server IP changes
class KappaFeed(object):
    def __init__(self):
        self.serverAddress = 'irc.twitch.tv'
        self.eventServerAddress = '192.16.64.143'
        self.portNumber = 6667
        self.userName = 'kappafeed'
        self.oauthToken = os.environ['OAUTH']
        self.numChannelsToJoin = 25
        self.kfLogger = Logger.Logger('kf')
        self.refreshMsg = {'serverMsg'.decode('utf-8'):
                           'Refreshing top streams. One moment.'.decode('utf-8')}

    def startKappaFeed(self):
        self.kfLogger.log('kappafeed starting...')

        while True:
            try:
                ircInstantiated = False;
                eventIrcInstantiated = False;

                irc = IrcConnection.IrcConnection(self.oauthToken, self.userName)
                eventIrc = IrcConnection.IrcConnection(self.oauthToken, self.userName)

                twitchApi = TwitchApi.TwitchApi()

                while True:
                    topChannels = twitchApi.getTopChannels(self.numChannelsToJoin)
                    globalEmotes = twitchApi.getEmotes('0')
                    channelsJoined = []
                    eventChannelsJoined = []

                    #detemine whether to join on event chat or regular
                    for chan in topChannels:
                        if twitchApi.getEventChatStatus(chan):
                            if eventIrcInstantiated == False:
                                eventIrc.connect(self.eventServerAddress, self.portNumber, True)
                                eventIrcInstantiated = True
                            if eventIrc.joinPartChannel('JOIN', chan):
                                eventChannelsJoined.append(chan)
                        else:
                            if ircInstantiated == False:
                                irc.connect(self.serverAddress, self.portNumber, True)
                                ircInstantiated = True
                            if irc.joinPartChannel('JOIN', chan):
                                channelsJoined.append(chan)

                    topChannelsToSend = []
                    for eChan in eventChannelsJoined:
                        topChannelsToSend.append({'channel'.decode('utf-8'): eChan.decode('utf-8')})
                    for chan in channelsJoined:
                        topChannelsToSend.append({'channel'.decode('utf-8'): chan.decode('utf-8')})
                    server.setTopChannelsMsg({'topChannels'.decode('utf-8'): topChannelsToSend})

                    if ircInstantiated:
                        t1 = Thread(target=irc.channelScan, args=[globalEmotes.values(), 3600])
                        t1.start()
                    if eventIrcInstantiated:
                        t2 = Thread(target=eventIrc.channelScan, args=[globalEmotes.values(), 3600])
                        t2.start()

                    if ircInstantiated:
                        t1.join()
                    if eventIrcInstantiated:
                        t2.join()

                    if ircInstantiated:
                        for chan in channelsJoined:
                            if irc.joinPartChannel('PART', chan) == False:
                                break
                    if eventIrcInstantiated:
                        for eChan in eventChannelsJoined:
                            if irc.joinPartChannel('PART', eChan) == False:
                                break

                    self.kfLogger.log('Refreshing top streams...')
                    server.sendToClients(self.refreshMsg, [])
                self.kfLogger.log('Restarting...')
                server.sendToClients(self.refreshMsg, [])
            except Exception, e:
                self.kfLogger.log('Error, restarting... %s' % str(e))
                server.sendToClients(self.refreshMsg, [])
