from multiprocessing import Process
from sys import argv
from itertools import imap

from butterfly import *

import aaargh

app = aaargh.App(description="`Distributed` computing of network usage")
settings(port=39512, viewport=8123)


@app.cmd
def serve():
    @server
    def tasks():
        for i in xrange(1, 10000):
            yield (i,), {}
    viewer.init()
    lp.start()


def wrapped_worker():
    @client
    def worker(i):
        return 37**i % 997
    lp.start()

@app.cmd
@app.cmd_arg("-c", "--count", type=int, default=1, help="Count of serving workers")
def work(count):
    print "Staring %d processes" % count
    processes = []
    for i in xrange(0, count):
        processes.append(Process(target=wrapped_worker))
        processes[-1].start()
    for p in processes:
        p.join()


if __name__ == "__main__":
    app.run()