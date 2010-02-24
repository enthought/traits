# Wrapped in a try/except in those situations where someone hasn't installed
# as an egg.  What do we do then?  For now, we just punt since we don't want
# to define the version number in two places.

from __future__ import absolute_import

try:
    import pkg_resources
    __version__ = pkg_resources.require('Traits')[0].version
except:
    __version__ = '3.0.0'
