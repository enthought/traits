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
            method. ``observer_handler`` may receive ``None`` if the handler
            has been garbage collected.
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
            self.handler = weakref.ref(handler)
        else:
            self.handler = partial(_return, value=handler)
        self.dispatcher = dispatcher

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

        event = self.event_factory(*args, **kwargs)

        # observer_handler will be given a chance to remove
        # notifiers on an observable when the notifier's target or the
        # handler is garbage collected. Hence no checks are performed
        # on the weak references here.
        self.observer_handler(
            event=event,
            path=self.path,
            target=self.target(),
            handler=self.handler(),
            dispatcher=self.dispatcher,
        )


def _return(value):
    return value
