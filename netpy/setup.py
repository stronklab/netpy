from distutils.core import setup
import py2exe

opts = dict(
    py2exe = {
        "dist_dir": "../dist",
    }
)

setup(console=["netpy.py"], options=opts)