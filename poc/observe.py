from functools import partial

from traits.trait_base import Undefined


def observe(object, callback, path, remove, dispatch):

    listener = path.node
    if listener.notify and remove:
        remove_notifiers(
            listener=listener,
            object=object,
            callback=callback,
        )
    elif listener.notify and not remove:
        add_notifiers(
            listener=listener,
            object=object,
            callback=callback,
            target=None,   # what should target be?
            dispatch=dispatch,
        )

    if path.next is not None:
        for next_object in listener.iter_next_targets(object):
            observe(next_object, callback, path.next, remove, dispatch)


class BaseObserverEvent:
    pass


class ObserverEvent(BaseObserverEvent):

    def __init__(self, object, name, old, new):
        self.object = object
        self.name = name
        self.old = old
        self.new = new


class ListObserverEvent(BaseObserverEvent):

    def __init__(self, object, name, old, new):
        self.object = object
        self.name = name
        self.old = old
        self.new = new
        self.added = new.added
        self.removed = new.removed
        self.index = new.index


class TraitObserverNotifier(object):

    def __init__(
            self, observer, owner, target=None, event_factory=ObserverEvent):
        pass

    def __call__(self, object, name, old, new):
        pass

    @property
    def count(self):
        return getattr(self, "_count", 0)

    @count.setter
    def count(self, value):
        self._count = value


WRAPPERS = {
    # These are placeholders.
    # The values are supposed to be different.
    "extended": TraitObserverNotifier,
    "same": TraitObserverNotifier,
    "ui": TraitObserverNotifier,
}


def add_notifiers(listener, object, callback, target, dispatch):
    if listener.notify:
        raise ValueError(
            "Don't call add_notifiers if the listener is supposed to "
            "be quiet!"
        )
    if object is Undefined:
        # TODO: Do something to defer adding a notifier
        return

    for observer_notifiers in listener.iter_lists_of_notifiers(object):

        for other in observer_notifiers:
            if other.equals(callback):
                other.count += 1
                break
        else:
            new_notifier = WRAPPERS[dispatch](
                observer=callback,
                owner=observer_notifiers,
                target=target,
                event_factory=listener.event_factory,
            )
            new_notifier.count = 1
            observer_notifiers.append(new_notifier)


def remove_notifiers(listener, object, callback):
    for observer_notifiers in listener.iter_lists_of_notifiers(object):
        for other in observer_notifiers[:]:
            if other.equals(callback):
                other.count -= 1
                if other.count == 0:
                    other.observer_deleted()
                    other.dispose()
                break


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

    def iter_lists_of_notifiers(self, object):
        for target in self.iter_this_targets(object):
            yield target._notifiers(True)

    def iter_next_targets(self, object):
        # For walking down the path of Listeners
        yield from ()


class AnyTraitListener(BaseListener):

    def iter_this_targets(self, object):
        yield object

    def iter_next_targets(self, object):
        for name in object.trait_names():
            yield object.__dict__.get(name, Undefined)


class FilteredTraitListener(BaseListener):

    def __init__(self, notify, filter):
        self.filter = filter
        self.notify = notify

    def iter_this_targets(self, object):
        # object must be an instance of HasTraits
        for name, trait in object.traits().items():
            if self.filter(trait):
                yield object._trait(name, 2)


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


OptionalTraitListener = partial(NamedTraitListener, optional=True)

RequiredTraitListener = partial(NamedTraitListener, optional=False)


class ListItemListener(BaseListener):

    def __init__(self, notify):
        self.notify = notify

    def iter_this_targets(self, object):
        # object should be a TraitListObject
        yield object.trait


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