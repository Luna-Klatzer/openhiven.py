"""

OpenHiven.py - The OpenSource Python API Wrapper for Hiven

---

Under MIT License

<<<<<<< HEAD
Copyright © 2020 - 2021 Nicolas Klatzer
=======
Copyright © 2020 - 2021 Luna Klatzer
>>>>>>> v0.2_rewrite

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
__version__ = "0.2.alpha1"
__copyright__ = "Luna Klatzer"

import logging

# Loading the environment variables which contain basic configuration for the base-lib variables
# (heartbeat, timeout etc.)
from openhivenpy.settings import load_env_vars
from . import exceptions

load_env_vars()

from .types import Object
from . import utils
from . import events
from . import gateway
from .types import *
from .client import *

logging.getLogger(__name__).addHandler(logging.NullHandler())
