# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.observation._observe import add_or_remove_notifiers


def dispatch_same(handler, event):
    """ Dispatch an event handler on the same thread.

    Parameters
    ----------
    handler : callable(event)
        User-defined callable to handle change events.
        ``event`` is an object representing the change.
        Its type and content depends on the change.
    event : object
        The event object to be given to handler.
    """
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
    dispatcher : callable(callable, event)
        Callable for dispatching the user-defined handler, i.e. dispatching
        callback on a different thread.
    """
    # Implicit interface: ``expression`` can be anything with a method
    # ``_as_graphs`` that returns a list of ObserverGraph.
    for graph in expression._as_graphs():
        add_or_remove_notifiers(
            object=object,
            graph=graph,
            handler=handler,
            target=object,
            dispatcher=dispatcher,
            remove=remove,
        )
