from functools import partial
import itertools
import logging
import threading

from traits import ctraits
from traits.constants import ComparisonMode
from traits.trait_base import Undefined, Uninitialized
from traits.ctrait import CTrait
from traits.trait_dict_object import TraitDictObject
from traits.trait_set_object import TraitSetObject


from poc.interfaces import INotifiableObject
from poc.trait_observer_notifier import (
    ObserverEvent,
    ListObserverEvent,
    TraitObserverNotifier,
)
from poc.listener_change_notifier import ListenerChangeNotifier

# We need to identify objects which has this `_notifiers` methods
# We could do the easy-to-ask-forgiveness-than-permission way.
# Or we could do the leap-before-you-leap way.
# Here is the LBYL way
from traits.trait_list_object import TraitListObject
INotifiableObject.register(TraitListObject)
INotifiableObject.register(CTrait)
INotifiableObject.register(ctraits.CHasTraits)

logger = logging.getLogger()


def dispatch_same(callback, args=(), kwargs=None):
    if kwargs is None:
        kwargs = {}
    callback(*args, **kwargs)


def dispatch_new_thread(callback, args=(), kwargs=None):
    if kwargs is None:
        kwargs = {}
    threading.Thread(
        target=callback, args=args, kwargs=kwargs).start()


# These are user-facing notifier factories...
DISPATCHERS = {
    "extended": dispatch_same,
    "same": dispatch_same,
    "new": dispatch_new_thread,
}


def observe(object, callback, path, remove, dispatch):
    """
    Parameters
    ----------
    object : HasTrait
        An object that implements `_notifiers` for returning a list for
        adding or removing notifiers
    callback : callable(BaseObserverEvent)
        A callable conforming to the notifier signature.
    path : ListenerPath
        Path for listening to extended traits.
    remove : boolean
        Whether to remove the observer.
    dispatch : str
        A string indicating the thread on which notifications should be
        run.
    """
    if remove:
        remove_notifiers(
            path=path,
            object=object,
            callback=callback,
            target=object,
            dispatcher=DISPATCHERS[dispatch],
        )
    else:
        add_notifiers(
            path=path,
            object=object,
            callback=callback,
            target=object,
            dispatcher=DISPATCHERS[dispatch],
        )


def add_notifiers(object, callback, path, target, dispatcher):
    """ Add notifiers for a ListenerPath

    Parameters
    ----------
    object : HasTrait
        An object that implements `_notifiers` for returning a list for
        adding or removing notifiers
    callback : callable(object, name, old, new)
        A callable conforming to the notifier signature.
    path : ListenerPath
        Path for listening to extended traits.
    remove : boolean
        Whether to remove the observer.
    dispatcher : callable(callable, args, kwargs)
        Callable for dispatching the callback, i.e. dispatching
        callback on a different thread.
    """

    listener = path.node
    for this_target in listener.iter_this_targets(object):
        if listener.notify:
            # TODO: Move this to the listener interface?
            notifier = TraitObserverNotifier(
                observer=callback,
                owner=this_target._notifiers(True),
                target=target,
                event_factory=listener.event_factory,
                dispatcher=dispatcher,
            )
            add_notifier(object=this_target, notifier=notifier)

        for next_path in path.nexts:

            change_notifier = listener.get_change_notifier(
                callback=callback,
                path=next_path,
                target=target,
                dispatcher=dispatcher,
            )
            add_notifier(object=this_target, notifier=change_notifier)

            for next_target in listener.iter_next_targets(object):
                add_notifiers(
                    object=next_target,
                    callback=callback,
                    path=next_path,
                    target=target,
                    dispatcher=dispatcher,
                )
    if type(listener) is not TraitAddedListener:
        add_notifiers(
            object=object,
            callback=callback,
            path=ListenerPath(
                node=TraitAddedListener(),
                nexts=[path],
            ),
            target=target,
            dispatcher=dispatcher,
        )


def add_notifier(object, notifier):
    """ Add a notifier to an notifiable object.

    Parameters
    ----------
    object : INotifiableObject
    notifier : INotifier

    """
    observer_notifiers = object._notifiers(True)
    for other in observer_notifiers:
        # Rename ``observer`` (passive) to ``callback`` (active)!
        if other.equals(notifier):
            # should we compare dispatch as well?
            logger.debug("ADD: Incrementing notifier %r", other)
            other.increment()
            break

    else:
        logger.debug(
            "ADD: adding notifier %r for object %r",
            notifier, object
        )
        observer_notifiers.append(notifier)


