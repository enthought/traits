# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Classes that implement and support the Traits change notification mechanism
"""

import contextlib
import logging
import threading
from threading import local as thread_local
from threading import Thread
import traceback
from types import MethodType
import weakref
import sys

from .constants import ComparisonMode, TraitKind
from .trait_base import Uninitialized
from .trait_errors import TraitNotificationError

# Global Data

# The currently active handler for notifications that must be run on the UI
# thread, or None if no handler has been set.
# Note: the Pyface library current accesses the `ui_handler` attribute
# directly, so we can't make it private yet.
ui_handler = None


def get_ui_handler():
    """
    Return the current user interface thread handler.
    """
    return ui_handler


def set_ui_handler(handler):
    """ Sets up the user interface thread handler.
    """
    global ui_handler

    ui_handler = handler


def ui_dispatch(handler, *args, **kw):
    if threading.current_thread() == threading.main_thread():
        handler(*args, **kw)
    elif ui_handler is None:
        raise RuntimeError("no UI handler registered for dispatch='ui'")
    else:
        ui_handler(handler, *args, **kw)


class NotificationExceptionHandlerState(object):
    def __init__(self, handler, reraise_exceptions, locked):
        self.handler = handler
        self.reraise_exceptions = reraise_exceptions
        self.locked = locked


class NotificationExceptionHandler(object):
    def __init__(self):
        self.traits_logger = None
        self.main_thread = None
        self.thread_local = thread_local()

    # -- Private Methods ------------------------------------------------------

    def _push_handler(
        self, handler=None, reraise_exceptions=False, main=False, locked=False
    ):
        """ Pushes a new traits notification exception handler onto the stack,
            making it the new exception handler. Returns a
            NotificationExceptionHandlerState object describing the previous
            exception handler.

            Parameters
            ----------
            handler : handler
                The new exception handler, which should be a callable or
                None. If None (the default), then the default traits
                notification exception handler is used. If *handler* is not
                None, then it must be a callable which can accept four
                arguments: object, trait_name, old_value, new_value.
            reraise_exceptions : bool
                Indicates whether exceptions should be reraised after the
                exception handler has executed. If True, exceptions will be
                re-raised after the specified handler has been executed.
                The default value is False.
            main : bool
                Indicates whether the caller represents the main application
                thread. If True, then the caller's exception handler is
                made the default handler for any other threads that are
                created. Note that a thread can explicitly set its own
                exception handler if desired. The *main* flag is provided to
                make it easier to set a global application policy without
                having to explicitly set it for each thread. The default
                value is False.
            locked : bool
                Indicates whether further changes to the Traits notification
                exception handler state should be allowed. If True, then
                any subsequent calls to _push_handler() or _pop_handler() for
                that thread will raise a TraitNotificationError. The default
                value is False.
        """
        handlers = self._get_handlers()
        self._check_lock(handlers)
        if handler is None:
            handler = self._log_exception
        handlers.append(
            NotificationExceptionHandlerState(
                handler, reraise_exceptions, locked
            )
        )
        if main:
            self.main_thread = handlers

        return handlers[-2]

    def _pop_handler(self):
        """ Pops the traits notification exception handler stack, restoring
            the exception handler in effect prior to the most recent
            _push_handler() call. If the stack is empty or locked, a
            TraitNotificationError exception is raised.

            Note that each thread has its own independent stack. See the
            description of the _push_handler() method for more information on
            this.
        """
        handlers = self._get_handlers()
        self._check_lock(handlers)
        if len(handlers) > 1:
            handlers.pop()
        else:
            raise TraitNotificationError(
                "Attempted to pop an empty traits notification exception "
                "handler stack."
            )

    def _handle_exception(self, object, trait_name, old, new):
        """ Handles a traits notification exception using the handler defined
            by the topmost stack entry for the corresponding thread.
        """
        excp_class, excp = sys.exc_info()[:2]
        handler_info = self._get_handlers()[-1]
        handler_info.handler(object, trait_name, old, new)
        if handler_info.reraise_exceptions or isinstance(
            excp, TraitNotificationError
        ):
            raise excp

    def _get_handlers(self):
        """ Returns the handler stack associated with the currently executing
            thread.
        """
        thread_local = self.thread_local
        handlers = getattr(thread_local, "handlers", None)

        if handlers is None:
            if self.main_thread is not None:
                handler = self.main_thread[-1]
            else:
                handler = NotificationExceptionHandlerState(
                    self._log_exception, False, False
                )
            handlers = [handler]
            thread_local.handlers = handlers

        return handlers

    def _check_lock(self, handlers):
        """ Raises an exception if the specified handler stack is locked.
        """
        if handlers[-1].locked:
            raise TraitNotificationError(
                "The traits notification exception handler is locked. "
                "No changes are allowed."
            )

    def _log_exception(self, object, trait_name, old, new):
        """ Logs any exceptions generated in a trait notification handler.

        This method defines the default notification exception handling
        behavior of traits. However, it can be completely overridden by pushing
        a new handler using the '_push_handler' method.
        """
        # When the stack depth is too great, the logger can't always log the
        # message. Make sure that it goes to the console at a minimum:
        excp_class, excp = sys.exc_info()[:2]
        if (
            (excp_class is RuntimeError)
            and (len(excp.args) > 0)
            and (excp.args[0] == "maximum recursion depth exceeded")
        ):
            sys.__stderr__.write(
                "Exception occurred in traits notification "
                "handler for object: %s, trait: %s, old value: %s, "
                "new value: %s.\n%s\n"
                % (
                    object,
                    trait_name,
                    old,
                    new,
                    "".join(traceback.format_exception(*sys.exc_info())),
                )
            )

        logger = self.traits_logger
        if logger is None:
            self.traits_logger = logger = logging.getLogger("traits")

        try:
            logger.exception(
                "Exception occurred in traits notification handler for "
                "object: %s, trait: %s, old value: %s, new value: %s"
                % (object, trait_name, old, new)
            )
        except Exception:
            # Ignore anything we can't log the above way:
            pass


# Traits global notification exception handler

notification_exception_handler = NotificationExceptionHandler()

push_exception_handler = notification_exception_handler._push_handler
pop_exception_handler = notification_exception_handler._pop_handler
handle_exception = notification_exception_handler._handle_exception

# Traits global notification event tracer

_pre_change_event_tracer = None
_post_change_event_tracer = None


def set_change_event_tracers(pre_tracer=None, post_tracer=None):
    """ Set the global trait change event tracers.

    The global tracers are called whenever a trait change event is dispatched.
    There are two tracers: `pre_tracer` is called before the notification is
    sent; `post_tracer` is called after the notification is sent, even if the
    notification failed with an exception (in which case the `post_tracer` is
    called with a reference to the exception, then the exception is sent to
    the `notification_exception_handler`).

    The tracers should be a callable taking 5 arguments:
    ::
      tracer(obj, trait_name, old, new, handler)

    `obj` is the source object, on which trait `trait_name` was changed from
    value `old` to value `new`. `handler` is the function or method that will
    be notified of the change.

    The post-notification tracer also has a keyword argument, `exception`,
    that is `None` if no exception has been raised, and the a reference to the
    raise exception otherwise.
    ::
      post_tracer(obj, trait_name, old, new, handler, exception=None)

    Note that for static trait change listeners, `handler` is not a method, but
    rather the function before class creation, since this is the way Traits
    works at the moment.
    """
    global _pre_change_event_tracer
    global _post_change_event_tracer
    _pre_change_event_tracer = pre_tracer
    _post_change_event_tracer = post_tracer


def get_change_event_tracers():
    """ Get the currently active global trait change event tracers. """
    return _pre_change_event_tracer, _post_change_event_tracer


def clear_change_event_tracers():
    """ Clear the global trait change event tracer. """
    global _pre_change_event_tracer
    global _post_change_event_tracer
    _pre_change_event_tracer = None
    _post_change_event_tracer = None


@contextlib.contextmanager
def change_event_tracers(pre_tracer, post_tracer):
    """ Context manager to temporarily change the global event tracers. """
    old_pre_tracer, old_post_tracer = get_change_event_tracers()
    set_change_event_tracers(pre_tracer, post_tracer)
    try:
        yield
    finally:
        set_change_event_tracers(old_pre_tracer, old_post_tracer)


class AbstractStaticChangeNotifyWrapper(object):
    """
    Concrete implementation must define the 'argument_transforms' class
    argument, a dictionary mapping the number of arguments in the event
    handler to a function that takes the arguments (obj, trait_name, old, new)
    and returns the arguments tuple for the actual handler.
    """

    arguments_transforms = {}

    def __init__(self, handler):
        arg_count = handler.__code__.co_argcount
        if arg_count > 4:
            raise TraitNotificationError(
                (
                    "Invalid number of arguments for the static anytrait "
                    "change notification handler: %s. A maximum of 4 "
                    "arguments is allowed, but %s were specified."
                )
                % (handler.__name__, arg_count)
            )
        self.argument_transform = self.argument_transforms[arg_count]

        self.handler = handler

    def __call__(self, object, trait_name, old, new):
        """ Dispatch to the appropriate handler method. """

        if _change_accepted(object, trait_name, old, new):

            # Extract the arguments needed from the handler.
            args = self.argument_transform(object, trait_name, old, new)

            # Send a description of the change event to the event tracer.
            if _pre_change_event_tracer is not None:
                _pre_change_event_tracer(
                    object, trait_name, old, new, self.handler
                )

            try:
                # Call the handler.
                self.handler(*args)
            except Exception as e:
                if _post_change_event_tracer is not None:
                    _post_change_event_tracer(
                        object, trait_name, old, new, self.handler, exception=e
                    )
                handle_exception(object, trait_name, old, new)
            else:
                if _post_change_event_tracer is not None:
                    _post_change_event_tracer(
                        object,
                        trait_name,
                        old,
                        new,
                        self.handler,
                        exception=None,
                    )

    def equals(self, handler):
        return False


class StaticAnytraitChangeNotifyWrapper(AbstractStaticChangeNotifyWrapper):

    # The wrapper is called with the full set of argument, and we need to
    # create a tuple with the arguments that need to be sent to the event
    # handler, depending on the number of those.
    argument_transforms = {
        0: lambda obj, name, old, new: (),
        1: lambda obj, name, old, new: (obj,),
        2: lambda obj, name, old, new: (obj, name),
        3: lambda obj, name, old, new: (obj, name, new),
        4: lambda obj, name, old, new: (obj, name, old, new),
    }


class StaticTraitChangeNotifyWrapper(AbstractStaticChangeNotifyWrapper):

    # The wrapper is called with the full set of argument, and we need to
    # create a tuple with the arguments that need to be sent to the event
    # handler, depending on the number of those.
    argument_transforms = {
        0: lambda obj, name, old, new: (),
        1: lambda obj, name, old, new: (obj,),
        2: lambda obj, name, old, new: (obj, new),
        3: lambda obj, name, old, new: (obj, old, new),
        4: lambda obj, name, old, new: (obj, name, old, new),
    }


class TraitChangeNotifyWrapper(object):
    """ Dynamic change notify wrapper.

    This class is in charge to dispatch trait change events to dynamic
    listener, typically created using the `on_trait_change` method, or
    the decorator with the same name.
    """

    # The wrapper is called with the full set of argument, and we need to
    # create a tuple with the arguments that need to be sent to the event
    # handler, depending on the number of those.
    argument_transforms = {
        0: lambda obj, name, old, new: (),
        1: lambda obj, name, old, new: (new,),
        2: lambda obj, name, old, new: (name, new),
        3: lambda obj, name, old, new: (obj, name, new),
        4: lambda obj, name, old, new: (obj, name, old, new),
    }

    def __init__(self, handler, owner, target=None):
        self.init(handler, owner, target)

    def init(self, handler, owner, target=None):
        # If target is not None and handler is a function then the handler
        # will be removed when target is deleted.
        if type(handler) is MethodType:
            func = handler.__func__
            object = handler.__self__
            if object is not None:
                self.object = weakref.ref(object, self.listener_deleted)
                self.name = handler.__name__
                self.owner = owner
                arg_count = func.__code__.co_argcount - 1
                if arg_count > 4:
                    raise TraitNotificationError(
                        (
                            "Invalid number of arguments for the dynamic "
                            "trait change notification handler: %s. A maximum "
                            "of 4 arguments is allowed, but %s were specified."
                        )
                        % (func.__name__, arg_count)
                    )

                # We use the unbound method here to prevent cyclic garbage
                # (issue #100).
                self.notify_listener = type(self)._notify_method_listener
                self.argument_transform = self.argument_transforms[arg_count]

                return arg_count

        elif target is not None:
            # Set up so the handler will be removed when the target is deleted.
            self.object = weakref.ref(target, self.listener_deleted)
            self.owner = owner

        arg_count = handler.__code__.co_argcount
        if arg_count > 4:
            raise TraitNotificationError(
                (
                    "Invalid number of arguments for the dynamic trait change "
                    "notification handler: %s. A maximum of 4 arguments is "
                    "allowed, but %s were specified."
                )
                % (handler.__name__, arg_count)
            )

        self.name = None
        self.handler = handler

        # We use the unbound method here to prevent cyclic garbage
        # (issue #100).
        self.notify_listener = type(self)._notify_function_listener
        self.argument_transform = self.argument_transforms[arg_count]

        return arg_count

    def __call__(self, object, trait_name, old, new):
        """ Dispatch to the appropriate method.

        We do explicit dispatch instead of assigning to the .__call__ instance
        attribute to avoid reference cycles.
        """

        # `notify_listener` is either the *unbound*
        # `_notify_method_listener` or `_notify_function_listener` to
        # prevent cyclic garbage (issue #100).
        self.notify_listener(self, object, trait_name, old, new)

    def dispatch(self, handler, *args):
        """ Dispatch the event to the listener.

        This method is normally the only one that needs to be overridden in
        a subclass to implement the subclass's dispatch mechanism.
        """
        handler(*args)

    def equals(self, handler):
        if handler is self:
            return True

        if (type(handler) is MethodType) and (handler.__self__ is not None):
            return (handler.__name__ == self.name) and (
                handler.__self__ is self.object()
            )

        return (self.name is None) and (handler == self.handler)

    def listener_deleted(self, ref):
        # In multithreaded situations, it's possible for this method to
        # be called after, or concurrently with, the dispose method.
        # Don't raise in that case.
        try:
            self.owner.remove(self)
        except ValueError:
            pass
        self.object = self.owner = None

    def dispose(self):
        self.object = None

    def _dispatch_change_event(self, object, trait_name, old, new, handler):
        """ Prepare and dispatch a trait change event to a listener. """

        # Extract the arguments needed from the handler.
        args = self.argument_transform(object, trait_name, old, new)

        # Send a description of the event to the change event tracer.
        if _pre_change_event_tracer is not None:
            _pre_change_event_tracer(object, trait_name, old, new, handler)

        # Dispatch the event to the listener.
        try:
            self.dispatch(handler, *args)
        except Exception as e:
            if _post_change_event_tracer is not None:
                _post_change_event_tracer(
                    object, trait_name, old, new, handler, exception=e
                )
            # This call needs to be made inside the `except` block in case
            # the handler wants to re-raise the exception.
            handle_exception(object, trait_name, old, new)
        else:
            if _post_change_event_tracer is not None:
                _post_change_event_tracer(
                    object, trait_name, old, new, handler, exception=None
                )

    def _notify_method_listener(self, object, trait_name, old, new):
        """ Dispatch a trait change event to a method listener. """

        obj_weak_ref = self.object
        if (obj_weak_ref is not None
                and _change_accepted(object, trait_name, old, new)):
            # We make sure to hold a reference to the object before invoking
            # `getattr` so that the listener does not disappear in a
            # multi-threaded case.
            obj = obj_weak_ref()
            if obj is not None:
                # Dynamically resolve the listener by name.
                listener = getattr(obj, self.name)
                self._dispatch_change_event(
                    object, trait_name, old, new, listener
                )

    def _notify_function_listener(self, object, trait_name, old, new):
        """ Dispatch a trait change event to a function listener. """

        if _change_accepted(object, trait_name, old, new):
            self._dispatch_change_event(
                object, trait_name, old, new, self.handler
            )


class ExtendedTraitChangeNotifyWrapper(TraitChangeNotifyWrapper):
    """ Change notify wrapper for "extended" trait change events..

    The "extended notifiers" are set up internally when using extended traits,
    to add/remove traits listeners when one of the intermediate traits changes.

    For example, in a listener for the extended trait `a.b`, we need to
    add/remove listeners to `a:b` when `a` changes.
    """

    def _dispatch_change_event(self, object, trait_name, old, new, handler):
        """ Prepare and dispatch a trait change event to a listener. """

        # Extract the arguments needed from the handler.
        args = self.argument_transform(object, trait_name, old, new)

        # Dispatch the event to the listener.
        try:
            self.dispatch(handler, *args)
        except Exception:
            handle_exception(object, trait_name, old, new)

    def _notify_method_listener(self, object, trait_name, old, new):
        """ Dispatch a trait change event to a method listener. """

        obj_weak_ref = self.object
        if obj_weak_ref is not None:
            # We make sure to hold a reference to the object before invoking
            # `getattr` so that the listener does not disappear in a
            # multi-threaded case.
            obj = obj_weak_ref()
            if obj is not None:
                # Dynamically resolve the listener by name.
                listener = getattr(obj, self.name)
                self._dispatch_change_event(
                    object, trait_name, old, new, listener
                )

    def _notify_function_listener(self, object, trait_name, old, new):
        """ Dispatch a trait change event to a function listener. """

        self._dispatch_change_event(object, trait_name, old, new, self.handler)


class FastUITraitChangeNotifyWrapper(TraitChangeNotifyWrapper):
    """ Dynamic change notify wrapper, dispatching on the UI thread.

    This class is in charge to dispatch trait change events to dynamic
    listener, typically created using the `on_trait_change` method and the
    `dispatch` parameter set to 'ui' or 'fast_ui'.
    """

    def dispatch(self, handler, *args):
        if threading.current_thread() == threading.main_thread():
            handler(*args)
        elif ui_handler is None:
            raise RuntimeError("no UI handler registered for dispatch='ui'")
        else:
            ui_handler(handler, *args)


class NewTraitChangeNotifyWrapper(TraitChangeNotifyWrapper):
    """ Dynamic change notify wrapper, dispatching on a new thread.

    This class is in charge to dispatch trait change events to dynamic
    listener, typically created using the `on_trait_change` method and the
    `dispatch` parameter set to 'new'.
    """

    def dispatch(self, handler, *args):
        Thread(target=handler, args=args).start()


def _change_accepted(object, name, old, new):
    """ Return true if notifications should be emitted for the change.

    Parameters
    ----------
    object : HasTraits
        The object on which the trait is changed.
    name : str
        The name of the trait changed.
    old : any
        The old value
    new : any
        The new value

    Returns
    -------
    accepted : bool
        Whether the event should be emitted.
    """
    if old is Uninitialized:
        return False

    trait = object._trait(name, 2)
    if (trait.type == TraitKind.trait.name
            and trait.comparison_mode == ComparisonMode.equality):
        try:
            return bool(old != new)
        except Exception:
            # Maybe do something else about the exception
            # enthought/traits#1230
            pass
    return True
