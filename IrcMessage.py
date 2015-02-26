

class IrcMessage(object):

    def __init__(self, col, emo, sub, tur, usr, pre, com, arg):
        self.color = col
        self.emotes = emo
        self.subscriber = sub
        self.turbo = tur
        self.userType = usr
        self.prefix = pre
        self.command = com
        self.args = arg
