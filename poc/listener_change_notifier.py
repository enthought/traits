import logging

from interfaces import INotifier


logger = logging.getLogger(__name__)


class ListenerChangeNotifier(INotifier):
    """ Notifier for when a trait has changed, removes
    'extended' listeners from the removed object, and propagates
    the 'extended' listeners to the new object.
    """

    def __init__(
            self, listener_callback, actual_callback, path,
            target, event_factory, dispatcher):
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
        logger.debug(
            "ListenerChangeNotifier is called for %s(%r)",
            type(event).__name__,
            (event.__dict__),
        )
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
        )
