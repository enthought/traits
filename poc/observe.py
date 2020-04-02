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


from poc.events import CTraitObserverEvent, ListObserverEvent
from poc.interfaces import INotifiableObject
from poc.trait_observer_notifier import (
    TraitObserverNotifier,
)
from poc.listener_change_notifier import (
    ListenerChangeNotifier,
)

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


# These are user-facing notifier factories...
DISPATCHERS = {
    "same": dispatch_same,
}


def observe(object, callback, path, remove, dispatch):
    """
    Parameters
    ----------
    object : HasTrait
        An object on which trait changes are observed based on the given
        (attribute) path.
    callback : callable(object)
        A callable which will receive an event object with information
        about a change. The type and interface of this event object
        depends on the type of events. For example, a change to a simple
        trait will emit CTraitObserverEvent. A mutation to a list
        will emit ListObserverEvent.
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
    object : INotifiableObject
        An object that implements `_notifiers` for returning a list for
        adding notifiers
    callback : callable(event)
        A callable conforming to the notifier signature. ``event`` is
        an object representing the change to notify about. Its type
        and content depends on the change.
    path : ListenerPath
        Path for listening to extended traits.
    target : Any
        Sets the context for the (actual) callback. In practice, it is
        the HasTrait instance on which the listener path is defined and
        will be seen by users as the "owner" of the notifier.
        Strictly speaking, this object sets the context for the notifier
        and does not have to be a notifiable object.
    dispatcher : callable(callable, args, kwargs)
        Callable for dispatching the callback, i.e. dispatching
        callback on a different thread.
    """

    listener = path.node
    for this_target in listener.iter_this_targets(object):
        if listener.notify:
            notifier = listener.create_user_notifier(
                object=this_target,
                callback=callback,
                target=target,
                dispatcher=dispatcher,
            )
            notifier.add_to(object=this_target)

        for next_path in path.nexts:

            change_notifier = listener.get_change_notifier(
                callback=callback,
                path=next_path,
                target=target,
                dispatcher=dispatcher,
            )
            change_notifier.add_to(object=this_target)

            for next_target in listener.iter_next_targets(object):
                add_notifiers(
                    object=next_target,
                    callback=callback,
                    path=next_path,
                    target=target,
                    dispatcher=dispatcher,
                )
    for static_path in listener.get_static_paths(path):
        add_notifiers(
            object=object,
            callback=callback,
            path=static_path,
            target=target,
            dispatcher=dispatcher,
        )


def remove_notifiers(object, callback, path, target, dispatcher):
    """ Remove notifiers for a ListenerPath

    Parameters
    ----------
    object : INotifiableObject
        An object that implements `_notifiers` for returning a list for
        removing notifiers
    callback : callable(event)
        A callable conforming to the notifier signature. ``event`` is
        an object representing the change to notify about. Its type
        and content depends on the change.
    path : ListenerPath
        Path for listening to extended traits.
    target : Any
        Sets the context for the (actual) callback. In practice, it is
        the HasTrait instance on which the listener path is defined and
        will be seen by users as the "owner" of the notifier.
        Strictly speaking, this object sets the context for the notifier
        and does not have to be a notifiable object.
    dispatcher : callable(callable, args, kwargs)
        Callable for dispatching the callback, i.e. dispatching
        callback on a different thread.
    """
    listener = path.node
    for this_target in listener.iter_this_targets(object):
        if listener.notify:
            notifier = listener.create_user_notifier(
                object=this_target,
                callback=callback,
                target=target,
                dispatcher=dispatcher,
            )
            notifier.remove_from(this_target)

        for next_path in path.nexts:

            change_notifier = listener.get_change_notifier(
                callback=callback,
                path=next_path,
                target=target,
                dispatcher=dispatcher,
            )
            change_notifier.remove_from(object=this_target)

            for next_target in listener.iter_next_targets(object):
                remove_notifiers(
                    object=next_target,
                    callback=callback,
                    path=next_path,
                    target=target,
                    dispatcher=dispatcher,
                )
    for static_path in listener.get_static_paths(path):
        remove_notifiers(
            object=object,
            callback=callback,
            path=static_path,
            target=target,
            dispatcher=dispatcher,
        )


def is_notifiable(object):
    """ Return true if an object conforms to the expected
    interface for a notifiable object.
    """
    return isinstance(object, INotifiableObject)