def remove_notifier(object, notifier):
    """ Remove a notifier from an notifiable object.

    Parameters
    ----------
    object : INotifiableObject
    notifier : INotifier
    """

    observer_notifiers = object._notifiers(True)
    logger.debug("Removing from %r", observer_notifiers)
    for other in observer_notifiers[:]:
        if other.equals(notifier):
            other.decrement()
            if other.can_be_removed():
                # TODO: Always do this on the main thread!
                observer_notifiers.remove(other)
                other.dispose()
            break
    else:
        # We can't raise here to be defensive.
        # If a trait has an implicit default, when the trait is
        # assigned a new value, the event's old value is filled
        # with this implicit default, which does not have
        # any notifiers.
        pass


def remove_notifiers(object, callback, path, target, dispatcher):
    """ Remove notifiers for a ListenerPath

    Parameters
    ----------
    object : HasTrait
        An object that implements `_notifiers` for returning a list for
        adding or removing notifiers
    callback : callable(object, name, old, new)
        A callable conforming to the notifier signature.
    path : ListenerPath
        Path for listening to extended traits.
    remove : boolean
        Whether to remove the observer.
    dispatcher : callable(callable, args, kwargs)
        Callable for dispatching the callback, i.e. dispatching
        callback on a different thread.
    """
    listener = path.node
    for this_target in listener.iter_this_targets(object):
        if listener.notify:
            notifier = TraitObserverNotifier(
                observer=callback,
                owner=this_target._notifiers(True),
                target=target,
                event_factory=listener.event_factory,
                dispatcher=dispatcher,
            )
            remove_notifier(this_target, notifier)

        for next_path in path.nexts:

            change_notifier = listener.get_change_notifier(
                callback=callback,
                path=next_path,
                target=target,
                dispatcher=dispatcher,
            )
            remove_notifier(object=this_target, notifier=change_notifier)

            for next_target in listener.iter_next_targets(object):
                remove_notifiers(
                    object=next_target,
                    callback=callback,
                    path=next_path,
                    target=target,
                    dispatcher=dispatcher,
                )


def is_notifiable(object):
    """ Return true if an object conforms to the expected
    interface for a notifiable object.
    """
    return isinstance(object, INotifiableObject)


class BaseListener:

    def event_factory(self, object, name, old, new):
        raise NotImplementedError()

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

    def iter_this_targets(self, object):
        """ Yield (notifiable) objects for attaching notifiers for this
        listener.
        """
        yield from ()

    def iter_next_targets(self, object):
        """ Yield (notifiable) objects for attaching notifiers for the
        next listener following this one in a ListenerPath.
        """
        # For walking down the path of Listeners
        yield from ()

    def get_change_notifier(self, callback, path, target, dispatcher):
        """ Return a ListenerChangeNotifier for removing/propagating listeners
        for the 'next' targets.
        """
        raise NotImplementedError()


class AnyTraitListener(BaseListener):

    def iter_this_targets(self, object):
        yield object

    def iter_next_targets(self, object):
        for name in object.trait_names():
            value = object.__dict__.get(name, Undefined)
            if is_notifiable(value):
                yield value


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

    def event_factory(self, object, name, old, new):
        return ObserverEvent(object, name, old, new)

    def __eq__(self, other):
        if other is self:
            return True
        if type(other) is not type(self):
            return False
        return (
            (self.filter, self.notify)
            == (other.filter, other.notify)
        )

    def iter_this_targets(self, object):
        # object must be an instance of HasTraits
        for name, trait in object.traits().items():
            if self.filter(name, trait):
                yield object._trait(name, 2)

    def iter_next_targets(self, object):
        for name, trait in object.traits().items():
            if self.filter(name, trait):
                value = object.__dict__.get(name, Undefined)
                if is_notifiable(value):
                    yield value

    def get_change_notifier(self, callback, path, target, dispatcher):
        return ListenerChangeNotifier(
            listener_callback=self.change_callback,
            actual_callback=callback,
            path=path,
            target=target,
            event_factory=self.event_factory,
            dispatcher=dispatcher,
        )

    @staticmethod
    def change_callback(event, callback, path, target, dispatcher):
        if event.old is not Uninitialized and event.old is not Undefined:
            remove_notifiers(
                object=event.old,
                callback=callback,
                path=path,
                target=target,
                dispatcher=dispatcher,
            )
        add_notifiers(
            object=event.new,
            callback=callback,
            path=path,
            target=target,
            dispatcher=dispatcher,
        )


class _MetadataFilter:
    """ Callable as a filter in `FilteredTraitListener` for
    listening to traits with/without a given metadata.
    """

    def __init__(self, metadata_name, include):
        """
        metadata_name : str
            Name of metadata.
        incude : boolean
            If true, listen to the trait that **have** the metadata.
            If false, listen to the trait that **do not have** the
            metadata.
        """
        self.metadata_name = metadata_name
        self.include = include

    def __call__(self, name, trait):
        return getattr(trait, self.metadata_name, False) is self.include

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) is not type(self):
            return False
        return (
            (self.metadata_name, self.include)
            == (other.metadata_name, other.include)
        )


