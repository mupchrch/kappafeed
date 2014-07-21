import socket
import re

serverAddress = "irc.twitch.tv"
portNumber = 6667
nickname = "mupchrch"
realName = "mupchrch"
password = "oauth:d1ebu8gjs0aa0f49stppqxs7uqgeph7"
channelName = "#mupbot"
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
	"""Finds messages with the specified emote regex in them
	"""
	return filt.search(s)

def main():
	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	irc.connect((serverAddress, portNumber))

	irc.send('PASS %s\r\n' % password)
	irc.send('NICK %s\r\n' % nickname)
	irc.send('USER %s %s %s :%s\r\n' % (nickname, serverAddress, nickname, realName))
	irc.send('JOIN %s\r\n' % channelName)

	print 'Starting.'

	while True:
		data = irc.recv(4096) #Make Data the Receive Buffer
		prefix, command, args = parsemsg(data)
		if command == 'PRIVMSG':
			twitchUser = prefix[:prefix.find('!')]
			twitchMsg = args[1].rstrip('\r\n')

			if twitchMsg == 'leave':
				print 'Ending.'
				break

			filt = re.compile(r'(^|\s|\W)' + emote + r'($|\s|\W)')
			if emotefilter(twitchMsg, filt):
				#We didn't find a 'Kappa' Kappa
				print "~~~EMOTE BELOW~~~"

			print ('%s: %s' % (twitchUser, twitchMsg))

if  __name__ =='__main__':
    main()