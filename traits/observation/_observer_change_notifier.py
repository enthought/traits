# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import types
import weakref

from traits.observation._exceptions import NotifierNotFound


class ObserverChangeNotifier:
    """ Wrapper for maintaining notifiers in an ObserverGraph
    when an upstream object changes.

    An instance of ``ObserverChangeNotifier`` is a callable to be contributed
    to an instance of ``IObserverable``, e.g. ``CTrait``, ``TraitList`` etc.,
    such that it will be called when an observerable emits notificaitons for
    changes.

    For example, suppose changes are observed on an extended attribute path,
    e.g. ``foo.bar.baz``, where ``foo`` and ``bar`` are both instances of
    ``HasTraits``.  There will be an instance of ``ObserverChangeNotifier`` on
    the ``CTrait`` for ``foo``. When ``foo`` changes, the notifier will be
    called for maintaining the observers for ``bar.baz``. Similarly, there
    will be an instance of ``ObserverChangeNotifier`` on the ``CTrait`` for
    ``bar`` for maintaining the observers for ``baz``, when ``bar`` changes.

    """

    def __init__(
            self, *, observer_handler, event_factory, prevent_event,
            graph, handler, target, dispatcher):
        """

        Parameters
        ----------
        observer_handler : callable(event, graph, handler, target, dispatcher)
            The handler for maintaining observers and notifiers.
            ``event`` is the object created by the ``event_factory`` and is
            associated with the change event that triggers this notifier.
            The rest of the arguments are provided by the arguments to this
            notifier.
        event_factory : callable(*args, **kwargs) -> object
            A factory function for creating the event object to be sent to
            the observer_handler. The call signature must be compatible with
            the call signature expected by the observable this notifier is
            used with. e.g. for CTrait, the call signature will be
            ``(object, name, old, new)``.
        prevent_event : callable(event) -> boolean
            A callable for controlling whether the observer_handler should be
            invoked. It receives the event created by the event factory and
            returns true if the event should be prevented, false if the event
            should be fired.
        graph : ObserverGraph
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
            A weak reference is created for the target. If the target is
            garbage collected, this notifier will be silenced.
            This is typically an instance of HasTraits acting as a container
            for an observable on which this notifier is attached to. It would
            be seen by the user as the "owner" of the observer.
        dispatcher : callable(function, event)
            Callable for dispatching the user's handler.
        """
        self.observer_handler = observer_handler
        self.event_factory = event_factory
        self.prevent_event = prevent_event
        self.graph = graph
        self.target = weakref.ref(target)
        if isinstance(handler, types.MethodType):
            self.handler = weakref.WeakMethod(handler)
        else:

            def _return_handler():
                return handler

            self.handler = _return_handler

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
        """ Remove a notifier equivalent to this one from the observable.

        Parameters
        ----------
        observable : IObservable

        Raises
        ------
        NotifierNotFound
            If the notifier cannot be found.
        """
        notifiers = observable._notifiers(True)
        for notifier in notifiers[:]:
            if self.equals(notifier):
                notifiers.remove(notifier)
                break
        else:
            raise NotifierNotFound("Notifier not found.")

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
        if self.prevent_event(event):
            return

        self.observer_handler(
            event=event,
            graph=self.graph,
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
            # in the downstream graph.
            and self.observer_handler is other.observer_handler
            # graph is an input for observer_handler.
            # Unequal graphs should not interfere each other.
            and self.graph == other.graph
            # user handler is an input for observer_handler.
            # different user handlers should not interfere each other.
            and self.handler() == other.handler()
            # target is an input for observer_handler.
            # it goes together with the user's handler
            and self.target() is other.target()
            # dispatcher is an input for observer_handler.
            # different dispatchers should not interfere each other.
            and self.dispatcher == other.dispatcher
        )