def MetadataTraitListener(metadata_name, notify, include):
    """
    notify : boolean
        Whether to notify for changes.
    metadata_name : str
        Name of metadata.
    incude : boolean
        If true, listen to the trait that **have** the metadata.
        If false, listen to the trait that **do not have** the
        metadata.
    """
    return _FilteredTraitListener(
        notify=notify,
        filter=_MetadataFilter(metadata_name=metadata_name, include=include)
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

    def event_factory(self, object, name, old, new):
        if (self.comparison_mode is ComparisonMode.equality
                and old == new):
            return None

        return ObserverEvent(object, name, old, new)

    def __eq__(self, other):
        if other is self:
            return True
        if type(other) is not type(self):
            return False
        return (
            (self.name, self.notify, self.optional, self.comparison_mode)
            == (other.name, other.notify, other.optional, other.comparison_mode)
        )

    def iter_this_targets(self, object):
        # object must be an instance of HasTraits
        trait = object.trait(name=self.name)
        if trait is None and not self.optional:
            raise ValueError(
                "Trait name {!r} is not defined".format(self.name))
        # this has side effect of creating instance trait...
        yield object._trait(self.name, 2)

    def iter_next_targets(self, object):
        value = object.__dict__.get(self.name, Undefined)
        if is_notifiable(value):
            yield value

    def get_change_notifier(self, callback, path, target, dispatcher):
        return ListenerChangeNotifier(
            listener_callback=self.change_callback,
            actual_callback=callback,
            path=path,
            target=target,
            event_factory=ObserverEvent,
            dispatcher=dispatcher,
        )

    @staticmethod
    def change_callback(event, callback, path, target, dispatcher):
        if event.old is not Uninitialized and event.old is not Undefined:
            remove_notifiers(
                object=event.old,
                callback=callback,
                path=path,
                target=target,
                dispatcher=dispatcher,
            )
        add_notifiers(
            object=event.new,
            callback=callback,
            path=path,
            target=target,
            dispatcher=dispatcher,
        )


OptionalTraitListener = partial(NamedTraitListener, optional=True)

RequiredTraitListener = partial(NamedTraitListener, optional=False)


class TraitAddedListener(BaseListener):
    """ Listener for handling trait_added event.
    """

    def __init__(self):
        self.notify = False

    def __eq__(self, other):
        return type(self) is type(other)

    def iter_this_targets(self, object):
        try:
            yield object._trait("trait_added", 2)
        except AttributeError:
            pass

    def iter_next_targets(self, object):
        yield from ()

    def get_change_notifier(self, callback, path, target, dispatcher):
        return ListenerChangeNotifier(
            listener_callback=self.change_callback,
            actual_callback=callback,
            path=path,
            target=target,
            event_factory=ObserverEvent,
            dispatcher=dispatcher,
        )

    @staticmethod
    def change_callback(event, callback, path, target, dispatcher):
        # The event comes from trait_added
        listener = path.node
        add_notifiers(
            object=event.object,
            callback=callback,
            path=ListenerPath(
                node=RequiredTraitListener(
                    name=event.new, notify=listener.notify),
                nexts=path.nexts
            ),
            target=target,
            dispatcher=dispatcher,
        )


class ListItemListener(BaseListener):

    def __init__(self, notify):
        self.notify = notify

    def __eq__(self, other):
        return type(self) is type(other) and self.notify == other.notify

    def event_factory(self, object, name, old, new):
        return ListObserverEvent(object, name, old, new)

    def iter_this_targets(self, object):
        # object should be a TraitListObject
        yield object

    def iter_next_targets(self, object):
        for item in object:
            if is_notifiable(item):
                yield item

    def get_change_notifier(self, callback, path, target, dispatcher):
        return ListenerChangeNotifier(
            listener_callback=self.change_callback,
            actual_callback=callback,
            path=path,
            target=target,
            event_factory=self.event_factory,
            dispatcher=dispatcher,
        )

    @staticmethod
    def change_callback(event, callback, path, target, dispatcher):
        logger.debug(
            "Handling list change. "
            "({!r})".format(
                (event.old, event.new, event.removed, event.added, path.node))
        )
        for item in event.removed:
            if is_notifiable(item):
                remove_notifiers(
                    object=item,
                    callback=callback,
                    path=path,
                    target=target,
                    dispatcher=dispatcher,
                )
        for item in event.added:
            if is_notifiable(item):
                add_notifiers(
                    object=item,
                    callback=callback,
                    path=path,
                    target=target,
                    dispatcher=dispatcher,
                )


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

    @classmethod
    def from_nodes(cls, node, *nodes):
        """ Convenient factory function for creating a ListenerPath
        with no branches.
        """
        nodes = iter(nodes)
        root = path = cls(node=node)
        for node in nodes:
            next_path = cls(node=node)
            path.nexts = [next_path]
            path = next_path
        return root


# "inst.attr"
# fire if inst is changed, or inst.attr is changed
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=True),
    nexts=[
        ListenerPath(
            node=RequiredTraitListener(name="attr", notify=True),
            nexts=(),
        )
    ],
)

