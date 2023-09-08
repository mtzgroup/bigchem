# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
from importlib import metadata

__version__ = metadata.version(__name__)

from .algos import *
from .canvas import *
from .tasks import *
