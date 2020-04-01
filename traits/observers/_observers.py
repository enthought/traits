# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


class BaseObserver:
    """ Base class for all observers.

    Each instance of ``BaseObserver`` can be a node in the
    ``ObserverPath``. These objects are considered
    low-level objects not to be instantiated directly by the
    user. In order to support equality and hashing on the
    ``ObserverPath``, ``BaseObserver`` needs to be hashable
    and it needs to support comparison for equality.

    This class will have more meaningful methods later
    when the ``observe`` mechanism is implemented.
    (enthought/traits#???)
    """

    @property
    def notify(self):
        """ A boolean for whether this observer will notify
        for changes.
        """
        raise NotImplementedError(
            "Subclass should implement this property.")


class NamedTraitObserver(BaseObserver):
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
        return self._name

    @property
    def notify(self):
        """ A boolean for whether this observer will notify
        for changes.
        """
        return self._notify

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.notify == other.notify
        )
