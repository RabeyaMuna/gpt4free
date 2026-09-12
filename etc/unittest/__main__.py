import unittest

try:
    import g4f.debug

    g4f.debug.version_check = False
except Exception:
    # If g4f cannot be imported (e.g., SyntaxError during import), avoid aborting test discovery
    pass

from .asyncio import *
from .backend import *
from .client import *
from .image_client import *
from .include import *
from .main import *
from .model import *
from .models import *
from .retry_provider import *
from .thinking import *
from .web_search import *

unittest.main()
