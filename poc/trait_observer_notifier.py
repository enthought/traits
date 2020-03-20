#####
# Copy from enthought/traits#931
#####

import logging
from types import MethodType
import weakref

from traits.trait_base import Uninitialized

logger = logging.getLogger()

class BaseObserverEvent(object):
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
        trait_list, index, removed, added = new
        self.new = trait_list
        self.added = added
        self.removed = removed
        self.index = index


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
    """

    def __init__(self, observer, owner, target=None, event_factory=ObserverEvent):
        if isinstance(observer, MethodType):
            # allow observing object methods to be garbage collected
            self.observer = weakref.WeakMethod(observer, self.observer_deleted)
            self.notify_observer = self._notify_weak_observer
        else:
            self.observer = observer
            self.notify_observer = self._notify_function_observer

        self.owner = owner
        self.target = target
        if target is not None:
            self.target_count = 1
        else:
            self.target_count = 0

        self.event_factory = event_factory

    def __repr__(self):
        return "<TraitObserverNotifier target={!r} event_factory={!r}>".format(
            self.target,
            self.event_factory
        )

    def __call__(self, object, name, old, new):
        """ Notifier for observers.

        This adapts the underlying CTrait notifier signature to an event
        object that is expected by observers.
        """
        if self.target is not None and self.target_count == 0:
            raise ValueError("I should have been removed!")
        if old is not Uninitialized:
            logger.debug("Notifier is called: {!r} with {!r}".format(self, (object, name, old, new)))
            self.notify_observer(object, name, old, new)

    def dispatch(self, observer, object, name, old, new):
        """ Create an event and call the observer.
        """
        if self.target is not None:
            # keep a reference to the target while handling callback
            target = self.target
        else:
            target = None
        event = self.event_factory(object, name, old, new)
        observer(event)

    def equals(self, observer):
        """ Check if equal to either self or the observer callback.

        Parameters
        ----------
        observer : callable
            The observer we are comparing to.
        """
        if observer is self:
            return True
        elif observer is None:
            return False

        if isinstance(self.observer, weakref.WeakMethod):
            return self.observer() is observer
        else:
            return self.observer is observer

    def increment_target_count(self, target):
        if self.target is not target:
            raise ValueError("Unknown target.")
        self.target_count += 1

    def decrement_target_count(self, target):
        if self.target is not target:
            raise ValueError("Unknown target.")
        self.target_count -= 1
        if self.target_count < 0:
            raise ValueError("Too many decrement.")

    @property
    def target(self):
        if self._target is not None:
            return self._target()
        return self._target

    @target.setter
    def target(self, value):
        if value is not None:
            self._target = weakref.ref(value, self.observer_deleted)
        else:
            self._target = value

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
        self.target = None
        self.target_count = 0

    def dispose(self):
        """ Perform clean-up when no longer in use.
        """
        pass

    def _notify_function_observer(self, object, name, old, new):
        self.dispatch(self.observer, object, name, old, new)

    def _notify_method_observer(self, object, name, old, new):
        observer = self.observer()
        if observer is not None:
            self.dispatch(observer, object, name, old, new)