from tornado.web import RequestHandler, Application


class Observer(RequestHandler):
    viewers = []
    app = None

    def start_observer(self):
        self.app = Application(self.viewers)
        self.app.listen(self.viewport)
        print "Viewer started at", self.viewport