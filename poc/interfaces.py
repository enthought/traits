import abc


class INotifiableObject(abc.ABC):

    @abc.abstractmethod
    def _notifiers(self, force_create):
        return []


class INotifier(abc.ABC):

    def __call__(self, object, name, old, new):
        raise NotImplementedError()

    def increment(self):
        raise NotImplementedError()

    def decrement(self):
        raise NotImplementedError()

    def can_be_removed(self):
        # return true or false.
        raise NotImplementedError()

    def dispose(self):
        # clean up tasks **after** this notifier is removed from
        # the notifiable object.
        raise NotImplementedError()

    def equals(self, other):
        # Return true or false
        raise NotImplementedError()
