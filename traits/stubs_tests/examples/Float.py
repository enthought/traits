# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Float, HasTraits


class HasIndex:
    """Class with __index__ method; instances should be assignable to Float."""
    def __index__(self):
        return 1729


class HasFloat:
    """Class with __float__ method; instances should be assignable to Float."""
    def __float__(self):
        return 1729.0


class Test(HasTraits):
    i = Float()


o = Test()
o.i = "5"  # E: assignment
o.i = 5
o.i = 5.5
o.i = HasIndex()
o.i = HasFloat()
