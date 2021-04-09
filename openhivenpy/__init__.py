"""

OpenHiven.py - The OpenSource Python API Wrapper for Hiven

---

Under MIT License

Copyright © 2020 - 2021 Nicolas Klatzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

__title__ = "openhiven.py"
__author__ = "Nicolas Klatzer"
__license__ = "MIT"
__version__ = "0.1.3.1"
__copyright__ = "Nicolas Klatzer"

import logging

from openhivenpy.settings import load_env
# Loading the environment
load_env()

from . import exception
from . import utils
from . import types
from . import events
from . import gateway
from .client import *

logging.getLogger(__name__).addHandler(logging.NullHandler())
