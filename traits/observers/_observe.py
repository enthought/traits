# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


def add_or_remove_notifiers(
        *, object, graph, handler, target, dispatcher, remove):
    """ Add/Remove notifiers on objects following the description on an
    ObserverGraph.

    Parameters
    ----------
    object : IObservable
        An object to be observed.
    graph : ObserverGraph
        A graph describing what and how extended traits are being observed.
    handler : callable(event)
        User-defined callable to handle change events.
        ``event`` is an object representing the change.
        Its type and content depends on the change.
    target : Any
        Sets the context for the handler. In practice, it is
        the HasTrait instance on which the observer graph is defined and
        will be seen by users as the "owner" of the observer.
        Strictly speaking, this object does not have to be an observable.
    dispatcher : callable(callable, event)
        Callable for dispatching the user-defined handler, i.e. dispatching
        callback on a different thread.
    remove : boolean
        If true, notifiers are being removed.
    """

    observer = graph.node
    for observable in observer.iter_observables(object):
        if observer.notify:
            notifier = observer.get_notifier(
                observable=observable,
                handler=handler,
                target=target,
                dispatcher=dispatcher,
            )
            if remove:
                notifier.remove_from(observable)
            else:
                notifier.add_to(observable)

        for child_graph in graph.children:

            change_notifier = observer.get_maintainer(
                graph=child_graph,
                handler=handler,
                target=target,
                dispatcher=dispatcher,
            )
            if remove:
                change_notifier.remove_from(observable)
            else:
                change_notifier.add_to(observable)

    for child_graph in graph.children:
        for next_object in observer.iter_objects(object):
            add_or_remove_notifiers(
                object=next_object,
                handler=handler,
                graph=child_graph,
                target=target,
                dispatcher=dispatcher,
                remove=remove,
            )

    for extra_graph in observer.iter_extra_graphs(graph):
        add_or_remove_notifiers(
            object=object,
            handler=handler,
            graph=extra_graph,
            target=target,
            dispatcher=dispatcher,
            remove=remove,
        )
