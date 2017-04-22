class Attrs:
    ip = "localhost"
    viewport = 8123
    port = 39511
    sep = "thisisdummysep"
    greet = "hi"
    notask = "no"


def settings(**kwargs):
    Attrs.__dict__.update(kwargs)