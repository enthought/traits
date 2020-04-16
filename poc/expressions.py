
import copy
from functools import reduce, update_wrapper
from poc.observe import (
    _is_not_none,
    ListenerPath,
    MetadataListener,
    NamedTraitListener,
    _FilteredTraitListener,
    ListItemListener,
    DictItemListener,
    SetItemListener,
)


def observe(object, expression, handler):
    # ``observe`` replaces ``on_trait_change``.
    # ``expression`` replaces ``name`` in ``on_trait_change``.
    # This is an example implementation to demonstrate
    # how the Expression is used. This will fail because
    # ``_observe`` is not implemented here.
    for path in expression.as_paths():
        _observe(object=object, path=path, handler=handler)  # noqa: F821


class Expression:
    """ A user-facing object for constructing the data structures
    required by ``observe`` (a future replacement for
    ``on_trait_change``).

    ``Expression.as_paths()`` creates a new list of ``ListenerPath``
    objects for ``observe`` to operate on.

    While the object constructor is public facing, users will likely
    use one of the module-level convenient functions for creating
    an instance of ``Expression``. Methods on ``Expression``
    allows the users to extend the ``ListenerPath``.
    """
    def __init__(self):
        # ``_levels`` is a list of tuple(branched nodes, cycled nodes)
        # The last item is the most nested level.
        # When paths are constructured from this expression, one starts
        # from the end of this list, to the top, and then continues to
        # the prior_expressions
        self._levels = []

        # Represent prior expressions to be combined in series (JOIN)
        # or in parallel (OR)
        self._prior_expression = None

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self.as_paths() == other.as_paths()

    def __or__(self, expression):
        """ Create a new expression that matches this expression OR
        the given expression.

        e.g. ``t("age") | t("number")`` will match either trait `age`
        or trait `number` on an object.

        Parameters
        ----------
        expression : Expression

        Returns
        -------
        new_expression : Expression
        """
        new = Expression()
        new._prior_expression = _ParallelExpression([self, expression])
        return new

    def then(self, expression):
        """ Create a new expression by extending this expression with
        the given expression.

        e.g. ``t("child").then( t("age") | t("number") )`` on an object
        matches ``child.age`` or ``child.number`` on the object.

        This example is equivalent to
        ``t("child").t("age") | t("child").t("number")``

        Parameters
        ----------
        expression : Expression

        Returns
        -------
        new_expression : Expression
        """

        # if self._prior_expression is None and not self._levels:
        #     # this expression is empty...
        #     new = expression.copy()
        # else:
        new = Expression()
        new._prior_expression = _SeriesExpression([self, expression])
        return new

    def _root_nodes(self):
        """ Return the root branched nodes of this expression. They may come
        from the prior expressions if defined.

        This is for supporting recursions back to the root nodes.

        Returns
        -------
        bnodes : set(BaseListener)
            Nodes for branches.

        Raises
        ------
        ValueError
            If no root nodes are found.
        """
        if not self._levels and self._prior_expression is None:
            raise ValueError("No root nodes")

        if self._prior_expression is not None:
            return self._prior_expression._root_nodes()

        for bnodes in self._levels:
            if bnodes:
                return bnodes

        raise ValueError("No root nodes")

    def as_paths(self):
        """ Return all the ListenerPath for the observer.
        """
        paths = _create_paths(self)
        return set(paths)

    def t(self, name, notify=True, optional=False):
        """ Create a new expression that matches the current
        expression and then a trait with the exact name given.

        e.g. ``t("child").t("age")`` matches ``child.age`` on an object,
        and is equivalent to ``t("child").then(t("age"))``

        Parameters
        ----------
        name : str
            Name of the trait to match.
        notify : boolean, optional
            Whether to notify for changes.
        optional : boolean, optional
            Whether this trait is optional on an object.

        Returns
        -------
        new_expression : Expression
        """
        return self._new_with_branches(
            nodes=[NamedTraitListener(name, notify, optional)],
        )

    def list_items(self, notify=True, optional=False):
        """ Create a new expression for observing items inside a list.

        e.g. ``t("containers").list_items()`` for observing to mutations
        to a list named ``containers``.

        e.g. ``t("containers").list_items().t("value")`` for observing
        the trait ``value`` on any items in the list ``containers``.

        Parameters
        ----------
        notify : boolean, optional
            Whether to notify for changes.
        optional : booleal, optional
            Whether to ignore this if the upstream object is not a list.

        Returns
        -------
        new_expression : Expression
        """
        return self._new_with_branches(
            nodes=[ListItemListener(notify=notify, optional=optional)],
        )

    def dict_items(self, notify=True, optional=False):
        """ Create a new expression for observing items inside a dict.

        An expression with ``dict_items`` cannot be further extended
        as it is ambiguous which of the keys and values are being
        observed.

        Parameters
        ----------
        notify : boolean, optional
            Whether to notify for changes.
        optional : booleal, optional
            Whether to ignore this if the upstream object is not a dict.

        Returns
        -------
        new_expression : Expression
        """
        # Should be similar to list_items but for dict
        return self._new_with_branches(
            nodes=[DictItemListener(notify=notify, optional=optional)],
        )

    def set_items(self, notify=True, optional=False):
        """ Create a new expression for observing items inside a set.

        Parameters
        ----------
        notify : boolean, optional
            Whether to notify for changes.
        optional : booleal, optional
            Whether to ignore this if the upstream object is not a set.

        Returns
        -------
        new_expression : Expression
        """
        # Should be similar to list_items but for set
        return self._new_with_branches(
            nodes=[SetItemListener(notify=notify, optional=optional)],
        )

    def items(self, notify=True):
        """ Create a new expression for observing items in a list or
        a dict or a set.

        If the type of the collection is known, it will be more efficient
        to use the type specific implementation, namely, ``list_items``,
        ``dict_items`` and ``set_items``.

        Parameters
        ----------
        notify : boolean, optional
            Whether to notify for changes.

        Returns
        -------
        new_expression : Expression
        """
        return (
            self.list_items(notify=notify, optional=True)
            | self.dict_items(notify=notify, optional=True)
            | self.set_items(notify=notify, optional=True)
        )

    def filter_(self, filter, notify=True):
        """ Create a new expression that matches traits using the
        given filter after the current expression returns a match.

        Parameters
        ----------
        filter : callable(str, TraitType) -> boolean
            Return true if a trait is to be observed.
            Note that if this expression is used for removing
            observers, the given filter must compare equally to the
            filter used for putting up the observer in the first place.
        notify : boolean, optional
            Whether to notify for changes.

        Returns
        -------
        new_expression : Expression
        """
        return self._new_with_branches(
            nodes=[_FilteredTraitListener(notify=notify, filter=filter)],
        )

    def anytrait(self, notify=True):
        """ Create a new expression that matches anytrait after
        the current expresion returns a match.

        e.g. ``t("child").anytrait()`` with match anytrait on
        the trait ``child`` on a given object, such as ``child.age``,
        ``child.name``, ``child.mother`` and so on.

        Equivalent to ``filter(filter=anytrait_filter)`` where
        ``anyrait_filter`` always returns True.

        Parameters
        ----------
        notify : boolean, optional
            Whether to notify for changes.

        Returns
        -------
        new_expression : Expression
        """
        return self.filter_(filter=_anytrait_filter, notify=notify)

    def metadata(self, metadata_name, value=_is_not_none, notify=True):
        """ Return a new expression that matches traits based on
        metadata filters, after the current expression matches.

        e.g. ``metadata("age", filter=lambda value: value is not None)``
        matches traits with metadata whose values are not None.

        Parameters
        ----------
        metadata_name : str
            Name of the metadata to filter traits with.
        value : callable(value) -> boolean
            Return true if a trait is to be observed.
            ``value`` is the value of the metadata, if defined on a trait.
        notify : boolean, optional
            Whether to notify for changes.

        Returns
        -------
        new_expression : Expression

        See also
        --------
        HasTraits.traits
        """
        # Something that makes use of
        # HasTraits.traits(**{metadata_name: filter})
        return self._new_with_branches(
            nodes=[
                MetadataListener(
                    metadata_name=metadata_name, value=value, notify=notify),
            ]
        )

    def _new_with_branches(self, nodes):
        expression = self.copy()
        expression._levels.append(set(nodes))
        return expression

    def copy(self):
        """ Return a shallow copy of this expression."""
        expression = Expression()
        expression._levels = self._levels.copy()
        if self._prior_expression is not None:
            expression._prior_expression = self._prior_expression.copy()
        return expression

    def info(self):
        """ Return a list of user-friendly texts containing descriptive information
        about this expression.
        """
        infos = []
        for path in self.as_paths():
            infos.append(" ---- Path ---- ")
            infos.extend(path.info())
        return infos

    def print(self):
        """ Print the descriptive information for this expression.
        """
        print(*self.info(), sep="\n")


