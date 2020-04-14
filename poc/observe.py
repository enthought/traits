

class BaseListener:

    def __eq__(self, other):
        """ Return true if a given instance is equivalent to this
        one. Needed for comparing paths and cleaning up listeners.
        """
        raise NotImplementedError()

    @property
    def notify(self):
        """ Whether to call notifiers for changes on this item."""
        return self._notify

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

    def __repr__(self):
        return "<Filter notify={!r} filter={!r}>".format(
            self.notify, self.filter,
        )

    def __hash__(self):
        return hash((type(self), self.notify, self.filter))

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

    def __repr__(self):
        return "<Name(name={!r}, notify={!r}, ...)>".format(
            self.name, self.notify,
        )

    def __hash__(self):
        return hash((
            type(self),
            self.name,
            self.notify,
            self.optional,
            self.comparison_mode,
        ))

    def __eq__(self, other):
        if other is self:
            return True
        if type(other) is not type(self):
            return False
        return (
            (self.name, self.notify, self.optional, self.comparison_mode)
            == (other.name, other.notify, other.optional,
                other.comparison_mode)
        )


class ListItemListener(BaseListener):

    def __init__(self, notify, optional):
        self.notify = notify
        self.optional = optional

    def __repr__(self):
        return "<List notify={!r} optional={!r}>".format(
            self.notify, self.optional,
        )

    def __hash__(self):
        return hash((type(self), self.notify, self.optional))

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.notify == other.notify
            and self.optional == other.optional
        )


class DictItemListener(BaseListener):

    def __init__(self, notify, optional):
        self.notify = notify
        self.optional = optional

    def __repr__(self):
        return "<Dict notify={!r} optional={!r}>".format(
            self.notify, self.optional,
        )

    def __hash__(self):
        return hash((type(self), self.notify, self.optional))

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.notify == other.notify
            and self.optional == other.optional
        )


class SetItemListener(BaseListener):

    def __init__(self, notify, optional):
        self.notify = notify
        self.optional = optional

    def __repr__(self):
        return "<Set notify={!r} optional={!r}>".format(
            self.notify, self.optional,
        )

    def __hash__(self):
        return hash((type(self), self.notify, self.optional))

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.notify == other.notify
            and self.optional == other.optional
        )


class DictValueListener(BaseListener):
    # TODO: Define this class taking into account
    # what is going to happen in TraitDictObject

    def __init__(self, notify):
        self.notify = notify


class ListenerPath:
    """ Data structure for representing the path(s) to observe
    traits.

    For equality check, handling of cycles relies on the creator
    of these ListenerPath to have maintained the cycles separately.
    Only nodes are used when cycles are compared for equality.
    """

    def __init__(self, node, branches=(), cycles=()):
        """

        Parameters
        ----------
        node : BaseListener
            The current node.
        branches : iterable of ListenerPath
            Paths as branches.
        cycles : iterable of ListenerPath
            Paths as cycles. They are assumed to have been referenced
            elsewhere inside a larger ListenerPath that includes this
            path.
        """
        self.node = node
        self.branches = set(branches)
        self.cycles = set(cycles)

    @property
    def nexts(self):
        """ Next set of ListenerPath.
        """
        return self.branches | self.cycles

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.node = None
        self.branches = set()
        self.cycles = set()
        return self

    def __repr__(self):
        return "<ListenerPath node={!r}, {} branches, {} cycles>".format(
            self.node, len(self.branches), len(self.cycles)
        )

    def __hash__(self):
        return hash(
            (
                type(self),
                self.node,
                frozenset(p.node for p in self.cycles),
                frozenset(self.branches),
            )
        )

    def __eq__(self, other):
        """ Return true if a given ListenerPath is equivalent to this one.
        """
        if other is self:
            return True
        if type(other) is not type(self):
            return False

        self_loop_nodes = set(p.node for p in self.cycles)
        other_loop_nodes = set(p.node for p in other.cycles)
        return(
            self.node == other.node
            # Rehash as the branches may have been modified afterwards
            and set(iter(self.branches)) == set(iter(other.branches))
            and self_loop_nodes == other_loop_nodes
        )

    def info(self, indent=0):
        """ Return a list of user-friendly texts containing descriptive information
        about this path.

        Returns
        -------
        lines : list of str
        """
        infos = []
        infos.append(" " * indent + "Node: {!r}".format(self.node))
        for path in self.branches:
            infos.extend(path.info(indent=indent + 4))

        for path in self.cycles:
            infos.append(" " * (indent + 4) + "Loop to {!r}".format(path.node))
        return infos
