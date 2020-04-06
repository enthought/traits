
from poc.observe import (
    ListenerPath,
    NamedTraitListener,
    _FilteredTraitListener,
    ListItemListener,
)


def observe(object, expression, handler):
    # ``observe`` replaces ``on_trait_change``.
    # ``expression`` replaces ``name`` in ``on_trait_change``.
    # This is an example implementation to demonstrate
    # how the Expression is used. This will fail because
    # ``_observe`` is not implemented here.
    for path in expression.as_paths():
        _observe(object=object, path=path, handler=handler)  # noqa: F821


def _anytrait_filter(name, trait):
    """ Filter for matching any traits."""
    return True


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
        # ``_levels`` is a list of list of ``ListenerPath`` for
        # representing each level of "branching".
        # It is used for constructing a new list of ``ListenerPath``
        # in ``as_paths``.
        # The first item represents the level at the roots.
        # The last item represents the most nested level.
        # The number of ``ListenerPath`` in the first item of
        # this list is the number of rooted trees represented
        # by this ``Expression``.
        # e.g. ``t("name") | t("age")`` is translated to
        # two independent rooted trees.
        self._levels = []

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
        new._levels = [
            self.as_paths() + expression.as_paths()
        ]
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
        return self._new_with_paths(expression.as_paths())

    def recursive(self, expression):
        """ Create a new expression by adding a recursive path to
        this expression.

        e.g. ``t("root").recursive(t("left") | t("left")).t("value")``
        will match ``root.left.value``, ``root.left.left.value``,
        ``root.left.right.left.value`` and so on.

        Parameters
        ----------
        expression : Expression

        Returns
        -------
        new_expression : Expression
        """
        others = expression.as_paths()
        for other in others:
            other.nexts.update(others)
        return self._new_with_paths(others)

    def as_paths(self):
        """ Return the list of ListenerPath for the observer.
        """
        if not self._levels:
            return []

        inner_paths = self._levels[-1].copy()
        for outer_paths in self._levels[::-1][1:]:
            new_paths = []
            for outer_path in outer_paths:
                path = ListenerPath(
                    node=outer_path.node,
                    nexts=outer_path.nexts.union(inner_paths),
                )
                new_paths.append(path)
            inner_paths = new_paths
        return inner_paths

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
        return self._new_with_paths([
            ListenerPath(
                node=NamedTraitListener(name, notify, optional),
                nexts=[]
            )
        ])

    def list_items(self, notify=True):
        """ Create a new expression for observing items inside a list.

        e.g. ``t("containers").list_items()`` for observing to mutations
        to a list named ``containers``.

        e.g. ``t("containers").list_items().t("value")`` for observing
        the trait ``value`` on any items in the list ``containers``.

        Parameters
        ----------
        notify : boolean, optional
            Whether to notify for changes.

        Returns
        -------
        new_expression : Expression
        """
        return self._new_with_paths([
            ListenerPath(
                node=ListItemListener(notify=notify),
                nexts=[]
            )
        ])

    def dict_items(self, notify=True):
        # Should be similar to list_items but for dict
        raise NotImplementedError()

    def set_items(self, notify=True):
        # Should be similar to list_items but for set
        raise NotImplementedError()

    def items(self, notify=True):
        # this complicates the code path, so maybe not introduce this?
        return (
            self.list_items(notify=notify)
            | self.dict_items(notify=notify)
            | self.set_items(notify=notify)
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
        return self._new_with_paths([
            ListenerPath(
                node=_FilteredTraitListener(
                    notify=notify,
                    filter=filter,
                ),
                nexts=[]
            )
        ])

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

    def metadata(self, metadata_name, filter, notify=True):
        """ Return a new expression that matches traits based on
        metadata filters, after the current expression matches.

        e.g. ``metadata("age", filter=lambda value: value is not None)``
        matches traits with metadata whose values are not None.

        Parameters
        ----------
        metadata_name : str
            Name of the metadata to filter traits with.
        filter : callable(value) -> boolean
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
        raise NotImplementedError()

    def _new_with_paths(self, others):
        expression = Expression()
        expression._levels = self._levels + [others]
        return expression


def t(name, notify=True, optional=False):
    """ Create a new expression for matching a trait with the exact name
    given.

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
    expression : Expression
    """
    return Expression().t(name=name, notify=notify, optional=optional)


def anytrait(notify=True):
    """ Create a new expression for matching anytrait on an object.

    Parameters
    ----------
    notify : boolean, optional
        Whether to notify for changes.

    Returns
    -------
    expression : Expression
    """
    return Expression().anytrait(notify=notify)


def filter_(filter, notify=True):
    """ Create a new expression for matching traits with a given
    filter.

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
    expression : Expression
    """
    return Expression().filter_(filter=filter, notify=notify)
