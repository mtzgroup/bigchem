from importlib import metadata as _metadata

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:
    # Source tree / build hook / CI checkout
    __version__ = "0.0.0+local"

# Patch for numpy v1 API used by qcengine
import numpy as np

if not hasattr(np, "defchararray"):
    np.defchararray = np.char  # type: ignore

from .algos import *
from .canvas import *
from .tasks import *
