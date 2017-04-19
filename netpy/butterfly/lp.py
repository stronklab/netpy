from tornado.tcpserver import TCPServer
from tornado.tcpclient import TCPClient
from tornado.iostream import StreamClosedError
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen


class lp:
    callbacks = []

    @classmethod
    def later(cls, fn):
        cls.callbacks.append(fn)

    @classmethod
    def start(cls):
        import signal
        import logging

        is_closing = []

        def try_exit(): 
            if is_closing:
                IOLoop.current().stop()
                logging.info('exit success')

        def signal_handler(signum, frame):
            logging.info('exiting...')
            is_closing.append(0)

        signal.signal(signal.SIGINT, signal_handler)
        PeriodicCallback(try_exit, 100).start()
        for cb in cls.callbacks:
            IOLoop.current().spawn_callback(cb)
        IOLoop.current().start()