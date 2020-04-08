# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import logging
import weakref

_trait_logger = logging.getLogger("traits")

# This flag indicates no targets are being tracked.
# This differentiates from None value, which indicates a target
# was tracked but it has been deleted.
_NOT_TRACKED = "no target tracked"


class TraitEventNotifier:
    """ Wrapper for invoking user's handler for a trait change
    event.

    The user's handler will receive an event object created by the
    event factory provided to this wrapper.

    An instance of TraitEventNotifier is a callable to be given to
    an object that will emit change notifications. The signature
    of the event factory must be compatible with the notification call
    signature defined by the object.
    """

    def __init__(
            self, *, handler, target,
            event_factory, prevent_event, dispatcher):
        """
        Parameters
        ----------
        handler : callable(event)
            The user's handler to receive the change event.
            The event object type and attributes depend on the
            type of change event, e.g. a list mutation event versus
            a HasTraits trait change event.
            For comparing two notifiers, the handlers are compared using
            equality.
        target : any
            An object for defining the context of the notifier.
            This is also used for distinguishing one notifier from
            another notifier wrapping the same handler. Targets are
            compared using identity.
            If this target is not None, a weak reference is created for
            the target. If the target is garbage collected, the notifier
            will be muted. This target is typically an instahce of
            ``HasTraits`` and will be seen by the user as the "owner" of
            the change handler.
        event_factory : callable(*args, **kwargs) -> object
            A factory function for creating the event object to be sent to
            the user. the call signature must be compatible with the
            call signature defined by the object from which change
            notifications are emitted. e.g. for CTrait, the call signature
            will be ``(object, name, old, new)``.
        prevent_event : callable(event) -> boolean
            A callable for controlling whether the user handler should be
            invoked. It receives the event created by the event factory and
            returns true if the event should be prevented, false if the event
            should be fired.
        dispatcher : callable(handler, event)
            A callable for dispatching the handler, e.g. on a different
            thread or on a GUI event loop. ``event`` is the object
            created by the event factory.
        """
        if target is not None:
            # This is such that the notifier does not prevent
            # the target from being garbage collected.
            self.target = weakref.ref(target)
        else:
            self.target = _return_not_tracked
        self.handler = handler
        self.dispatcher = dispatcher
        self.event_factory = event_factory
        # Reference count to avoid adding multiple notifiers
        # which are equivalent to the same observable.
        self._ref_count = 0

    def __call__(self, *args, **kwargs):
        if self.target() is None:
            # target is deleted. The notifier is disabled.
            return

        event = self.event_factory(*args, **kwargs)
        try:
            self.dispatcher(self.handler, event=event)
        except Exception:
            _trait_logger.exception(
                "Exception occurred in traits notification handler "
                "for event object: %r",
                event,
            )

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
        """
        notifiers = observable._notifiers(True)
        for other in notifiers:
            if self.equals(other):
                other._ref_count += 1
                break
        else:
            notifiers.append(self)
            self._ref_count += 1

    def equals(self, other):
        """ Return true if the other notifier is equivalent to this one.

        Parameters
        ----------
        other : any
        """
        if other is self:
            return True
        if type(other) is not type(self):
            return False
        self_target = self.target()
        other_target = other.target()
        return self.handler == other.handler and self_target is other_target


def _return_not_tracked():
    return _NOT_TRACKED
