import socket
import re
import server
import urllib2
import json
import time

serverAddress = "irc.twitch.tv"
portNumber = 80
nickname = "mupchrch"
realName = "mupchrch"
password = "oauth:d1ebu8gjs0aa0f49stppqxs7uqgeph7"
#these will be the top 25 streams using twitch api at some point:
channelNames = []
numChannelsToJoin = 25
emote = r'Kappa'

def parseMessage(s):
   """Breaks a message from an IRC server into its prefix, command, and arguments.
   """
   prefix = ''
   trailing = []
   if not s:
      raise IRCBadMessage("Empty line.")
   if s[0] == ':':
      prefix, s = s[1:].split(' ', 1)
   if s.find(' :') != -1:
      s, trailing = s.split(' :', 1)
      args = s.split()
      args.append(trailing)
   else:
      args = s.split()
   command = args.pop(0)
   return prefix, command, args

def emoteFilter(s, filt):
   #Finds messages with the specified emote regex in them
   return filt.search(s)

def logToConsole(s):
   print '{kf} ' + s

def getTopStreams():
   logToConsole('Getting top streams...')
   rawjson = urllib2.urlopen('https://api.twitch.tv/kraken/streams')
   twitchJson = json.load(rawjson)

   numChan = 0

   for twitchStream in twitchJson['streams']:
      if numChan == numChannelsToJoin:
         break
      channelNames.append('#' + twitchStream['channel']['name'])
      numChan += 1

def chatConnect():
   getTopStreams()
   logToConsole('Connecting to Twitch...')

   irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   irc.connect((serverAddress, portNumber))

   irc.send('PASS %s\r\n' % password)
   irc.send('NICK %s\r\n' % nickname)
   irc.send('USER %s %s %s :%s\r\n' % (nickname, serverAddress, nickname, realName))
   return irc

def joinChannels(irc):
   logToConsole('Joining channels...')
   for channel in channelNames:
      irc.send('JOIN %s\r\n' % channel)
      channelStartTime = time.time()
      numJoinAttempts = 0
      while True:
         joinData = irc.recv(512)
         if joinData:
            joinPrefix, joinCommand, joinArgs = parseMessage(joinData)
            if joinCommand == 'JOIN':
               if joinArgs[0] == channel:
                  logToConsole('Channel %s started.' % channel)
                  break
         if time.time() - channelStartTime >= 1:
            numJoinAttempts += 1
            if numJoinAttempts == 3:
               logToConsole('Failed to join channel %s.' % channel)
               channelNames.remove(channel)
               break
            irc.send('JOIN %s\r\n' % channel)
            channelStartTime = time.time()

def channelScan(irc):
   logToConsole('Scanning for %s...' % emote)
   kappaStartTime = time.time()
   while True:
      try:
         data = irc.recv(512) #Make Data the Receive Buffer
         if data:
            prefix, command, args = parseMessage(data)
            if command == 'PRIVMSG':
               twitchUser = prefix[:prefix.find('!')]
               twitchChannel = args[0]
               twitchMsg = args[1].rstrip('\r\n')
               if 'PRIVMSG' not in twitchMsg:
                  filt = re.compile(r'(^|\s|\W)' + emote + r'($|\s|\W)')
                  if emoteFilter(twitchMsg, filt):
                     #We didn't find a 'Kappa' Kappa
                     server.sendToClients('%s -> %s: %s' % (twitchChannel, twitchUser, twitchMsg))
                     #print('{kf}%s -> %s: %s' % (twitchChannel, twitchUser, twitchMsg))
         if time.time() - kappaStartTime >= 3600:
            break
      except:
         pass

def partChannels(irc):
   logToConsole('Parting channels...')
   for channel in channelNames:
      irc.send('PART %s\r\n' % channel)
      channelLeaveTime = time.time()
      numPartAttempts = 0
      while True:
         partData = irc.recv(512)
         if partData:
            partPrefix, partCommand, partArgs = parseMessage(partData)
            if partCommand == 'PART':
               if partArgs[0] == channel:
                  channelNames.remove(channel)
                  logToConsole('Failed to part channel %s.' % channel)
                  break
         if time.time() - channellLeaveTime >= 1:
            numPartAttempts += 1
            if numPartAttempts == 3:
               logToConsole('Failed to part channel %s.' % channel)
               channelNames.remove(channel)
               break
            irc.send('PART %s\r\n' % channel)
            channelLeaveTime = time.time()
   if len(channelNames) > 0:
      channelsNotLeft = ''
      for channel in channelNames:
         channelsNotLeft += channel + ' '
      logToConsole('Channels not left(GettingToThisPrintStatementIsPrettyBad.jpg): ' + channelsNotLeft)
   channelNames = []

def startKappaFeed():
   irc = chatConnect()
   while True:
      joinChannels(irc)
      channelScan(irc)
      partChannels(irc)
