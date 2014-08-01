import tornado.ioloop
import tornado.web
import tornado.websocket
import os

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

#list of connected clients
clients = []

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        clients.append(self)
        self.stream.set_nodelay(True)
        self.write_message(u"Welcome to KappaFeed!")

    def on_message(self, message):
        print "~SERVER~ Received a message : %s" % (message)
        self.write_message(u"You said: " + message)
        
    def on_close(self):
        clients.remove(self)

def sendToClients(message):
    for client in clients:
        if not client.ws_connection.stream.socket:
            print "~SERVER~ client left"
            clients.remove(client)
        else:
            client.write_message(message)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/feed/', WebSocketHandler),
    (r"/(kappa\.js)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
    (r"/(kappa\.css)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
])

def startServer():
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
