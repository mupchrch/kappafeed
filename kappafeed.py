import Logger
import IrcConnection
import TwitchApi

#import re
#import server
#import urllib2
#import json
#import time
#import sys
#from thread import start_new_thread

apiAddress = "https://api.twitch.tv/kraken/"
serverAddress = "irc.twitch.tv"
portNumber = 80
userName = "kappafeed"
oauthToken = "oauth:pf7dk9qchza0f0v64c34hp5zb8p4fk"
numChannelsToJoin = 25
emote = r'Kappa'

#def emoteFilter (s, filt):
    #Finds messages with the specified emote regex in them
#    return filt.search(s)

#def logToConsole(s):
#    print '{kf} [' + time.strftime("%Y-%m-%d %H:%M:%S") + '] ' + s
#    sys.stdout.flush()

#TODO(mike): move this method to ircconnection class?
#def channelScan(irc):
#    logToConsole('Scanning for %s...' % emote)
#    kappaStartTime = time.time()
#    while True:
#        data = irc.recv(1024) #TODO sometimes 2 msgs come together... fix it so we don't lose 2nd msg?
#        if data:
#            logToConsole(data)
#            prefix, command, args = parseMessage(data)
#            if command == 'PRIVMSG':
#                twitchUser = prefix[:prefix.find('!')]
#                twitchChannel = args[0]
#                twitchMsg = args[1].rstrip('\r\n')
#                if 'PRIVMSG' not in twitchMsg:
#                    filt = re.compile(r'\b' + emote + r'\b')
#                    if emoteFilter(twitchMsg, filt):
#                        try:
#                            server.sendToClients({'channel': twitchChannel.decode('utf8'), 'user': twitchUser.decode('utf8'), 'msg': twitchMsg.decode('utf8')})
#                        except:
#                            pass
#            elif command == 'PING':
#                logToConsole('Received PING.')
#                logToConsole('Sending PONG...')
#                irc.send('PONG :tmi.twitch.tv\r\n')
#        if time.time() - kappaStartTime >= 3600:
#            break

#TODO(mike): move this method to ircconnection class?
#def partChannels(irc, channelsToPart):
#    logToConsole('Parting channels...')
#    channelCount = 0
#    channelsNotParted = []
#    for channel in channelsToPart:
#        irc.send('PART %s\r\n' % channel)
#        channelLeaveTime = time.time()
#        numPartAttempts = 0
#        while True:
#            partData = irc.recv(512)
#            if partData:
#                partPrefix, partCommand, partArgs = parseMessage(partData)
#                if partCommand == 'PART':
#                    if partArgs[0] == channel:
#                        logToConsole('Left channel %s.' % channel)
#                        channelCount += 1
#                        break
#            if time.time() - channelLeaveTime >= 1:
#                numPartAttempts += 1
#                if numPartAttempts == 3:
#                    logToConsole('Failed to part channel %s.' % channel)
#                    channelsNotParted.append(channel)
#                    break
#                irc.send('PART %s\r\n' % channel)
#                channelLeaveTime = time.time()
#    if numChannelsToJoin - channelCount > 0:
#        logToConsole('Unable to part %i channels.' % (numChannelsToJoin - channelCount))
#    return channelsNotParted

def startKappaFeed():
#    while True:
    kfLogger = Logger.Logger('kf')
    kfLogger.log('testing...')

    irc = IrcConnection.IrcConnection(oauthToken, userName)
    irc.connect(serverAddress, portNumber, True)
    twitchApi = TwitchApi.TwitchApi()
    topChannels = twitchApi.getTopChannels(numChannelsToJoin)

    irc.joinChannels(topChannels)
    irc.channelScan('25')

    #start_new_thread(ircListen, (irc.getIrc,))

#        try:
#            irc = chatConnect()
#            channelNames = []
#            while True:
#                channelNames = joinChannels(irc)
#                #restart program if no channels were successfully joined
#                if len(channelNames) == 0:
#                    break
#                channelScan(irc)
#                channelNames = partChannels(irc, channelNames)
#                if len(channelNames) > 0:
#                    break
#                logToConsole('Refreshing channel list...')
#            logToConsole('Restarting kappafeed...')
#        except Exception, e:
#            logToConsole('Error, restarting kappafeed... ' + str(e))
