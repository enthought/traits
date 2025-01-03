# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from functools import partial
import types
import weakref

from traits.observation.exception_handling import handle_exception
from traits.observation.exceptions import NotifierNotFound


class TraitEventNotifier:
    """ Wrapper for invoking user's handler for a trait change event.

    An instance of ``TraitEventNotifier`` is a callable to be contributed
    to an instance of ``IObserverable``, e.g. ``CTrait``, ``TraitList`` etc.,
    such that it will be called when an observerable emits notificaitons for
    changes. The call signature is defined by the observable object
    and may vary. It is the responsibility of the ``event_factory`` to adapt
    the varying call signatures and create an event object to be given
    to the user's handler.

    A ``TraitEventNotifier`` keeps a reference count in order to address
    situations where a same object is repeated inside a container
    and one would not want to fire the same change handler multiple times
    (see enthought/traits#237). For that purpose, a notifier keeps track of
    the ``HasTraits`` instance (called ``target``) on which the user applies
    the observers, keeps a reference count internally, and it also needs to
    determine whether another notifier refers to the same change handler and
    ``HasTraits`` instance.

    Since there is only one reference count associated with a notifier,
    each notifier is expected to be added to only one observable.

    Parameters
    ----------
    handler : callable(event)
        The user's handler to receive the change event.
        The event object is returned by the ``event_factory``.
        If the handler is an instance method, then a weak reference is
        created for the method. If the instance is garbage collected,
        the notifier will be muted.
    target : object
        An object for defining the context of the notifier.
        A weak reference is created for the target.
        If the target is garbage collected, the notifier will be muted.
        This target is typically an instance of ``HasTraits`` and will be
        seen by the user as the "owner" of the change handler.
        This is also used for distinguishing one notifier from another
        notifier wrapping the same handler.
    event_factory : callable(*args, **kwargs) -> object
        A factory function for creating the event object to be sent to
        the handler. The call signature must be compatible with the
        call signature expected by the observable this notifier is used
        with. e.g. for CTrait, the call signature will be
        ``(object, name, old, new)``.
    prevent_event : callable(event) -> boolean
        A callable for controlling whether the user handler should be
        invoked. It receives the event created by the event factory and
        returns true if the event should be prevented, false if the event
        should be fired.
    dispatcher : callable(handler, event)
        A callable for dispatching the handler, e.g. on a different
        thread or on a GUI event loop. ``event`` is the object
        created by the event factory.

    Raises
    ------
    ValueError
        If the handler given is not a callable.
    """

    def __init__(
            self, *, handler, target,
            event_factory, prevent_event, dispatcher):

        if not callable(handler):
            raise ValueError(
                "handler must be a callable, got {!r}".format(handler))

        # This is such that the notifier does not prevent
        # the target from being garbage collected.
        self.target = weakref.ref(target)

        if isinstance(handler, types.MethodType):
            self.handler = weakref.WeakMethod(handler)
        else:
            self.handler = partial(_return, value=handler)
        self.dispatcher = dispatcher
        self.event_factory = event_factory
        self.prevent_event = prevent_event
        # Reference count to avoid adding multiple equivalent notifiers
        # to the same observable.
        self._ref_count = 0

    def __call__(self, *args, **kwargs):
        """ Called by observables. The call signature will vary and will be
        handled by the event factory.
        """
        if self.target() is None:
            # target is deleted. The notifier is disabled.
            return

        # Hold onto the reference while invoking the handler
        handler = self.handler()

        if handler is None:
            # The instance method is deleted. The notifier is disabled.
            return

        event = self.event_factory(*args, **kwargs)
        if self.prevent_event(event):
            return
        try:
            self.dispatcher(handler, event)
        except Exception:
            handle_exception(event)

    def add_to(self, observable):
        """ Add this notifier to an observable object.

        If an equivalent notifier exists, the existing notifier's reference
        count is bumped. Hence this method is not idempotent.
        N number of calls to this ``add_to`` must be matched by N calls to the
        ``remove_from`` method in order to completely remove a notifier from
        an observable.

        Parameters
        ----------
        observable : IObservable
            An object for adding this notifier to.

        Raises
        ------
        RuntimeError
            If the internal reference count is not zero and an equivalent
            notifier is not found in the observable.
        """
        notifiers = observable._notifiers(True)
        for other in notifiers:
            if self.equals(other):
                other._ref_count += 1
                break
        else:
            # It is not a current use case to share a notifier with multiple
            # observables. Using a single reference count will tie the lifetime
            # of the notifier to multiple objects.
            if self._ref_count != 0:
                raise RuntimeError(
                    "Sharing notifiers across observables is unexpected."
                )
            notifiers.append(self)
            self._ref_count += 1

    def remove_from(self, observable):
        """ Remove this notifier from an observable object.

        If an equivalent notifier exists, the existing notifier's reference
        count is decremented and the notifier is only removed if
        the count is reduced to zero.

        Parameters
        ----------
        observable : IObservable
            An object for removing this notifier from.

        Raises
        ------
        RuntimeError
            If the reference count becomes negative unexpectedly.
        NotifierNotFound
            If the notifier is not found.
        """
        notifiers = observable._notifiers(True)
        for other in notifiers[:]:
            if self.equals(other):
                if other._ref_count == 1:
                    notifiers.remove(other)
                other._ref_count -= 1
                if other._ref_count < 0:
                    raise RuntimeError(
                        "Reference count is negative. "
                        "Race condition?"
                    )
                break
        else:
            raise NotifierNotFound("Notifier not found.")

    def equals(self, other):
        """ Return true if the other notifier is equivalent to this one.

        Parameters
        ----------
        other : any

        Returns
        -------
        boolean
        """
        if other is self:
            return True
        if type(other) is not type(self):
            return False
        return (
            self.handler() == other.handler()
            and self.target() is other.target()
            and self.dispatcher == other.dispatcher
        )


def _return(value):
    return value
