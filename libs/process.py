from __future__ import absolute_import

import sys
import logging

log = logging.getLogger("process")
# log.setLevel(logging.DEBUG)

try:
    from subprocess32 import Popen
except ImportError:
    if sys.platform != "win32" and sys.version_info[0] < 3:
        log.warn("Could not import subprocess32 module, falling back to subprocess module")
    # Not available on Windows - fallback to using regular subprocess module.
    from subprocess import Popen


class ProcessOpen(Popen):
    pass
