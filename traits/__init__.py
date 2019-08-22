from __future__ import absolute_import

try:
    from traits._version import full_version as __version__
except ImportError:
    # If we get here, we're using a source tree that hasn't been created via
    # the setup script. That likely also means that the ctraits extension
    # hasn't been built, so this isn't a viable Traits installation. OTOH, it
    # can be useful if a simple "import traits" doesn't actually fail.
    __version__ = "unknown"

# Add a NullHandler so 'traits' loggers don't complain when they get used.
import logging


class NullHandler(logging.Handler):
    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None


logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

del logging, logger, NullHandler