# "inst:attr"
# fire if inst.attr is changed
# do not fire if inst is changed (even if it is changed such that
# inst.attr is changed)
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=False),
    nexts=[
        ListenerPath(
            node=RequiredTraitListener(name="attr", notify=True),
            nexts=(),
        )
    ],
)

# "[inst1, inst2].attr"
# This is equivalent to having two paths
paths = [
    ListenerPath.from_nodes(
        RequiredTraitListener(name="inst1", notify=True),
        RequiredTraitListener(name="attr", notify=True),
    ),
    ListenerPath.from_nodes(
        RequiredTraitListener(name="inst2", notify=True),
        RequiredTraitListener(name="attr", notify=True),
    ),
]

# "inst.container"
path = ListenerPath.from_nodes(
    RequiredTraitListener(name="inst", notify=True),
    RequiredTraitListener(name="constainer", notify=True),
)


# "inst.container_items"
path = ListenerPath.from_nodes(
    RequiredTraitListener(name="inst", notify=True),
    RequiredTraitListener(name="constainer", notify=False),
    ListItemListener(notify=True),
)

# "inst.[inst1, inst2].attr"
# option 1: Two separate paths
paths = [
    ListenerPath.from_nodes(
        RequiredTraitListener(name="inst", notify=True),
        RequiredTraitListener(name="inst1", notify=True),
        RequiredTraitListener(name="attr", notify=True),
    ),
    ListenerPath.from_nodes(
        RequiredTraitListener(name="inst", notify=True),
        RequiredTraitListener(name="inst2", notify=True),
        RequiredTraitListener(name="attr", notify=True),
    ),
]

# option 2: Two items in `nexts`
inst_node = RequiredTraitListener(name="inst", notify=True)
inst1_node = RequiredTraitListener(name="inst1", notify=True)
inst2_node = RequiredTraitListener(name="inst2", notify=True)
attr_node = RequiredTraitListener(name="attr", notify=True)
path = ListenerPath(
    node=inst_node,
    nexts=[
        ListenerPath(
            node=inst1_node,
            nexts=[ListenerPath(node=attr_node)],
        ),
        ListenerPath(
            node=inst2_node,
            nexts=[ListenerPath(node=attr_node)],
        ),
    ]
)

# "inst.attr?"
path = ListenerPath.from_nodes(
    RequiredTraitListener(name="inst", notify=True),
    OptionalTraitListener(name="attr", notify=True),
)

# "inst.attr*"
# this should match inst.attr.attr.attr.attr....
attr = RequiredTraitListener(name="attr", notify=True)
path = ListenerPath(node=OptionalTraitListener(name="inst", notify=True))
path.next = path


# "inst.attr*.value"
# Example matches:
#    inst.attr.value
#    inst.attr.attr.value
#    inst.attr.attr.attr.value
value_path = ListenerPath(
    node=RequiredTraitListener(name="value", notify=True))
attr_path = ListenerPath(
    node=RequiredTraitListener(name="attr", notify=True))
attr_path.nexts = [
    attr_path,
    value_path,
]
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=True),
    nexts=[attr_path],
)

# "inst1?.inst2?.attr"
path = ListenerPath.from_nodes(
    OptionalTraitListener(name="inst1", notify=True),
    OptionalTraitListener(name="inst1", notify=True),
    RequiredTraitListener(name="attr", notify=True),
)

# Listen to changes to the items in the values of Dict(Str(), List())
path = ListenerPath.from_nodes(
    RequiredTraitListener(name="mapping", notify=True),
    DictValueListener(notify=True),
    ListItemListener(notify=True),
)

# Listen to all traits with a metadata 'updated'
path = ListenerPath(
    node=_FilteredTraitListener(
        filter=lambda _, trait: "updated" in trait.__dict__,
        notify=True,
    ),
    nexts=(),
)


# Listen to any traits, then any traits of each of these traits...
path = ListenerPath(
    node=AnyTraitListener(),
    nexts=(),
)
path.nexts = [path]