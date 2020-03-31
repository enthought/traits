import abc


class INotifiableObject(abc.ABC):
    """ A notifiable object is an object which has a list to/from which
    notifiers can be added / removed.
    """

    def _notifiers(self, force_create):
        """ Return a list for notifiers to be added or removed from.

        Parameters
        ----------
        force_create : boolean
            Kept for compatibility with ctraits. Maybe removed in
            the future. Other classes implementing this interface
            should not use this flag.
        """
        raise NotImplementedError()


class INotifier:
    """ A callable to be added to the list of notifiers returned
    by an INotifiableObject. Implements methods required for adding, removing
    and book-keeping notifiers inside such list.
    """

    def __call__(self, *args):
        """ Called by INotifiableObject. """
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
