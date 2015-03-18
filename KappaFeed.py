import Logger
import IrcConnection
import TwitchApi
import server

from threading import Thread

#TODO(mike): add support for the situation where event server IP changes
class KappaFeed(object):
    def __init__(self):
        self.serverAddress = 'irc.twitch.tv'
        self.eventServerAddress = '192.16.64.143'
        self.portNumber = 80
        self.userName = 'kappafeed'
        self.oauthToken = 'oauth:pf7dk9qchza0f0v64c34hp5zb8p4fk'
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

                    if ircInstantiated:
                        t1 = Thread(target=irc.channelScan, args=['25', 3600])
                        t1.start()
                    if eventIrcInstantiated:
                        t2 = Thread(target=eventIrc.channelScan, args=['25', 3600])
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
                    server.sendToClients(self.refreshMsg)
                self.kfLogger.log('Restarting...')
                server.sendToClients(self.refreshMsg)
            except Exception, e:
                self.kfLogger.log('Error, restarting... %s' % str(e))
                server.sendToClients(self.refreshMsg)
