# Copyright (c) 2008-2019 by Enthought, Inc.
# All rights reserved.

from __future__ import absolute_import

try:
    from traits.version import version as __version__
except ImportError:
    # If we get here, we're using a source tree that hasn't been created via
    # the setup script. That likely also means that the ctraits extension
    # hasn't been built, so this isn't a viable Traits installation. OTOH, it
    # can be useful if a simple "import traits" doesn't actually fail.
    __version__ = "unknown"

# Add a NullHandler so 'traits' loggers don't complain when they get used.
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging
