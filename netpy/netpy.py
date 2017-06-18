from multiprocessing import Process
from sys import argv
from itertools import imap

from butterfly import *
from network import *

import aaargh

app = aaargh.App(description="`Distributed` computing of network usage")
settings(port=39512, viewport=8123)
net = Network()

class ServeObserver:
    @property
    def progress(self):
        return float(len(self.complete))/self.count_tasks

    def get(self):
        self.write("Hello!<br/>")
        self.write("Currently complete %.2f%%" % self.progress)


class WorkerObserver:
    def get(self):
        self.write("Not implemented")


@app.cmd
@app.cmd_arg("-o", "--observer", action="store_const", const=True, help="Start observer of tasks completing")
@app.cmd_arg("-p", "--port", type=int, default=None, help="Remote server's port")
@server.spawn(ServeObserver)
def serve():
    import numpy as np
    for i in np.linspace(0.06, 14, 40):
        yield (i,), {}


@app.cmd
@app.cmd_arg("-c", "--count", type=int, default=1, help="Count of serving workers")
@app.cmd_arg("-s", "--server", type=str, default="localhost", help="Remote server's ip")
@app.cmd_arg("-p", "--port", type=int, default=None, help="Remote server's port")
@app.cmd_arg("-o", "--observer", action="store_const", const=True, help="Start observer of tasks completing")
@app.cmd_arg("-e", "--encode", action="store_const", const=True, help="Start observer of tasks completing")
@app.cmd_arg("-f", "--forcencode", action="store_const", const=True, help="Start observer of tasks completing")
@client.spawn(WorkerObserver)
def worker(h, e, f):
    return net.run(h)


if __name__ == "__main__":
    app.run()