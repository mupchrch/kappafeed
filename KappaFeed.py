import Logger
import IrcConnection
import TwitchApi

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
                irc = IrcConnection.IrcConnection(self.oauthToken, self.userName)
                irc.connect(self.serverAddress, self.portNumber, True)

                eventIrc = IrcConnection.IrcConnection(self.oauthToken, self.userName)
                eventIrc.connect(self.eventServerAddress, self.portNumber, True)

                twitchApi = TwitchApi.TwitchApi()

                while True:
                    topChannels = twitchApi.getTopChannels(self.numChannelsToJoin)
                    channelsJoined = []

                    #detemine whether to join on event chat or regular
                    for chan in topChannels:
                        if twitchApi.getEventChatStatus(chan):
                            if eventIrc.joinChannel(chan):
                                channelsJoined.append(chan)
                        else:
                            if irc.joinChannel(chan):
                                channelsJoined.append(chan)

                    channelsJoined = irc.joinChannels(topChannels)
                    if len(channelsJoined) == 0:
                        break
                    irc.channelScan('25')
                    channelsNotParted = irc.partChannels(channelsJoined)
                    if len(channelsNotParted) > 0:
                        break
                    self.kfLogger.log('Refreshing top streams...')
                self.kfLogger.log('Restarting...')
            except Exception, e:
                self.kfLogger.log('Error, restarting... %s' % str(e))
