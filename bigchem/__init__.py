# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
from importlib import metadata

__version__ = metadata.version(__name__)

# Patch for numpy v1 API used by qcengine
import numpy as np

if not hasattr(np, "defchararray"):
    np.defchararray = np.char  # type: ignore

from .algos import *
from .canvas import *
from .tasks import *
