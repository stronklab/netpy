class Attrs:
    viewport = 8123
    port = 39512
    sep = "thisisdummysep"
    greet = "hi"
    notask = "no"


def settings(**kwargs):
    Attrs.__dict__.update(kwargs)