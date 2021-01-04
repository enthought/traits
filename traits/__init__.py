# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

try:
    from traits.version import version as __version__
except ImportError:
    # If we get here, we're using a source tree that hasn't been created via
    # the setup script. That likely also means that the ctraits extension
    # hasn't been built, so this isn't a viable Traits installation. OTOH, it
    # can be useful if a simple "import traits" doesn't actually fail.
    __version__ = "unknown"
