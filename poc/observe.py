import itertools


class BaseListener:

    def __eq__(self, other):
        """ Return true if a given instance is equivalent to this
        one. Needed for comparing paths and cleaning up listeners.
        """
        raise NotImplementedError()

    @property
    def notify(self):
        """ Whether to call notifiers for changes on this item."""
        return getattr(self, "_notify", True)

    @notify.setter
    def notify(self, value):
        self._notify = value


class _FilteredTraitListener(BaseListener):

    def __init__(self, notify, filter):
        """
        Parameters
        ----------
        notify : boolean
            Whether to notify for changes.
        filter : callable(name, trait) -> boolean
            Callable that receives a named trait and returns
            a boolean as for whether the trait is being
            listened to.
            It is the developers' responsibility to ensure two
            equivalent ``filter`` compare equal.
            i.e. this class should not be exposed to the users.
        """
        self.filter = filter
        self.notify = notify

    def __eq__(self, other):
        if other is self:
            return True
        if type(other) is not type(self):
            return False
        return (
            (self.filter, self.notify)
            == (other.filter, other.notify)
        )


class NamedTraitListener(BaseListener):

    def __init__(
            self, name, notify, optional, comparison_mode=None):
        """
        Parameters
        ----------
        name : str
            Name of the trait to listen to.
        notify : boolean
            Whether to notify for changes.
        optional : boolean
            Whether the trait is optional. If false and the trait
            is not found, an exception will be raised.
        comparison_mode : ComparisonMode or None
            Whether to modify the default comparison behaviour.
        """
        self.name = name
        self.notify = notify
        self.optional = optional
        self.comparison_mode = comparison_mode

    def __eq__(self, other):
        if other is self:
            return True
        if type(other) is not type(self):
            return False
        return (
            (self.name, self.notify, self.optional, self.comparison_mode)
            == (other.name, other.notify, other.optional, other.comparison_mode)
        )


class ListItemListener(BaseListener):

    def __init__(self, notify):
        self.notify = notify

    def __eq__(self, other):
        return type(self) is type(other) and self.notify == other.notify


class DictValueListener(BaseListener):
    # TODO: Define this class taking into account
    # what is going to happen in TraitDictObject

    def __init__(self, notify):
        self.notify = notify


class ListenerPath:

    def __init__(self, node, nexts=()):
        self.node = node
        self.nexts = nexts

    def __eq__(self, other):
        """ Return true if a given ListenerPath is equivalent to this one.
        """

        # FIXME: The following is a draft.
        # We need to handle cycles!

        if other is self:
            return True
        if type(other) is not type(self):
            return False
        if self.node != other.node:
            return False
        if self.nexts == other.nexts:
            return True
        if len(self.nexts) != len(other.nexts):
            return False
        for nexts in itertools.permutations(other.nexts, len(other.nexts)):
            if all(n1 == n2 for n1, n2 in zip(self.nexts, nexts)):
                return True
        return False
