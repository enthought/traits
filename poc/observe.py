


def observe(has_trait, callback, path, remove, dispatch):
    pass


class INotifier:

    def __call__(self, object, trait_name, old, new):
        pass

    @property
    def count(self):
        return 0

    @count.setter
    def count(self, value):
        pass


class INotifiableObject:

    def _get_notifiers(self):
        return []


class Trait(INotifiableObject):

    def _get_notifiers(self):
        return self._notifiers(True)


class HasTrait(INotifiableObject):

    def _get_notifiers(self):
        return self._notifiers(True)


class TraitListObject(INotifiableObject):

    def _get_notifiers(self):
        return []

    def _add_notifier(self):
        pass


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

    def iter_lists_of_notifiers(self, object):
        return []


class AnyTraitListener(BaseListener):

    def iter_lists_of_notifiers(self, object):
        yield object._notifiers(True)


class FilteredTraitListener(BaseListener):

    def __init__(self, notify, filter):
        self.filter = filter
        self.notify = notify

    def iter_lists_of_notifiers(self, object):
        for name, trait in object.traits().items():
            if self.filter(trait):
                yield object._trait(name, 2)._notifiers(True)


class SimpleTraitListener(BaseListener):

    def __init__(self, name, notify):
        self.name = name
        self.notify = notify

    def iter_lists_of_notifiers(self, object):
        trait = object.trait(name=self.name)
        if trait is not None:
            yield object._trait(self.name, 2)._notifiers(True)


class ListItemListener(BaseListener):

    def __init__(self, notify):
        self.notify = notify

    def iter_lists_of_notifiers(self, object):
        # Not sure what to do here.
        pass


class ListenerPath:

    def __init__(self, node, next=None):
        self.node = node
        self.next = next


# "inst.attr"
# fire if inst is changed, or inst.attr is changed
path = ListenerPath(
    node=SimpleTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=SimpleTraitListener(name="attr", notify=True),
        next=None,
    )
)

# "inst:attr"
# fire if inst.attr is changed
# do not fire if inst is changed (even if it is changed such that
# inst.attr is changed)
path = ListenerPath(
    node=SimpleTraitListener(name="inst", notify=False),
    next=ListenerPath(
        node=SimpleTraitListener(name="attr", notify=True),
        next=None,
    ),
)

# "[inst1, inst2].attr"
# This is equivalent to having two paths
paths = [
    ListenerPath(
        node=SimpleTraitListener(name="inst1", notify=True),
        next=ListenerPath(
            node=SimpleTraitListener(name="attr", notify=True),
            next=None,
        )
    ),
    # path2
    ListenerPath(
        node=SimpleTraitListener(name="inst2", notify=True),
        next=ListenerPath(
            node=SimpleTraitListener(name="attr", notify=True),
            next=None,
        )
    ),
]

# "inst.container"
path = ListenerPath(
    node=SimpleTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=SimpleTraitListener(name="constainer", notify=True),
    ),
)

# "inst.container_items"
path = ListenerPath(
    node=SimpleTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=SimpleTraitListener(name="constainer", notify=False),
        next=ListenerPath(
            node=ListItemListener(notify=True),
            next=None,
        ),
    ),
)

# "inst.[inst1, inst2].attr"
paths = [
    ListenerPath(
        node=SimpleTraitListener(name="inst", notify=True),
        next=ListenerPath(
            node=SimpleTraitListener(name="inst1", notify=True),
            next=ListenerPath(
                node=SimpleTraitListener(name="attr", notify=True),
                next=None,
            )
        ),
    ),
    ListenerPath(
        node=SimpleTraitListener(name="inst", notify=True),
        next=ListenerPath(
            node=SimpleTraitListener(name="inst2", notify=True),
            next=ListenerPath(
                node=SimpleTraitListener(name="attr", notify=True),
                next=None,
            ),
        ),
    ),
]

# "inst.attr?"
path = ListenerPath(
    node=SimpleTraitListener(name="inst", notify=True),
    next=ListenerPath(
        node=OptionalTraitListener(name="attr", notify=True),
        next=None,
    )
)

# "inst.attr*"
# this should match inst.attr.attr.attr.attr....
attr = SimpleTraitListener(name="attr", notify=True)
path = ListenerPath(node=SimpleTraitListener(name="inst", notify=True))
path.next = path


# "inst1?.inst2?.attr"
path = ListenerPath(
    node=OptionalTraitListener(name="inst1", notify=True),
    next=ListenerPath(
        node=OptionalTraitListener(name="inst1", notify=True),
        next=ListenerPath(
            node=OptionalTraitListener(name="attr", notify=True),
            next=None,
        ),
    )
)

# Listen to changes to the items in the values of Dict(Str(), List())
path = ListenerPath(
    node=SimpleTraitListener(name="mapping", notify=True),
    next=ListenerPath(
        node=DictValueListener(notify=True),
        next=ListenerPath(
            node=ListItemListener(notify=True),
        )
    )
)

# Listen to all traits with a metadata 'updated'
path = ListenerPath(
    node=AnyTraitListener(filter=lambda trait: "updated" in trait.__dict__),
    next=None,
)

