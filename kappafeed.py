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

def parsemsg(s):
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

def emotefilter(s, filt):
   #Finds messages with the specified emote regex in them
   return filt.search(s)

def getTopStreams():
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

   irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   irc.connect((serverAddress, portNumber))

   irc.send('PASS %s\r\n' % password)
   irc.send('NICK %s\r\n' % nickname)
   irc.send('USER %s %s %s :%s\r\n' % (nickname, serverAddress, nickname, realName))
   return irc

def channelScan(irc):
   for channel in channelNames:
      irc.send('JOIN %s\r\n' % channel)
      channelStartTime = time.time()
      while True:
         da = irc.recv(512)
         pre, com, ar = parsemsg(da)
         if com == 'JOIN':
            if ar[0] == channel:
               break
         if time.time() - channelStartTime >= 3:
            irc.send('JOIN %s\r\n' % channel)
      print 'Channel %s started.' % channel

   kappaStartTime = time.time()

   while True:
      try:
         data = irc.recv(512) #Make Data the Receive Buffer

         if data:
            prefix, command, args = parsemsg(data)
            if command == 'PRIVMSG':
               twitchUser = prefix[:prefix.find('!')]
               twitchChannel = args[0]
               twitchMsg = args[1].rstrip('\r\n')

               if 'PRIVMSG' not in twitchMsg:
                  filt = re.compile(r'(^|\s|\W)' + emote + r'($|\s|\W)')
                  if emotefilter(twitchMsg, filt):
                     #We didn't find a 'Kappa' Kappa
                     server.sendToClients('%s -> %s: %s' % (twitchChannel, twitchUser, twitchMsg))
                     #print('%s -> %s: %s' % (twitchChannel, twitchUser, twitchMsg))
         if time.time() - kappaStartTime >= 3600:
            break
      except:
         pass

def startKappaFeed():
   irc = chatConnect()
   while True:
      channelScan(irc)
      channelNames = []
