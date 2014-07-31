import server
import kappafeed
from threading import Thread

def main():
	serverThread = Thread(target = server.startServer, args = [])
	serverThread.start()

	kappaThread = Thread(target = kappafeed.startKappaFeed, args = [])
	kappaThread.start()

if  __name__ =='__main__':
    main()