import Logger

import tornado.ioloop
import tornado.web
import tornado.websocket
import os
from tornado.options import define, options, parse_command_line

define("port", default=80, help="run on the given port", type=int)

clients = []
servLogger = Logger.Logger('serv')

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("website/index.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        servLogger.log('Client connect.')
        clients.append(self)
        self.stream.set_nodelay(True)

    def on_message(self, message):
        servLogger.log('Received a message: %s' % message)

    def on_close(self):
        servLogger.log('Client closed socket.')
        clients.remove(self)

def sendToClients(message):
    encodedMsg = tornado.escape.json_encode(message)

    for client in clients:
        if not client.ws_connection.stream.socket:
            servLogger.log('No client available.')
            clients.remove(client)
        else:
            client.write_message(encodedMsg)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "website_path": os.path.join(os.path.dirname(__file__), "website"),
}

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/index', IndexHandler),
    (r'/feed', WebSocketHandler),
    (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
],**settings)

def startServer():
    servLogger.log('Starting server...')
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    startServer()
