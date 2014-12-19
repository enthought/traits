from __future__ import absolute_import

from traits._version import full_version as __version__

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
