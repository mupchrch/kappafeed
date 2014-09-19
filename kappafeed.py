import socket
import re
import server
import urllib2
import json
import time
import sys

serverAddress = "irc.twitch.tv"
portNumber = 80
nickname = "mupchrch"
realName = "mupchrch"
password = "oauth:d1ebu8gjs0aa0f49stppqxs7uqgeph7"
numChannelsToJoin = 25
emote = r'Kappa'

def parseMessage(s):
   """Breaks a message from an IRC server into its prefix, command, and arguments.
   """
   prefix = ''
   trailing = []
   command = 'UNKNOWN'
   args = []

   if not s:
      #raise IRCBadMessage("Empty line.")
      logToConsole('Empty line in IRC message.')
      return prefix, command, args

   try:
      if s[0] == ':':
         prefix, s = s[1:].split(' ', 1)
      if s.find(' :') != -1:
         s, trailing = s.split(' :', 1)
         args = s.split()
         args.append(trailing)
      else:
         args = s.split()
   except:
      logToConsole('Error in parseMessage.')
      return prefix, command, args

   if len(args) == 0:
      logToConsole('No command in IRC message.')
   else:
      command = args.pop(0)

   return prefix, command, args

def emoteFilter (s, filt):
   #Finds messages with the specified emote regex in them
   return filt.search(s)

def logToConsole(s):
   print '{kf} [' + time.strftime("%Y-%m-%d %H:%M:%S") + '] ' + s
   sys.stdout.flush()

def getTopStreams():
   logToConsole('Getting top streams...')
   rawjson = urllib2.urlopen('https://api.twitch.tv/kraken/streams')
   twitchJson = json.load(rawjson)

   numChan = 0
   topChannels = []

   for twitchStream in twitchJson['streams']:
      if numChan == numChannelsToJoin:
         break
      topChannels.append('#' + twitchStream['channel']['name'])
      numChan += 1
   return topChannels

def chatConnect():
   logToConsole('Connecting to Twitch...')

   irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   irc.connect((serverAddress, portNumber))

   irc.send('PASS %s\r\n' % password)
   irc.send('NICK %s\r\n' % nickname)
   irc.send('USER %s %s %s :%s\r\n' % (nickname, serverAddress, nickname, realName))
   return irc

   def joinChannels(irc):
   channelsToJoin = getTopStreams()
   logToConsole('Joining channels...')
   for channel in channelsToJoin:
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
               channelsToJoin.remove(channel)
               break
            irc.send('JOIN %s\r\n' % channel)
            channelStartTime = time.time()
   return channelsToJoin

def channelScan(irc):
   logToConsole('Scanning for %s...' % emote)
   kappaStartTime = time.time()
   while True:
      data = irc.recv(512) #TODO sometimes 2 msgs come together... fix it so we don't lose 2nd msg?
      if data:
         prefix, command, args = parseMessage(data)
         if command == 'PRIVMSG':
            twitchUser = prefix[:prefix.find('!')]
            twitchChannel = args[0]
            twitchMsg = args[1].rstrip('\r\n')
            if 'PRIVMSG' not in twitchMsg:
               filt = re.compile(r'\b' + emote + r'\b')
               if emoteFilter(twitchMsg, filt):
                  try:
                     server.sendToClients({'channel': twitchChannel.decode('utf8'), 'user': twitchUser.decode('utf8'), 'msg': twitchMsg.decode('utf8')})
                  except:
                     pass
         elif command == 'PING':
            logToConsole('Received PING.')
            logToConsole('Sending PONG...')
            irc.send('PONG :tmi.twitch.tv\r\n')
      if time.time() - kappaStartTime >= 3600:
         break

def partChannels(irc, channelsToPart):
   logToConsole('Parting channels...')
   channelCount = 0
   channelsNotParted = []
   for channel in channelsToPart:
      irc.send('PART %s\r\n' % channel)
      channelLeaveTime = time.time()
      numPartAttempts = 0
      while True:
         partData = irc.recv(512)
         if partData:
            partPrefix, partCommand, partArgs = parseMessage(partData)
            if partCommand == 'PART':
               if partArgs[0] == channel:
                  logToConsole('Left channel %s.' % channel)
                  channelCount += 1
                  break
         if time.time() - channelLeaveTime >= 1:
            numPartAttempts += 1
            if numPartAttempts == 3:
               logToConsole('Failed to part channel %s.' % channel)
               channelsNotParted.append(channel)
               break
            irc.send('PART %s\r\n' % channel)
            channelLeaveTime = time.time()
   if numChannelsToJoin - channelCount > 0:
      logToConsole('Unable to part %i channels.' % (numChannelsToJoin - channelCount))
   return channelsNotParted

def startKappaFeed():
   while True:
      try:
         irc = chatConnect()
         channelNames = []
         while True:
            channelNames = joinChannels(irc)
            channelScan(irc)
            channelNames = partChannels(irc, channelNames)
            if len(channelNames) > 0:
               break
            logToConsole('Refreshing channel list...')
         logToConsole('Restarting kappafeed...')
      except:
         logToConsole('Error, restarting kappafeed...')