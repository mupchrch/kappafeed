import Logger

import urllib2
import json

class TwitchApi(object):

    def __init__(self):
        self.address = 'https://api.twitch.tv/kraken/'
        self.apiLogger = Logger.Logger('api')

    #gets the names of the top n streams
    def getTopChannels(self, numChannels):
        self.apiLogger.log('Getting top streams...')
        streamsAddress = self.address + 'streams'
        topChannels = []
        count = 0

        while True:
            rawJson = urllib2.urlopen(streamsAddress)
            twitchJson = json.load(rawJson)

            for twitchStream in twitchJson['streams']:
                if count == numChannels:
                    return topChannels
                topChannels.append(twitchStream['channel']['name'])
                count += 1
            streamsAddress = twitchJson['_links']['next']
        return topChannels

    #true if channel has event chat server, false for normal chat server
    def getEventChatStatus(self, channel):
        #self.apiLogger.log('Getting #%s event chat status...' % channel)
        chatAddress = 'http://api.twitch.tv/api/channels/' + channel + '/chat_properties'
        rawJson = urllib2.urlopen(chatAddress)
        twitchJson = json.load(rawJson)

        serverList = []

        if twitchJson['eventchat']:
            self.apiLogger.log('Event chat is true.')
            for serv in twitchJson['chat_servers']:
                serverList.append(serv)
            #return serverList
            return True
        else:
            return False

    def getEmotes(self, emoteSet):
        self.apiLogger.log('Getting emotes for emote set %s...' % emoteSet)
        emoteAddress = 'http://api.twitch.tv/kraken/chat/emoticon_images?emotesets=' + emoteSet
        rawJson = urllib2.urlopen(emoteAddress)
        twitchJson = json.load(rawJson)

        emotes = {}
        rawEmotes = twitchJson['emoticon_sets'][emoteSet]
        for pair in rawEmotes:
            emotes[pair['code']] = pair['id']

        return emotes
