# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import asyncio
import inspect

from traits.observation._observe import add_or_remove_notifiers
from traits.observation.expression import compile_expr

#: Set to hold references to active async traits handlers.
_active_handler_tasks = set()


def dispatch_same(handler, event):
    """ Dispatch an event handler on the same thread.

    This dispatcher accepts both callables and async callables, the latter
    being dispatched asynchronously via an async Task.  Asynchronous dispatch
    is only available when an async event loop is running; it will raise if
    it cannot create an async Task.

    Parameters
    ----------
    handler : callable(event) or async callable(event)
        User-defined callable to handle change events.
        ``event`` is an object representing the change.
        Its type and content depends on the change.
    event : object
        The event object to be given to handler.
    """
    if inspect.iscoroutinefunction(handler):
        task = asyncio.create_task(handler(event))
        _active_handler_tasks.add(task)
        task.add_done_callback(_active_handler_tasks.discard)
    else:
        handler(event)


def observe(
        object, expression, handler,
        *, remove=False, dispatcher=dispatch_same):
    """ Observer or unobserve traits on an object.

    Parameters
    ----------
    object : object
        An object to be observed. Usually an instance of ``HasTraits``.
    expression : ObserverExpression
        An object describing what traits are being observed.
    handler : callable(event)
        User-defined callable to handle change events.
        ``event`` is an object representing the change.
        Its type and content depends on the change.
    remove : boolean, optional
        If true, remove notifiers. i.e. unobserve the traits.
    dispatcher : callable(callable, event), optional
        Callable for dispatching the user-defined handler, e.g. dispatching
        callback on a different thread. Default is to dispatch on the same
        thread.
    """
    apply_observers(
        object,
        graphs=compile_expr(expression),
        handler=handler,
        dispatcher=dispatcher,
        remove=remove,
    )


def apply_observers(object, graphs, handler, *, dispatcher, remove=False):
    """ Apply one or more ObserverGraphs to an object and handler.

    Parameters
    ----------
    object : object
        An object to be observed. Usually an instance of ``HasTraits``.
    graphs : list of ObserverGraph
        Graphs describing the observation patterns to apply.
    handler : callable(event)
        User-defined callable to handle change events.
        ``event`` is an object representing the change.
        Its type and content depends on the change.
    dispatcher : callable(callable, event).
        Callable for dispatching the user-defined handler, e.g. dispatching
        callback on a different thread.
    remove : boolean, optional
        If True, remove notifiers. i.e. unobserve the traits. The default
        is False.
    """
    for graph in graphs:
        add_or_remove_notifiers(
            object=object,
            graph=graph,
            handler=handler,
            target=object,
            dispatcher=dispatcher,
            remove=remove,
        )
