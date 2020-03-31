import abc


class INotifiableObject(abc.ABC):
    """ A notifiable object is an object which has a list to/from which
    INotifier can be added / removed.
    """

    def _notifiers(self, force_create):
        """ Return a list of INotifier to be added or removed from.

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
        """ Called by INotifiableObject.
        Subclass should specify the exact call signature expected
        by the INotifiableObject.
        """
        raise NotImplementedError()

    def add_to(self, object):
        """ Add this notifier to an INotifiableObject
        """
        raise NotImplementedError()

    def remove_from(self, object):
        """ Remove this notifier from an INotifiableObject
        """
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


class ICTraitNotifier(INotifier):

    def __call__(self, object, name, old, new):
        raise NotImplementedError()


class IListNotifier(INotifier):

    def __call__(self, trait_list, trait_list_event):
        raise NotImplementedError()
