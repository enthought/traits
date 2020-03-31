#####
# Copy from enthought/traits#931
#####

import logging
import threading
from types import MethodType
import weakref

from traits.trait_base import Uninitialized

logger = logging.getLogger()


class BaseObserverEvent(object):

    def __init__(self, arg1, arg2, arg3, arg4):
        raise NotImplementedError()

    @property
    def new(self):
        return self._new

    @new.setter
    def new(self, value):
        self._new = value


class ObserverEvent(BaseObserverEvent):

    def __init__(self, object, name, old, new):
        self.object = object
        self.name = name
        self.old = old
        self.new = new


class ListObserverEvent(BaseObserverEvent):

    def __init__(self, trait_list, trait_list_event):
        self.new = trait_list
        self.added = trait_list_event.added
        self.removed = trait_list_event.removed
        self.index = trait_list_event.index


class TraitObserverNotifier(object):
    """ Observer for a trait on a HasTraits instance.

    Attributes
    ----------
    observer : callable or WeakMethod
        The observer callback or a weak reference to it if it is a method.
    notifier_observer : method
        The method to use for dispatch, either
    owner : list of callables
        The list of notifiers that this is part of.
    target : optional HasTraits instance
        An optional object which is required for the observer to function.  If
        provided, then only a weak reference is held to this object.
    event_factory : callable
        A factory function or class that creates appropriate event objects.
        If the factory returns None, the event is silenced.
    dispatcher : callable(callable, BaseObserverEvent)
        Callable to eventually dispatch an event, e.g. to the same thread
        or a different thread.

    Parameters
    ----------
    observer : callable
        The observer callback.  This should accept a single ObserverEvent
        instance as an argument.  If the callable is a method, only a weak
        reference to the method will be used.
    owner : list of callables
        The list of notifiers that this is part of.
    target : optional HasTraits instance
        An optional object which is required for the observer to function.  If
        provided, then only a weak reference is held to this object.
    event_factory : callable
        A factory function or class that creates appropriate event objects.
        If the factory returns None, the event is silenced.
    """

    def __init__(
            self, observer, owner, target, event_factory, dispatcher):
        if isinstance(observer, MethodType):
            # allow observing object methods to be garbage collected
            self._observer = weakref.WeakMethod(observer, self.observer_deleted)
        else:
            self._observer = observer

        if target is not None:
            self._target = weakref.ref(target, self.observer_deleted)
        else:
            self._target = target

        self.owner = owner
        self.dispatcher = dispatcher
        self.target_count = 1
        self.event_factory = event_factory

    def __repr__(self):
        return "<TraitObserverNotifier target={!r} event_factory={!r}>".format(
            self.target,
            self.event_factory
        )

    def __call__(self, *args):
        """ Called by INotifiableObject when it reports changes.

        It adaptes varying notifier signatures into event objects to be
        sent to the callback such that the callback only receives one
        argument.
        """

        if self.target_count <= 0:
            raise ValueError("I should have been removed!")

        event = self.event_factory(*args)
        if event is None:
            logger.debug("Event is silenced for %r", args)
            return

        logger.debug(
            "Notifier is called: {!r} with {!r}".format(
                self, args))
        self.dispatcher(self.dispatch, args=(event, ))

    def dispatch(self, event):
        # keep a reference to the observer while handling callback
        observer = self.observer
        # keep a reference to the target while handling callback
        target = self.target    # noqa: F841

        if observer is None:
            return

        if self._target is not None and target is None:
            return

        observer(event)

    def increment(self):
        self.target_count += 1

    def decrement(self):
        self.target_count -= 1
        if self.target_count < 0:
            raise ValueError("Too many decrement.")

    def can_be_removed(self):
        return self.target_count <= 0

    @property
    def target(self):
        if self._target is not None:
            return self._target()
        return self._target

    @property
    def observer(self):
        if isinstance(self._observer, weakref.WeakMethod):
            return self._observer()
        return self._observer

    def equals(self, other):
        if type(other) is not type(self):
            return False
        return other.observer is self.observer and other.target is self.target

    def observer_deleted(self, ref=None):
        """ Callback to remove this from the list of notifiers.

        Parameters
        ----------
        ref : object
            The object about to be deleted, if any.  This is not used, but
            is required as part of the weakref callback mechanisms.
        """
        # This code could be running on any thread, as it is invoked by the
        # garbage collection mechanisms.  There is a potential race condition
        # where notifier might have already been removed on a different thread
        # independently.  As a result this method must be idempotent.
        try:
            self.owner.remove(self)
        except ValueError:
            pass
        self.owner = None
        self._target = None
        self.target_count = 0

    def dispose(self):
        """ Perform clean-up when no longer in use.
        """
        pass


class CTraitNotifier(TraitObserverNotifier):

    def __call__(self, object, name, old, new):
        """ Called by an instance of HasTraits.
        See ``call_notifier`` in ctraits.c
        """
        super(CTraitNotifier, self).__call__(object, name, old, new)


class ListNotifier(TraitObserverNotifier):

    def __call__(self, trait_list, event):
        """ Called by an instance of TraitListObject.
        """
        super(ListNotifier, self).__call__(trait_list, event)
