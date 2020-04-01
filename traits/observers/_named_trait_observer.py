# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
from traits.observers._interfaces import IObserver


class NamedTraitObserver(IObserver):
    """ Observer for observing changes on a named trait
    on an instance of HasTraits.
    """

    def __init__(self, *, name, notify):
        """ Initializer.
        Once this observer is defined, it should not be mutated.

        Parameters
        ----------
        name : str
            Name of the trait to be observed.
        notify : boolean
            Whether to notify for changes.
        """
        self._name = name
        self._notify = notify

    @property
    def name(self):
        """ Name of trait to observe on any given HasTraits object."""
        return self._name

    @property
    def notify(self):
        """ A boolean for whether this observer will notify
        for changes.
        """
        return self._notify

    def __hash__(self):
        return hash((type(self), self.name, self.notify))

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.notify == other.notify
        )
