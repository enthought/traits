# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Base classes for adapters.

Adapters do not have to inherit from these classes, as long as their
constructor takes the object to be adapted as the first and only
*positional* argument.

"""


from traits.has_traits import HasTraits
from traits.trait_types import Any


class PurePythonAdapter(object):
    """ Base class for pure Python adapters. """

    def __init__(self, adaptee):
        self.adaptee = adaptee


class Adapter(HasTraits):
    """ Base class for adapters with traits. """

    def __init__(self, adaptee, **traits):
        traits["adaptee"] = adaptee
        super().__init__(**traits)

    adaptee = Any
