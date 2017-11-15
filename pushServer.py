from twisted.protocols import basic
from twisted.web.websockets import WebSocketsResource, WebSocketsProtocol, lookupProtocolForFactory
import time
import json
from twisted.internet import task
from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.application import service, internet
from twisted.internet.protocol import Factory
import RBS.utility as config


class WebsocketChat(basic.LineReceiver):
    def connectionMade(self):
        print "Got new client!"

        self.transport.write('connected ....\n')
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print "Lost a client!"
        self.factory.clients.remove(self)

    def dataReceived(self, data):
        print "dataReceived...", data
        self.factory.messages[float(time.time())] = data
        self.updateClients(data)

    def updateClients(self, data):
        for c in self.factory.clients:
            c.message(data)

    def message(self, message):
        self.transport.write(message + '\n')


class ChatFactory(Factory):
    protocol = WebsocketChat
    clients = []
    messages = {}


class HttpChat(Resource):
    # optimization
    isLeaf = True

    def __init__(self):
        self.throttle = 1
        self.delayed_requests = []
        self.messages = {}
        self.wsFactory = ChatFactory()
        loopingCall = task.LoopingCall(self.processDelayedRequests)
        loopingCall.start(self.throttle, False)
        self.wsFactory.messages = self.messages
        Resource.__init__(self)

    def render_POST(self, request):
        request.setHeader('Content-Type', 'application/json')
        args = request.args
        get_data = json.loads(request.content.getvalue())
        print "Got msg ..", get_data

        if 'data' in get_data:
            # self.messages[float(time.time())] = args['new_message'][0]

            if len(self.wsFactory.clients) > 0:
                self.wsFactory.clients[0].updateClients(request.content.getvalue())
            self.processDelayedRequests()

        print "ok"
        return json.dumps({"messsage": "sucess"})

    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/json')
        args = request.args
        print "render_GET.............", args
        if 'callback' in args:
            request.jsonpcallback = args['callback'][0]
        if 'lastupdate' in args:
            request.lastupdate = float(args['lastupdate'][0])
        else:
            request.lastupdate = 0.0
        if request.lastupdate < 0:
            return self.__format_response(request, 1, "connected...", timestamp=0.0)
            # get the next message for this user
        data = self.getData(request)
        if data:
            return self.__format_response(request, 1, data.message, timestamp=data.published_at)

        self.delayed_requests.append(request)
        return NOT_DONE_YET

        # returns the next sequential message,

    # and the time it was received at
    def getData(self, request):
        for published_at in sorted(self.messages):
            if published_at > request.lastupdate:
                return type('obj', (object,), {'published_at': published_at, "message": self.messages[published_at]})();
        return

    def processDelayedRequests(self):
        for request in self.delayed_requests:
            data = self.getData(request)

            if data:
                try:
                    request.write(self.__format_response(request, 1, data.message, data.published_at))
                    request.finish()
                except:
                    print 'connection lost before complete.'
                finally:
                    self.delayed_requests.remove(request)

    def __format_response(self, request, status, data, timestamp=float(time.time())):
        response = json.dumps({'status': status, 'timestamp': timestamp, 'data': data})

        if hasattr(request, 'jsonpcallback'):
            return request.jsonpcallback + '(' + response + ')'
        else:
            return response


resource = HttpChat()
factory = Site(resource)
ws_resource = WebSocketsResource(lookupProtocolForFactory(resource.wsFactory))
root = Resource()
root.putChild("rbsHTTP", resource)
root.putChild("rbsTCP", ws_resource)
application = service.Application("pushServer")
internet.TCPServer(config.push_server_port, Site(root), interface='0.0.0.0').setServiceParent(application)