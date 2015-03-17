import Logger
import IrcConnection
import TwitchApi
import server

from threading import Thread

class KappaFeed(object):
    def __init__(self):
        self.serverAddress = 'irc.twitch.tv'
        self.eventServerAddress = '199.9.252.26'
        self.portNumber = 80
        self.userName = 'kappafeed'
        self.oauthToken = 'oauth:pf7dk9qchza0f0v64c34hp5zb8p4fk'
        self.numChannelsToJoin = 25
        self.kfLogger = Logger.Logger('kf')

    def startKappaFeed(self):
        self.kfLogger.log('kappafeed starting...')

        while True:
            try:
                ircInstantiated = False;
                eventIrcInstantiated = False;

                irc = IrcConnection.IrcConnection(self.oauthToken, self.userName)

                eventIrc = IrcConnection.IrcConnection(self.oauthToken, self.userName)

                twitchApi = TwitchApi.TwitchApi()
                #server.sendToClients({'serverMsg': 'Refreshing top streams list. One moment.'})
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
                            if eventIrc.joinChannel(chan):
                                eventChannelsJoined.append(chan)
                        else:
                            if ircInstantiated == False:
                                irc.connect(self.serverAddress, self.portNumber, True)
                                ircInstantiated = True
                            if irc.joinChannel(chan):
                                channelsJoined.append(chan)

                    if ircInstantiated:
                        t1 = Thread(target=irc.channelScan, args=['25'])
                        t1.start()
                    if eventIrcInstantiated:
                        t2 = Thread(target=eventIrc.channelScan, args=['25'])
                        t2.start()

                    if ircInstantiated:
                        t1.join()
                    if eventIrcInstantiated:
                        t2.join()

                    if ircInstantiated:
                        channelsNotParted = irc.partChannels(channelsJoined)
                        if len(channelsNotParted) > 0:
                            break

                    if eventIrcInstantiated:
                        eventChannelsNotParted = eventIrc.partChannels(eventChannelsJoined)
                        if len(eventChannelsNotParted) > 0:
                            break

                    self.kfLogger.log('Refreshing top streams...')
                self.kfLogger.log('Restarting...')
                #server.sendToClients({'serverMsg': 'Refreshing top streams list. One moment.'})
            except Exception, e:
                self.kfLogger.log('Error, restarting... %s' % str(e))
                #server.sendToClients({'serverMsg': 'Refreshing top streams list. One moment.'})
