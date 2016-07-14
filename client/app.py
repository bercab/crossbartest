import os
import argparse
import six
import txaio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import asyncio


class Component1(ApplicationSession):

    def onConnect(self):
        self.log.info("client connected")
        self.join(self.config.realm, [u'anonymous'])


    async def onJoin(self, details):
        self.log.info("Client session joined {details}", details=details)
        self.received = 0
        results = await self.subscribe(self)
        for res in results:
            if isinstance(res, wamp.protocol.Subscription):
                print("Ok, subscribed handler with subscription ID {}".format(res.id))
            else:
                print("Failed to subscribe handler: {}".format(res))

        results = await self.register(self)
        for res in results:
            if isinstance(res, wamp.protocol.Registration):
                print("Ok, registered procedure with subscription ID {}".format(res.id))
            else:
                print("Failed to register procedure: {}".format(res))

        #def onevent(msg):
        #    self.log("Client 1 Got event: {}".format(msg))

        #await self.subscribe(onevent, u'com.app1.oncounter')
        #self.leave()

    def onLeave(self, details):
        self.log.info("Client Router session closed ({details})", details=details)
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Client1 router connection closed")
        asyncio.get_event_loop().stop()

    @wamp.subscribe(u'com.app1.oncounter')
    def on_counter_event(self, i):
        self.log.info("client Got event on topic1: {}".format(i))
        self.received += 1
        if self.received > 5:
            self.leave()

    @wamp.register(u'com.mathservice.add')
    def add2(self, x, y):
        return x + y


if __name__ == '__main__':

    # Crossbar.io connection configuration
    url = os.environ.get('CBURL', u'ws://localhost:8080/ws')
    realm = os.environ.get('CBREALM', u'realm1')

    # parse command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output.')
    parser.add_argument('--url', dest='url', type=six.text_type, default=url, help='The router URL (default: "ws://localhost:8080/ws").')
    parser.add_argument('--realm', dest='realm', type=six.text_type, default=realm, help='The realm to join (default: "realm1").')

    args = parser.parse_args()

    # start logging
    if args.debug:
        txaio.start_logging(level='debug')
    else:
        txaio.start_logging(level='info')

    # any extra info we want to forward to our ClientSession (in self.config.extra)
    extra = {
        u'foobar': u'A custom value'
    }

    # now actually run a WAMP client using our session class ClientSession
    runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra)
    runner.run(Component1)
