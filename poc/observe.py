from functools import partial

from traits.trait_base import Undefined
from traits.ctrait import CHasTraits, CTrait

from .interfaces import INotifiableObject
from .trait_observer_notifier import (
    ObserverEvent,
    ListObserverEvent,
    TraitObserverNotifier,
)


# We need to identify objects which has this `_notifiers` methods
# We could do the easy-to-ask-forgiveness-than-permission way.
# Or we could do the leap-before-you-leap way.
# Here is the LBYL way

INotifiableObject.register(CTrait)
INotifiableObject.register(CHasTraits)


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
        )
    else:
        add_notifiers(
            path=path,
            object=object,
            callback=callback,
            dispatch=dispatch,
        )


WRAPPERS = {
    # These are placeholders.
    # The values are supposed to be different.
    "extended": TraitObserverNotifier,
    "same": TraitObserverNotifier,
    "ui": TraitObserverNotifier,
}


def add_notifiers(object, callback, dispatch, path):
    listener = path.node
    if listener.notify:
        for target in listener.iter_this_targets(object):
            add_notifier(
                object, callback, dispatch, listener.event_factory,
            )
    if path.next is not None:
        for target in listener.iter_next_targets(object):
            add_notifiers(target, callback, dispatch, path.next)


def add_notifier(object, callback, dispatch, event_factory):
    if object is Undefined:
        # TODO: Do something to defer adding a notifier
        return

    observer_notifiers = object._notifiers(True)
    for other in observer_notifiers:
        if other.equals(callback):
            break
    else:
        new_notifier = WRAPPERS[dispatch](
            observer=callback,
            owner=observer_notifiers,
            target=object,
            event_factory=event_factory,
        )
        observer_notifiers.append(new_notifier)


def remove_notifer(object, callback):
    if object is Undefined:
        return
    observer_notifiers = object._notifiers(True)
    for other in observer_notifiers[:]:
        if other.equals(callback):
            observer_notifiers.remove(other)
            other.dispose()
            break


def remove_notifiers(object, callback, path):
    listener = path.node
    if listener.notify:
        for target in listener.iter_this_targets(object):
            remove_notifer(target, callback)
    if path.next is not None:
        for target in listener.iter_next_targets(object):
            remove_notifiers(target, callback, path)


def has_notifiers(object):
    return isinstance(object, INotifiableObject)


class BaseListener:

    event_factory = ObserverEvent

    @property
    def notify(self):
        """ Whether to call notifiers for changes on this item."""
        return getattr(self, "_notify", True)

    @notify.setter
    def notify_setter(self, value):
        self._notify = value

    def iter_this_targets(self, object):
        yield from ()

    def iter_next_targets(self, object):
        # For walking down the path of Listeners
        yield from ()


class AnyTraitListener(BaseListener):

    def iter_this_targets(self, object):
        yield object

    def iter_next_targets(self, object):
        for name in object.trait_names():
            value = object.__dict__.get(name, Undefined)
            if has_notifiers(value):
                yield value


class FilteredTraitListener(BaseListener):

    def __init__(self, notify, filter):
        self.filter = filter
        self.notify = notify

    def iter_this_targets(self, object):
        # object must be an instance of HasTraits
        for name, trait in object.traits().items():
            if self.filter(trait):
                yield object._trait(name, 2)

    def iter_next_targets(self, object):
        for name, trait in object.traits().items():
            if self.filter(trait):
                value = object.__dict__.get(name, Undefined)
                if has_notifiers(value):
                    yield value


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
        if has_notifiers(value):
            yield value


OptionalTraitListener = partial(NamedTraitListener, optional=True)

RequiredTraitListener = partial(NamedTraitListener, optional=False)


class ListItemListener(BaseListener):

    def __init__(self, notify):
        self.notify = notify

    def iter_this_targets(self, object):
        # object should be a TraitListObject
        yield object

    def iter_next_target(self, object):
        for item in object:
            if has_notifiers(item):
                yield item


def handle_list_item_changed(event, callback, dispatch, path):
    # The parent node of path should be a ListItemListener
    list_ = getattr(event.object, event.name)

    removed = set(event.removed) ^ set(list_)
    for item in removed:
        if has_notifiers(item):
            remove_notifiers(item, callback, path)

    for item in event.added:
        if has_notifiers(item):
            add_notifiers(item, callback, dispatch, path)


class ListenerPath:

    def __init__(self, node, next=None):
        self.node = node
        self.next = next


# "inst.attr"
# fire if inst is changed, or inst.attr is changed
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=RequiredTraitListener(name="attr", notify=True),
        next=None,
    )
)

# "inst:attr"
# fire if inst.attr is changed
# do not fire if inst is changed (even if it is changed such that
# inst.attr is changed)
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=False),
    next=ListenerPath(
        node=RequiredTraitListener(name="attr", notify=True),
        next=None,
    ),
)

# "[inst1, inst2].attr"
# This is equivalent to having two paths
paths = [
    ListenerPath(
        node=RequiredTraitListener(name="inst1", notify=True),
        next=ListenerPath(
            node=RequiredTraitListener(name="attr", notify=True),
            next=None,
        )
    ),
    # path2
    ListenerPath(
        node=RequiredTraitListener(name="inst2", notify=True),
        next=ListenerPath(
            node=RequiredTraitListener(name="attr", notify=True),
            next=None,
        )
    ),
]

# "inst.container"
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=RequiredTraitListener(name="constainer", notify=True),
    ),
)

# "inst.container_items"
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=RequiredTraitListener(name="constainer", notify=False),
        next=ListenerPath(
            node=ListItemListener(notify=True),
            next=None,
        ),
    ),
)

# "inst.[inst1, inst2].attr"
paths = [
    ListenerPath(
        node=RequiredTraitListener(name="inst", notify=True),
        next=ListenerPath(
            node=RequiredTraitListener(name="inst1", notify=True),
            next=ListenerPath(
                node=RequiredTraitListener(name="attr", notify=True),
                next=None,
            )
        ),
    ),
    ListenerPath(
        node=RequiredTraitListener(name="inst", notify=True),
        next=ListenerPath(
            node=RequiredTraitListener(name="inst2", notify=True),
            next=ListenerPath(
                node=RequiredTraitListener(name="attr", notify=True),
                next=None,
            ),
        ),
    ),
]

# "inst.attr?"
path = ListenerPath(
    node=RequiredTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=OptionalTraitListener(name="attr", notify=True),
        next=None,
    )
)

# "inst.attr*"
# this should match inst.attr.attr.attr.attr....
attr = RequiredTraitListener(name="attr", notify=True)
path = ListenerPath(node=OptionalTraitListener(name="inst", notify=True))
path.next = path


# "inst1?.inst2?.attr"
path = ListenerPath(
    node=OptionalTraitListener(name="inst1", notify=True),
    next=ListenerPath(
        node=OptionalTraitListener(name="inst1", notify=True),
        next=ListenerPath(
            node=RequiredTraitListener(name="attr", notify=True),
            next=None,
        ),
    )
)

# Listen to changes to the items in the values of Dict(Str(), List())
path = ListenerPath(
    node=RequiredTraitListener(name="mapping", notify=True),
    next=ListenerPath(
        node=DictValueListener(notify=True),
        next=ListenerPath(
            node=ListItemListener(notify=True),
        )
    )
)

# Listen to all traits with a metadata 'updated'
path = ListenerPath(
    node=FilteredTraitListener(filter=lambda trait: "updated" in trait.__dict__),
    next=None,
)


# Listen to any traits, then any traits of each of these traits...
path = ListenerPath(
    node=AnyTraitListener(),
    next=None,
)
path.next = path