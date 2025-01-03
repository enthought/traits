# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Examples for lazy adapter factories.

This module should be only imported when the adaptation takes place.
"""


class IBar(object):
    pass


class IBarToIFoo(object):
    pass


class IFoo(object):
    pass
