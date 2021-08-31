"""

openhiven.py - The OpenSource Python API Wrapper for Hiven

---

Under MIT License

Copyright © 2020 - 2021 Luna Klatzer

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
__author__ = "Luna Klatzer"
__license__ = "MIT"
__version__ = "0.2.dev3"
__copyright__ = "Luna Klatzer"

import logging

from . import events
from . import exceptions
from . import gateway
from . import utils
from .base_types import *
from .client import *
from .env_config import HivenENV
from .exceptions import *
from .types import *

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Loading the environment variables which contain basic configuration
# for the module
env = HivenENV()
env.load_env()