class BaseListener:

    def create_user_notifier(self, object, callback, target, dispatcher):
        """ Return an INotifier for calling user-defined callback.
        """
        raise NotImplementedError()

    def prevent_event(self, event):
        """ Return true if the event should be silenced.
        """
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

    def trait_added_matched(self, object, name, trait):
        """ Return true if an added trait should be handled by this listener
        """
        raise NotImplementedError()

    def get_static_paths(self, path):
        """ Return new ListenerPath(s) to be added/removed in addition to
        this listener.

        Parameters
        ----------
        path : ListenerPath
            The current listener path when this listener is the root.

        Returns
        -------
        paths: list of ListenerPath
        """
        raise NotImplementedError()


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

    def create_user_notifier(self, object, callback, target, dispatcher):
        return TraitObserverNotifier(
            observer=callback,
            owner=object._notifiers(True),
            target=target,
            dispatcher=dispatcher,
            prevent_event=self.prevent_event,
            event_factory=CTraitObserverEvent,
        )

    def prevent_event(self, event):
        """ Return true if the event should be silenced.
        """
        return event.old is Uninitialized

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
            dispatcher=dispatcher,
            event_factory=CTraitObserverEvent,
        )

    @staticmethod
    def change_callback(event, callback, path, target, dispatcher):
        if is_notifiable(event.old):
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

    def trait_added_matched(self, object, name, trait):
        """ Return true if an added trait should be handled by this listener
        """
        return self.filter(name, trait)

    def get_static_paths(self, path):
        """ Return new ListenerPath(s) to be added/removed in addition to
        this listener.

        Parameters
        ----------
        path : ListenerPath
            The current listener path when this listener is the root.

        Returns
        -------
        paths: list of ListenerPath
        """
        return [
            ListenerPath(node=TraitAddedListener(), nexts=[path])
        ]


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

    def create_user_notifier(self, object, callback, target, dispatcher):
        return TraitObserverNotifier(
            observer=callback,
            owner=object._notifiers(True),
            target=target,
            dispatcher=dispatcher,
            prevent_event=self.prevent_event,
            event_factory=CTraitObserverEvent,
        )

    def prevent_event(self, event):
        return (
            event.old is Uninitialized
            or (
                self.comparison_mode is ComparisonMode.equality
                and event.old == event.new
            )
        )

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
            dispatcher=dispatcher,
            event_factory=CTraitObserverEvent,
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

    def trait_added_matched(self, object, name, trait):
        """ Return true if an added trait should be handled by this listener
        """
        return name == self.name

    def get_static_paths(self, path):
        """ Return new ListenerPath(s) to be added/removed in addition to
        this listener.

        Parameters
        ----------
        path : ListenerPath
            The current listener path when this listener is the root.

        Returns
        -------
        paths: list of ListenerPath
        """
        return [
            ListenerPath(node=TraitAddedListener(), nexts=[path])
        ]


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
            dispatcher=dispatcher,
            event_factory=CTraitObserverEvent,
        )

    @staticmethod
    def change_callback(event, callback, path, target, dispatcher):
        # The event comes from trait_added
        listener = path.node
        object = event.object
        name = event.new
        trait = object.trait(name=name)
        if listener.trait_added_matched(object, name, trait):
            add_notifiers(
                object=object,
                callback=callback,
                path=ListenerPath(
                    node=RequiredTraitListener(
                        name=name, notify=listener.notify),
                    nexts=path.nexts
                ),
                target=target,
                dispatcher=dispatcher,
            )

    def get_static_paths(self, path):
        """ Return new ListenerPath(s) to be added/removed in addition to
        this listener.

        Parameters
        ----------
        path : ListenerPath
            The current listener path when this listener is the root.

        Returns
        -------
        paths: list of ListenerPath
        """
        return []


class ListItemListener(BaseListener):

    def __init__(self, notify):
        self.notify = notify

    def __eq__(self, other):
        return type(self) is type(other) and self.notify == other.notify

    def prevent_event(self, event):
        """ Return true if the event should be silenced.
        """
        return False

    def create_user_notifier(self, object, callback, target, dispatcher):
        return TraitObserverNotifier(
            observer=callback,
            owner=object._notifiers(True),
            target=target,
            dispatcher=dispatcher,
            prevent_event=self.prevent_event,
            event_factory=ListObserverEvent,
        )

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
            dispatcher=dispatcher,
            event_factory=ListObserverEvent,
        )

    @staticmethod
    def change_callback(event, callback, path, target, dispatcher):
        logger.debug(
            "Handling list change. "
            "({!r})".format(
                (event.new, event.removed, event.added, path.node))
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

    def trait_added_matched(self, object, name, trait):
        """ Return true if an added trait should be handled by this listener
        """
        return False

    def get_static_paths(self, path):
        """ Return new ListenerPath(s) to be added/removed in addition to
        this listener.

        Parameters
        ----------
        path : ListenerPath
            The current listener path when this listener is the root.

        Returns
        -------
        paths: list of ListenerPath
        """
        return []


class DictValueListener(BaseListener):
    # TODO: Define this class taking into account
    # what is going to happen in TraitDictObject

    def __init__(self, notify):
        self.notify = notify


class ListenerPath:

    def __init__(self, node, nexts=()):
        """
        Parameters
        ----------
        node : BaseListener
            A context specific listener, e.g. listening to changes
            on a named trait.
        nexts : list of ListenerPath
            Branches of the path.
        """
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
