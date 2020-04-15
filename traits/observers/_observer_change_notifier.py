# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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


class ObserverChangeNotifier:
    """ Wrapper for maintaining observers in an ObserverPath
    when an upstream object changes.

    For example, when observing an extended attribute path,
    e.g. ``foo.bar.baz``, on an instance of ``HasTraits``,
    if the container object changes, the observers and notifiers
    need to be removed from the old container and nested objects,
    and new observers and notifiers added to the new container and
    nested objects.

    """

    def __init__(
            self, *, observer_handler, event_factory,
            path, handler, target, dispatcher):
        """

        Parameters
        ----------
        observer_handler : callable(event, path, handler, target, dispatcher)
            The handler for maintaining observers and notifiers.
            ``event`` is the object created by the ``event_factory`` and is
            associated with the change event that triggers this notifier.
            The rest of the arguments are provided by the arguments to this
            notifier.
        event_factory : callable(*args, **kwargs) -> object
            A factory function for creating the event object to be sent to
            the handler. The call signature must be compatible with the
            call signature expected by the observable this notifier is used
            with. e.g. for CTrait, the call signature will be
            ``(object, name, old, new)``.
        path : ObserverPath
            An object describing what traits are being observed on an instance
            of ``HasTraits``, e.g. observe mutations on a list referenced by
            a specific named trait.
        handler : callable(event)
            The user handler being maintained when a container object changes.
            A weak reference is created for the handler if it is an instance
            method. If the instance method handler is garbage collected, this
            notifier will be silenced.
        target : object
            An object for defining the context of the user's handler notifier.
            A weak reference is created for the target. If the target is garbage
            collected, this notifier will be silenced.
        dispatcher : callable(function, event)
            Callable for dispatching the user's handler.
        """
        self.observer_handler = observer_handler
        self.event_factory = event_factory
        self.path = path
        self.target = weakref.ref(target)
        if isinstance(handler, types.MethodType):
            self.handler = weakref.WeakMethod(handler)
        else:
            self.handler = partial(_return, value=handler)
        self.dispatcher = dispatcher

    def add_to(self, observable):
        """ Add this notifier to the observable.

        Parameters
        ----------
        observable : IObservable
        """
        notifiers = observable._notifiers(True)
        notifiers.append(self)

    def remove_from(self, observable):
        """ Remove this notifier from the observable.

        Parameters
        ----------
        observable : IObservable
        """
        notifiers = observable._notifiers(True)
        notifiers.remove(self)

    def __call__(self, *args, **kwargs):
        """ Called by the observable this notifier is attached to.

        This exercises the observer_handler for maintaining observers and
        notifiers on changed objects.

        Note that any unexpected exceptions will be raised, as the
        ``observer_handler`` is not provided by users of traits, but is
        a callable maintained in traits.
        """
        target = self.target()
        if target is None:
            return

        handler = self.handler()
        if handler is None:
            return

        event = self.event_factory(*args, **kwargs)

        self.observer_handler(
            event=event,
            path=self.path,
            target=target,
            handler=handler,
            dispatcher=self.dispatcher,
        )

    def equals(self, other):
        """ Return true if the other value is a notifier equivalent to this one.

        Parameters
        ----------
        other : any

        Returns
        -------
        boolean
        """
        return (
            type(self) is type(other)
            # observer_handler contains the logic for maintaining notifiers
            # in the downstream path.
            and self.observer_handler is other.observer_handler
            # user handler is an input for observer_handler.
            # different user handlers should not interfere each other.
            and self.handler() is other.handler()
            # path is an input for observer_handler.
            # Unequal paths should not interfere each other.
            and self.path == other.path
            # target is an input for observer_handler.
            # it goes together with the user's handler
            and self.target() is other.target()
        )


def _return(value):
    return value
