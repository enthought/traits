# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


class IObserver:
    """ Interface for all observers.

    Each instance of ``IObserver`` can be a node in the
    ``ObserverPath``. These objects are considered
    low-level objects not to be instantiated directly by the
    user. In order to support equality and hashing on the
    ``ObserverPath``, ``IObserver`` needs to be hashable
    and it needs to support comparison for equality.
    """

    def __hash__(self):
        """ Return a hash of this object."""
        raise NotImplementedError("Subclass must implement __hash__.")

    def __eq__(self, other):
        """ Return true if this observer is equal to the given one."""
        raise NotImplementedError("Subclass must implement __eq__.")

    @property
    def notify(self):
        """ A boolean for whether this observer will notify
        for changes.
        """
        raise NotImplementedError(
            "Subclass should implement this property.")
