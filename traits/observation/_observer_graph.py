# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


class ObserverGraph:
    """ An ``ObserverGraph`` is an object for describing what traits are being
    observed on an instance of ``HasTraits``.

    The most basic unit in a graph is a node, which is a context specific
    observer. For example, a node can be an observer specialized in
    changes on a named trait, an observer specialized in
    changes on a number of traits matching a certain criteria, an observer
    specialized in mutations on a list, etc.

    The most basic example is an ``ObserverGraph`` that contains only one node,
    e.g. for observing changes on a named trait.

    An ``ObserverGraph`` can have branches, e.g. to observe more than one trait
    on a nested object. The attribute ``children`` represents these branches.
    Each item in ``children`` is another ``ObserverGraph``.

    In order to (1) avoid hooking up a user callback with the same observer
    twice, and (2) remove an observer when they are not needed, once an
    ``ObserverGraph`` object is constructed (e.g. after mutating ``children``
    for constructing branches) and is ready to be used against an instance
    of ``HasTraits``, it should not be mutated again.

    For the same reason, ``ObserverGraph`` implements ``__hash__`` and
    ``__eq__`` and requires its nodes to also support these methods.

    An ``ObserverGraph`` does not keep states regarding the HasTraits instances
    and the user callbacks it was used with. An ``ObserverGraph`` can be
    reused multiple times on different ``HasTraits`` instance and with
    different user callback.

    This object is considered a low-level object for the observer mechanism.
    It is not intended to be instantiated by users directly. Users will be
    given higher-level wrappers for creating ``ObserverGraph`` objects.

    Parameters
    ----------
    node : any
        A context specific observer.
        It must be a hashable object. In practice, this will be
        an instance that implements ``IObserver``.
    children : iterable of ObserverGraph, optional
        Branches on this graph. All children must be unique.

    Raises
    ------
    ValueError
        If not all children are unique.
    """

    __slots__ = ("node", "children")

    def __init__(self, *, node, children=None):

        if children is not None and len(set(children)) != len(children):
            raise ValueError("Not all children are unique.")

        self.node = node
        self.children = list(children) if children is not None else []

    def __hash__(self):
        """ Return the hash of this ObserverGraph."""
        return hash(
            (type(self).__name__, self.node, frozenset(self.children))
        )

    def __eq__(self, other):
        """ Return true if another object is an ObserverGraph with the
        same content. The order of children is not taken into account
        in the comparison.
        """
        return (
            type(self) is type(other)
            and self.node == other.node
            and set(self.children) == set(other.children)
        )

    def __repr__(self):
        formatted_args = [f"node={self.node!r}"]
        if self.children:
            formatted_args.append(f"children={self.children!r}")

        return f"{self.__class__.__name__}({', '.join(formatted_args)})"
