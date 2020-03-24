import abc


class INotifiableObject(abc.ABC):
    """ A notifiable object is an object which has a list to/from which
    notifiers can be added / removed.
    """

    @abc.abstractmethod
    def _notifiers(self, force_create):
        return []


class INotifier(abc.ABC):
    """ Interface for a notifier.
    """

    def __call__(self, object, name, old, new):
        """ Called by ctraits. """
        raise NotImplementedError()

    def increment(self):
        """ Increment an internal reference count.
        Subclass can ignore if reference counting is not required.
        """
        raise NotImplementedError()

    def decrement(self):
        """ Decrement an internal reference count.
        Subclass can ignore if reference counting is not required.
        """
        raise NotImplementedError()

    def can_be_removed(self):
        """ Return true if this notifier can be removed from a
        notifiable object.
        """
        # return true or false.
        raise NotImplementedError()

    def dispose(self):
        """ Clean up tasks **after** this notifier is removed from
        the notifiable object.
        """
        raise NotImplementedError()

    def equals(self, other):
        """ Return true if this notifier is considered equivalent to
        a given notifier.
        """
        raise NotImplementedError()