def _anytrait_filter(name, trait):
    """ Filter for matching any traits."""
    return True


def _create_paths(expression, paths=None):
    """ Create ListenerPaths from a given expression.

    Parameters
    ----------
    expression : Expression
    paths : collection of ListenerPath
        Leaf paths to be added.
        Needed when this function is called recursively.

    Returns
    -------
    paths : list of ListenerPath
        New paths
    """
    if paths is None:
        paths = []

    for bnodes in expression._levels[::-1]:
        if not bnodes:
            raise RuntimeError("Unexpectedly empty.")

        bpaths = [ListenerPath(node=node) for node in bnodes]
        for path in bpaths:
            path.branches = path.branches.union(paths)

        paths = bpaths

    if expression._prior_expression is not None:
        paths = expression._prior_expression._create_paths(
            paths=paths,
        )
    return paths


class _SeriesExpression:
    """ Container of Expression for joining expressions in series.
    Used internally in this module.
    """

    def __init__(self, expressions):
        self.expressions = expressions.copy()

    def copy(self):
        return _SeriesExpression(self.expressions)

    def _root_nodes(self):
        """ Return the root nodes of this expression.

        Returns
        -------
        bnodes : set(BaseListener)
            Nodes for branches.
        cnodes : set(BasListener)
            Nodes for cycles.

        Raises
        ------
        ValueError
            If no root nodes are found.
        """
        for expr in self.expressions:
            try:
                return expr._root_nodes()
            except ValueError:
                continue
        else:
            raise ValueError("No root nodes found.")

    def _create_paths(self, paths):
        """
        Create new ListenerPath(s) from the joined expressions.

        Parameters
        ----------
        paths : collection of ListenerPath
            Leaf paths to be added.
            Needed when this function is called recursively.

        Returns
        -------
        paths : list of ListenerPath
            New paths
        """
        for expr in self.expressions[::-1]:
            paths = _create_paths(
                expr,
                paths=paths,
            )
        return paths


