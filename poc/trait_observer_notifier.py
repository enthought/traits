#####
# Copy from enthought/traits#931
#####

import logging
import threading
from types import MethodType
import weakref

from traits.trait_base import Uninitialized

logger = logging.getLogger()


class TraitObserverNotifier:
    """ Observer for a trait on a HasTraits instance.

    Parameters
    ----------
    observer : callable(event)
        The observer callback.  This should accept a single ObserverEvent
        instance as an argument.  If the callable is a method, only a weak
        reference to the method will be used.
    owner : list of callables
        The list of notifiers that this is part of.
    target : optional HasTraits instance
        An optional object which is required for the observer to function.  If
        provided, then only a weak reference is held to this object.
    prevent_event : callable(object) -> boolean
        A callable to return true if an event should be silenced before
        being dispatched.
    event_factory : callable(*args) -> event
        A callable that receives all arguments given when a notifier is called,
        and return an event object to be passed to the user callback.
    """

    def __init__(
            self, observer, owner, target, dispatcher, prevent_event,
            event_factory):
        if isinstance(observer, MethodType):
            # allow observing object methods to be garbage collected
            self._observer = weakref.WeakMethod(
                observer, self.observer_deleted)
        else:
            self._observer = observer

        if target is not None:
            self._target = weakref.ref(target, self.observer_deleted)
        else:
            self._target = target

        self.owner = owner
        self.dispatcher = dispatcher
        self.target_count = 0
        self.prevent_event = prevent_event
        self.event_factory = event_factory

    def __repr__(self):
        return "<TraitObserverNotifier target={!r}>".format(
            self.target,
        )

    def add_to(self, object):
        """ Add this notifier to an INotifiableObject
        """
        observer_notifiers = object._notifiers(True)
        for other in observer_notifiers:
            if other.equals(self):
                logger.debug("ADD: Incrementing notifier %r", other)
                other.target_count += 1
                break

        else:
            logger.debug(
                "ADD: adding notifier %r for object %r",
                self, object
            )
            observer_notifiers.append(self)
            self.target_count += 1

    def remove_from(self, object):
        """ Remove this notifier from an INotifiableObject
        """
        observer_notifiers = object._notifiers(True)
        logger.debug("Removing from %r", observer_notifiers)
        for other in observer_notifiers[:]:
            if other.equals(self):
                other.target_count -= 1

                if other.target_count < 0:
                    raise ValueError("Race condition: Count becomes negative.")

                if other.target_count == 0:
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

    def __call__(self, *args):
        """ Called by the notifiable object."""
        self.dispatch(self.event_factory(*args))

    def dispatch(self, event):
        """ Dispatch the event.
        Expected to be called by subclass's __call__
        """
        if self.prevent_event(event):
            return
        self.dispatcher(self._notify, args=(event, ))

    def _notify(self, event):
        # keep a reference to the observer while handling callback
        observer = self.observer
        # keep a reference to the target while handling callback
        target = self.target    # noqa: F841

        if observer is None:
            return

        if self._target is not None and target is None:
            return

        observer(event)

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
        #: TODO: Shall we compare dispatch as well?
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
