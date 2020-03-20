from functools import partial
import logging

from traits import ctraits
from traits.trait_base import Undefined, Uninitialized
from traits.ctrait import CTrait
from traits.trait_dict_object import TraitDictObject
from traits.trait_set_object import TraitSetObject


from interfaces import INotifiableObject
from trait_observer_notifier import (
    ObserverEvent,
    ListObserverEvent,
    TraitObserverNotifier,
)
from trait_list_object import NewTraitListObject


# Mega hack for POC: Register the TraitListObject again to the global points...
ctraits._list_classes(NewTraitListObject, TraitSetObject, TraitDictObject)


# We need to identify objects which has this `_notifiers` methods
# We could do the easy-to-ask-forgiveness-than-permission way.
# Or we could do the leap-before-you-leap way.
# Here is the LBYL way

INotifiableObject.register(CTrait)
INotifiableObject.register(ctraits.CHasTraits)

logger = logging.getLogger()


def observe(object, callback, path, remove, dispatch):
    """
    Parameters
    ----------
    object : HasTrait or CTrait
        An object that implements `_notifiers` for returning a list for
        adding or removing notifiers
    callback : callable(object, name, old, new)
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
        )
    else:
        add_notifiers(
            path=path,
            object=object,
            callback=callback,
            dispatch=dispatch,
            target=object,
        )


WRAPPERS = {
    # These are placeholders.
    # The values are supposed to be different.
    "extended": TraitObserverNotifier,
    "same": TraitObserverNotifier,
    "ui": TraitObserverNotifier,
}


def add_notifiers(object, callback, dispatch, path, target):
    listener = path.node
    for this_target in listener.iter_this_targets(object):
        if listener.notify:
            add_notifier(
                this_target, callback, dispatch, listener.event_factory, target=target
            )

        for next_path in path.nexts:

            # FIXME: Can we not use partial
            # This holds a strong reference to the callback, is it okay?
            next_callback = partial(
                listener.change_callback, callback=callback, dispatch=dispatch,
                path=next_path, target=target)
            add_notifier(this_target, next_callback, dispatch, listener.event_factory, target=target)

            for next_target in listener.iter_next_targets(object):
                add_notifiers(next_target, callback, dispatch, next_path, target=target)


def add_notifier(object, callback, dispatch, event_factory, target):
    observer_notifiers = object._notifiers(True)
    for other in observer_notifiers:
        if other.observer is callback and other.target is target:
            # should we compare dispatch as well?
            logger.debug("ADD: adding target %r", target)
            other.increment_target_count(target)
            break

    else:
        logger.debug("ADD: adding notifier for object %r targeting %r", object, target)
        new_notifier = WRAPPERS[dispatch](
            observer=callback,
            owner=observer_notifiers,
            target=target,
            event_factory=event_factory,
        )
        observer_notifiers.append(new_notifier)


def remove_notifier(object, callback, target):
    if object is Undefined:
        return
    observer_notifiers = object._notifiers(True)
    logger.debug("Removing from %r", observer_notifiers)
    for other in observer_notifiers[:]:
        observer = other.observer
        logger.debug("%r, %r", observer, callback)
        if isinstance(observer, partial) and isinstance(callback, partial):  # FIXME: Code smell!
            same_callback = (
                observer.func is callback.func
                and observer.keywords["callback"] is callback.keywords["callback"]
            )
            logger.debug("other func: %r", observer.func)
            logger.debug("this func: %r", callback.func)
            logger.debug("other callback: %r", observer.keywords["callback"])
            logger.debug("this callback: %r", callback.keywords["callback"])
        else:
            same_callback = observer is callback

        if same_callback and other.target is target:
            other.decrement_target_count(target)
            if other.target_count == 0:
                observer_notifiers.remove(other)
                other.dispose()
            break


def remove_notifiers(object, callback, path, target):
    listener = path.node
    for this_target in listener.iter_this_targets(object):
        if listener.notify:
            remove_notifier(this_target, callback, target=target)

        for next_path in path.nexts:
            remove_notifier(this_target, partial(listener.change_callback, callback=callback), target=target)
            for next_target in listener.iter_next_targets(object):
                remove_notifiers(next_target, callback, next_path, target=target)


def is_notifiable(object):
    return isinstance(object, INotifiableObject)


class BaseListener:

    event_factory = ObserverEvent

    @property
    def notify(self):
        """ Whether to call notifiers for changes on this item."""
        return getattr(self, "_notify", True)

    @notify.setter
    def notify(self, value):
        self._notify = value

    def iter_this_targets(self, object):
        yield from ()

    def iter_next_targets(self, object):
        # For walking down the path of Listeners
        yield from ()

    def change_callback(self, event, callback, dispatch, path, target):
        """ Handle the removal/addition of notifiers a target changes.

        Parameters
        ----------
        event : event_factory
            An instance created by the event_factory of this listener.
        ...
        """
        raise NotImplementedError()

    def iter_new_events(self, object):
        # Yield an event for when a new target emerges.
        yield from ()


class AnyTraitListener(BaseListener):

    def iter_this_targets(self, object):
        yield object

    def iter_next_targets(self, object):
        for name in object.trait_names():
            value = object.__dict__.get(name, Undefined)
            if is_notifiable(value):
                yield value


class FilteredTraitListener(BaseListener):

    def __init__(self, notify, filter):
        self.filter = filter
        self.notify = notify

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

    def change_callback(self, event, callback, dispatch, path, target):
        if event.old is not Uninitialized and event.old is not Undefined:
            remove_notifiers(
                object=event.old,
                callback=callback,
                path=path,
                target=target,
            )
        add_notifiers(
            object=event.new,
            callback=callback,
            dispatch=dispatch,
            path=path,
            target=target,
        )


class NamedTraitListener(BaseListener):

    def __init__(self, name, notify, optional):
        self.name = name
        self.notify = notify
        self.optional = optional

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

    def change_callback(self, event, callback, dispatch, path, target):
        if event.old is not Uninitialized and event.old is not Undefined:
            remove_notifiers(
                object=event.old,
                callback=callback,
                path=path,
                target=target,
            )
        add_notifiers(
            object=event.new,
            callback=callback,
            dispatch=dispatch,
            path=path,
            target=target,
        )

    def iter_new_events(self, object):
        if self.name in object.__dict__:
            yield self.event_factory(
                object=object,
                name=self.name,
                old=Undefined,
                new=getattr(object, self.name),
            )


OptionalTraitListener = partial(NamedTraitListener, optional=True)

RequiredTraitListener = partial(NamedTraitListener, optional=False)


class ListItemListener(BaseListener):

    event_factory = ListObserverEvent

    def __init__(self, notify):
        self.notify = notify

    def iter_this_targets(self, object):
        # object should be a TraitListObject
        yield object

    def iter_next_targets(self, object):
        for item in object:
            if is_notifiable(item):
                yield item

    def change_callback(self, event, callback, dispatch, path, target):
        logger.debug(
            "Handling list change. "
            "({!r})".format(
                (event.old, event.new, event.removed, event.added, path.node)
        ))
        for item in event.removed:
            if is_notifiable(item):
                remove_notifiers(
                    object=item,
                    callback=callback,
                    path=path,
                    target=target,
                )
        for item in event.added:
            if is_notifiable(item):
                add_notifiers(
                    object=item,
                    callback=callback,
                    dispatch=dispatch,
                    path=path,
                    target=target,
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

    @classmethod
    def from_nodes(cls, node, *nodes):
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
    node=FilteredTraitListener(
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