class _ParallelExpression:
    """ Container of Expression for joining expressions in parallel.
    Used internally in this module.
    """

    def __init__(self, expressions):
        self.expressions = expressions.copy()

    def copy(self):
        return _ParallelExpression(self.expressions)

    def _root_nodes(self):
        """ Return the root branched nodes of this expression.

        Returns
        -------
        bnodes : set(BaseListener)
            Nodes for branches.

        Raises
        ------
        ValueError
            If no root nodes are found.
        """
        bnodes = set()
        for expr in self.expressions:
            nodes = expr._root_nodes()
            bnodes |= nodes

        if not bnodes:
            raise ValueError("No root nodes")

        return bnodes

    def _create_paths(self, paths):
        """
        Create new ListenerPath(s) from the joined expressions.

        Parameters
        ----------
        paths : collection of ListenerPath
            Leaf paths to be added.
            Needed when this function is called recursively.

        Returns
        -------
        paths : list of ListenerPath
            New paths
        """
        new_paths = []
        for expr in self.expressions:
            or_paths = _create_paths(
                expr,
                paths=paths,
            )
            new_paths.extend(or_paths)
        return new_paths


# Define top-level functions

def _as_top_level(func):

    def new_func(*args, **kwargs):
        return func(Expression(), *args, **kwargs)

    # Recreate the docstring with the appropriate arguments
    update_wrapper(
        new_func,
        getattr(Expression(), func.__name__)
    )
    new_func.__module__ = __name__
    return new_func


t = _as_top_level(Expression.t)

items = _as_top_level(Expression.items)

list_items = _as_top_level(Expression.list_items)

dict_items = _as_top_level(Expression.dict_items)

set_items = _as_top_level(Expression.set_items)

metadata = _as_top_level(Expression.metadata)


def join_(*expressions):
    """ Convenient function for joining many expressions
    using ``Expression.then``
    """
    return reduce(lambda e1, e2: e1.then(e2), expressions)