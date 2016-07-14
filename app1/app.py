import os
import argparse
import six
import txaio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import asyncio
import sys
import logging
log  = logging.getLogger(__name__)

async def get_date():
    # code = 'import datetime; print(datetime.datetime.now())'

    # Create the subprocess, redirect the standard output into a pipe
    proc = await asyncio.create_subprocess_shell("sleep 30; echo fet", stdout=asyncio.subprocess.PIPE)
    log.info("Process created")

    data = await proc.stdout.readline()
    line = data.decode('ascii').rstrip()
    log.info("Process returned")

    # Wait for the subprocess exit
    await proc.wait()
    return line
    #future.set_result(line)


class ClientSession(ApplicationSession):
    """
    Our WAMP session class .. place your app code here!
    """

    def onConnect(self):
        self.log.info("App1 connected")
        self.join(self.config.realm, [u'anonymous'])

    def onChallenge(self, challenge):
        self.log.info("Challenge for method {authmethod} received", authmethod=challenge.method)
        raise Exception("We haven't asked for authentication!")

    async def onJoin(self, details):
        self.log.info("App1 session joined {details}", details=details)

        counter = 0
        while True:
            self.publish('com.app1.oncounter', counter)
            counter += 1
            await asyncio.sleep(1)
            try:
                sum = await self.call('com.mathservice.add', counter, counter * 2)
            except:
                self.log.info("not registerd")
            else:
                self.log.info("sum: {}".format(sum))

            def on_date_done(f):
                self.log.info("date done: {}".format(f.result()))

            #future = asyncio.Future()
            #asyncio.ensure_future(get_date(future))
            #future.add_done_callback(on_date_done)
            date_task = asyncio.ensure_future(get_date())
            date_task.add_done_callback(on_date_done)


        self.leave()

    def onLeave(self, details):
        self.log.info("Router session closed ({details})", details=details)
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Router connection closed")
        try:
            asyncio.get_event_loop().stop()
        except:
            pass


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
    runner.run(ClientSession)
