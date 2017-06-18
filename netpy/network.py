import random

from earl import Graph


class Packet:
    def __init__(self, msg):
        self.msg = msg
        self.src = msg.src
        self.dst = msg.dst
        self.time = msg.time


class Event:
    def __init__(self, time, obj, **kwargs):
        self.type = type(obj)
        self.obj = obj
        self.time = time
        self.kwargs = kwargs

    def __getitem__(self, key):
        return self.kwargs.__getitem__(key)

class TX:
    def __init__(self, p):
        self.packet = p

    def __getattr__(self, key):
        return self.packet.__getattr__(key)


class Deliver:
    def __init__(self, p):
        self.packet = p

    def __getattr__(self, key):
        return self.packet.__getattr__(key)


class Collected:
    def __init__(self, m):
        self.msg = m

    def __getattr__(self, key):
        return self.msg.__getattr__(key)


class Error:
    def __init__(self, p):
        self.packet = p

    def __getattr__(self, key):
        return self.packet.__getattr__(key)


class Message:
    def __init__(self, n, src, dst):
        self.count = n
        self.src = src
        self.dst = dst

    def __nonzero__(self):
        return self.count == 0 and self.delivered == True

    def __isub__(self, v):
        self.count -= 1


class Encoded(list):
    n, k = 15, 11
    
    def __init__(self, packets):
        self.count = self.k
        map(self.append, packets)

    def __nonzero__(self):
        return self.count == 0 and self.delivered == True

    def __isub__(self, v):
        self.count -= 1


class Router:
    def __init__(self, graph):
        self.graph = graph
        self.build()

    def build(self):
        self.table = dict()
        for src in self.graph:
            for dst in self.graph:
                if src is not dst:
                    paths = set(path[0] for path in self.graph.paths(src, dst))
                    self.table[src][dst] = paths

    def next(self, p):
        if p.curr.deep > 0:
            return self.table[p.src][p.dst][0]
        return min(self.table[p.curr][p.dst], key=lambda x: len(x.buffer))

    def update(self, n):
        self.build()


class Network(Graph):
    def __init__(self, router=Router, usecode=False, forcecode=False):
        Graph.__init__(kwargs)
        self.events = []
        self.buffer = {v: {u: [] for u in self if u != v} for v in self}
        self.code = usecode
        self.forcecode = forcecode
        self.stats = {"msg": [], "pak": []}
        self.router = router(self)

    def dispatch(self, e):
        if e.type == Node:
            self.router.update(e.obj)

        if e.type == Message or e.type == Encoded:
            e.obj.time = self.time
            for _ in e.obj:
                packet = Packet(e.obj)
                self.events.append(Event(self.time, packet))
            if self.forcecode:
                self.events.append(Event(self.time, Encoded(), src=e.obj.src, dst=e.obj.dst))

        if e.type == Encoded:
            enc = Encoded(self.buffer[e.obj.src][e.obj.dst])
            for i in xrange(0, enc.n):
                    self.events.append(Event(self.time + e.obj.curr.distr.tx_awt(e.obj, self), TX(Packet(enc))))

        if e.type == Packet:
            if not self.code:
                self.events.append(Event(self.time + e.obj.curr.distr.tx_awt(e.obj, self), TX(packet)))
            else:
                self.buffer[e.obj.src][e.obj.dst].append(e.obj)
                if len(self.buffer[e.obj.src][e.obj.dst]) == Encoded.k:
                    enc = Encoded(self.buffer[e.obj.src][e.obj.dst])
                    for i in xrange(0, enc.n):
                        self.events.append(Event(self.time + e.obj.curr.distr.tx_awt(e.obj, self), TX(Packet(enc))))

        if e.type == TX:
            if e.obj.curr.distr.drop():
                self.events.append(Event(self.time, Error(packet)))
            else:
                e.obj.curr, dt = self.router.next(e.obj), e.obj.atime
                if e.obj.curr != e.obj.dst:
                    self.events.append(Event(self.time + dt, TX(packet)))
                    e.obj.atime = e.obj.curr.distr.tx_awt(e.obj, self)
                else:
                    self.events.append(Event(self.time + dt, Deliver(packet)))

        if e.type == Deliver:
            self.stats["pak"].append(self.time - e.obj.time)
            e.obj.msg -= 1
            if not e.obj.msg:
                self.events.append(Event(self.time, Collected(packet)))

        if e.type == Error:
            if not self.code:
                e.obj.curr = e.obj.src
                e.obj.atime = e.obj.curr.distr.tx_awt(e.obj, self)

        if e.type == Collected:
            if type(e.obj) == Encoded:
                for packet in e.obj:
                    self.events.append(Event(self.time, Deliver(packet)))
            self.stats["msg"].append(self.time - e.obj.time)

    def run(self, h=1, limit=10e9, e=None, f=None):
        if e is not None:
            self.code = e
        if f is not None:
            self.forcecode = f
        self.limit = limit
        while True:
            event = min(self.events, key=lambda e: e.time)
            self.events.remove(event)
            self.time = event.time
            self.dispatch(event)
        return self.stats