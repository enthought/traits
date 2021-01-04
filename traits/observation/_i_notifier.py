# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import abc


class INotifier(abc.ABC):
    """ Interface for all notifiers.

    An instance of notifier must be a callable, i.e. ``__call__`` must be
    implemented and cannot be None. The signature of that callable should be
    compatible with the observables the notifier will be given to. This
    interface does not define what that signature should be.
    """

    def __call__(self, *args, **kwargs):
        """ Called by an observable.
        The signature is not restricted by the interface.
        """
        raise NotImplementedError("__call__ must be implemented.")

    def add_to(self, observable):
        """ Add this notifier to the observable.

        Parameters
        ----------
        observable : IObservable
        """
        raise NotImplementedError("add_to must be implemented.")

    def remove_from(self, observable):
        """ Remove this notifier or a notifier equivalent to this one
        from the observable.

        Parameters
        ----------
        observable : IObservable

        Raises
        ------
        NotifierNotFound
            If the notifier cannot be found.
        """
        raise NotImplementedError("remove_from must be implemented.")
