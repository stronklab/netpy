class Task:
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

    def __iter__(self):
        return iter(self.args)

    def __getitem__(self, key):
        return self.kwargs.get(key)

    def __str__(self):
        args = ", ".join(map(str, self.args))
        kwgs = ", ".join("%s:%s" % kv for kv in self.kwargs.items())
        if len(kwgs) > 0:
            return  "%s; %s" % (args, kwgs)
        return args

    def keys(self):
        return self.kwargs.keys()