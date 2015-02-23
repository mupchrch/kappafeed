from time import strftime
from sys import stdout

class Logger(object):

    def __init__(self, className):
        self.className = className

    def log(self, msg):
        timeStamp = strftime("%Y-%m-%d %H:%M:%S")
        print '{%s} [%s] %s' % (self.className, timeStamp, msg)
        stdout.flush()
