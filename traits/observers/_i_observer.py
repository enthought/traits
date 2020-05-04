# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import abc


class IObserver(abc.ABC):
    """ Interface for all observers.

    Each instance of ``IObserver`` can be a node in the
    ``ObserverGraph``. These objects are considered
    low-level objects not to be instantiated directly by the
    user. In order to support equality and hashing on the
    ``ObserverGraph``, ``IObserver`` needs to be hashable
    and it needs to support comparison for equality.
    """

    def __hash__(self):
        """ Return a hash of this object."""
        raise NotImplementedError("__hash__ must be implemented.")

    def __eq__(self, other):
        """ Return true if this observer is equal to the given one."""
        raise NotImplementedError("__eq__ must be implemented.")
