import functools
import os
import pathlib


DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


@functools.lru_cache
def load_file(name: str):
    return open(DIR / 'data' / name, 'r').read()
