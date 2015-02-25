import Logger

import urllib2
import json

class TwitchApi(object):

    def __init__(self):
        self.address = 'https://api.twitch.tv/kraken/'
        self.apiLogger = Logger.Logger('api')

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
