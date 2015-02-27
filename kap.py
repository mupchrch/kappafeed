import server
import KappaFeed
from threading import Thread

def main():
    serverThread = Thread(target = server.startServer, args = [])
    serverThread.start()

    kappaFeed = KappaFeed.KappaFeed()
    kappaThread = Thread(target = kappaFeed.startKappaFeed, args = [])
    kappaThread.start()

if  __name__ =='__main__':
    main()
