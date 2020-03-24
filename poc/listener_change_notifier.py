import logging

from interfaces import INotifier


logger = logging.getLogger(__name__)


class ListenerChangeNotifier(INotifier):
    """ Notifier for maintaining nested listeners when a trait has
    changed.

    For example, when ``foo.bar.baz`` is being listened to and
    ``foo`` is changed, this notifier is fired such that listeners
    attached to the old ``foo`` 's nested attributes are removed,
    and new listeners are attached to the new ``foo``.
    """

    def __init__(
            self, listener_callback, actual_callback, path,
            target, event_factory, dispatcher):
        """
        Parameters
        ----------
        listener_callback : callable
            Input arguments are (event, callback, path, target, dispatcher).
            ``event`` represents the change event that should result in
            hooking/unhooking of listeners.
            ``callback`` is the same as ``actual_callback`` (see below).
            ``path``, ``target``, ``dispatcher`` are passed directly from
            the values given to this initializer.
        actual_callback : callable(BaseEvent)
            The actual callable the listeners are created for.
            i.e. it is the callback provided by the user via ``observe``.
        path : ListenerPath
            Path that defines what listeners to hook/unhook.
        target : Any
            Sets the context for the (actual) callback. In practice, it is
            the HasTrait instance on which the listener path is defined and
            will be seen by users as the "owner" of the notifier.
            Strictly speaking, this object sets the context for the notifier
            and does not have to be a notifiable object.
        event_factory : callable
            Factory function for creating the event to be passed to
            ``listener_callback``.
        dispatcher : callable(args, kwargs)
            Callable for dispatching the ``actual_callback``.
        """
        self.listener_callback = listener_callback

        #: TODO: Does this need to be a weak ref?
        self.actual_callback = actual_callback

        #: TODO: Does this need to be a weak ref?
        self.target = target

        self.dispatcher = dispatcher
        self.path = path
        self.event_factory = event_factory

    def __call__(self, object, name, old, new):
        event = self.event_factory(object, name, old, new)
        #: TODO: Should we use the same dispatcher?
        self.listener_callback(
            event=event,
            callback=self.actual_callback,
            path=self.path,
            target=self.target,
            dispatcher=self.dispatcher,
        )

    def increment(self):
        pass

    def decrement(self):
        pass

    def can_be_removed(self):
        # return true or false.
        return True

    def dispose(self):
        # clean up tasks **after** this notifier is removed from
        # the notifiable object.
        pass

    def equals(self, other):
        # Return true or false
        if type(other) is not type(self):
            return False
        return (
            self.listener_callback is other.listener_callback
            and self.actual_callback is other.actual_callback
            and self.path == other.path
        )
