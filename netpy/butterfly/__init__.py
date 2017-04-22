import pickle
import functools

import tornado.web

from lp import *
from attrs import *
from task import *
from observer import *


def call(fn):
    fn()


class server(TCPServer, Observer, Attrs):
    @classmethod
    def spawn(cls, obs):
        def more_wrapped(fn):
            @functools.wraps(fn)
            def wraped(observer):
                cls.instance = cls.type(fn)
                if observer:
                    cls.instance.start_observer()
                lp.start()
            return wraped
        cls.type = type("observed", (cls, obs), {})
        return more_wrapped

    def __init__(self, genfn):
        TCPServer.__init__(self)

        self.tasks = list(genfn())
        self.count_tasks = len(self.tasks)
        self.tasks = iter(enumerate(self.tasks))
        self.complete = list()
        self.listen(self.port)
        self.start()
        print "Server started at", self.port

    @gen.coroutine
    def handle_stream(self, stream, address):
        while True:
            try:
                i, task = self.tasks.next()
                data = yield stream.read_until(self.sep)
                prev, data = pickle.loads(data)
                if data != "hi":
                    print "From %s:%s received %s for %s" % (address[0], address[1], data, prev)
                    self.complete.append((prev, data))
                else:
                    print "Connected:", address
                task = Task(*task[0], **task[1])
                yield stream.write(pickle.dumps(task) + self.sep)
            except StreamClosedError:
                return
            except StopIteration:
                break

        while True:
            yield stream.write(pickle.dumps(self.notask) + self.sep)


class client(TCPClient, Observer, Attrs):
    ret = (None, Attrs.greet)

    @classmethod
    def spawn(cls, obs):
        def more_wrapped(fn):
            @classmethod
            def spawner(cls):
                instance = cls.type(fn)
                lp.start()
            cls.spawner = spawner

            @functools.wraps(fn)
            def wraped(count, observer, server):
                if count > 1:
                    from multiprocessing import Process
                    processes = []
                    for i in xrange(0, count):
                        processes.append(Process(target=cls.spawner))
                        processes[-1].start()
                    for p in processes:
                        p.join()
                else:
                    cls.spawner()
            return wraped
        cls.type = type("observed", (cls, obs), {})
        return more_wrapped

    def __init__(self, workfn):
        TCPClient.__init__(self)

        self.stream = None
        self.workfn = workfn

        @call
        @gen.coroutine
        def wrap():
            print "Connecting to", self.port
            self.stream = yield self.connect(self.ip, self.port)
            self.stream.set_nodelay(True)
        lp.later(self.take)

    @gen.coroutine
    def take(self):
        import time

        while self.stream is None:
            print "Still connecting to %d..." % self.port
            yield gen.Task(IOLoop.instance().add_timeout, time.time() + 0.05)
        print "Connected!"

        try:
            while True:
                self.stream.write(pickle.dumps(self.ret) + self.sep)
                self.ret = yield self.stream.read_until(self.sep)
                self.ret = pickle.loads(self.ret)
                print "Received task:", self.ret
                self.ret = self.ret, self.workfn(*self.ret, **self.ret)
                print "Complete task (%s): %s" % self.ret
        except StreamClosedError:
            return