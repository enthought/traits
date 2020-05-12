# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import contextlib
from functools import reduce
import operator

import traits.observers.expression as _expr_module
from traits.observers._generated_parser import (
    Lark_StandAlone as _Lark_StandAlone
)

_LARK_PARSER = _Lark_StandAlone()

#: Token annotation for a name (a trait name, or a metadata name, etc.)
_NAME_TOKEN = "NAME"


def _handle_series(trees, default_notifies):
    """ Handle expressions joined in series using "." or ":" connectors.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "series" rule.
        It should contain one or more items.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    expressions = (
        _handle_tree(tree, default_notifies=default_notifies)
        for tree in trees
    )
    return _expr_module.join_(*expressions)


def _handle_parallel(trees, default_notifies):
    """ Handle expressions joined in parallel using "," connectors.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "parallel" rule.
        It should contain one or more items.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    expressions = (
        _handle_tree(tree, default_notifies=default_notifies) for tree in trees
    )
    return reduce(operator.or_, expressions)


@contextlib.contextmanager
def _notify_flag(default_notifies, value):
    """ Context manager to push the notify to the given stack.
    Upon exiting the context, pop the flag out of the stack.

    Parameters
    ----------
    default_notifies : list of boolean
        The notify flag stack.
    value : boolean
        Notify flag to push.
    """
    default_notifies.append(value)
    try:
        yield
    finally:
        notify = default_notifies.pop()
        if notify is not value:
            raise RuntimeError("Default notify flag unexpectedly changed.")


def _handle_notify(trees, default_notifies):
    """ Handle trees wrapped with the notify flag set to True,
    indicated by the existence of "." suffix to an element.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "notify" rule.
        It contains only one item.
    default_notifies : list of boolean
        The notify flag stack.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    with _notify_flag(default_notifies, True):
        return _handle_last(trees, default_notifies=default_notifies)


def _handle_quiet(trees, default_notifies):
    """ Handle trees wrapped with the notify flag set to True,
    indicated by the existence of ":" suffix to an element.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "quiet" rule.
        It contains only one item.
    default_notifies : list of boolean
        The notify flag stack.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    with _notify_flag(default_notifies, False):
        return _handle_last(trees, default_notifies=default_notifies)


def _handle_last(trees, default_notifies):
    """ Handle trees when the notify is not immediately specified
    as a suffix. The last notify flag will be used.

    e.g. In "a.[b,c]:.d", the element "b" should receive a notify flag
    set to false, which is set after a parallel group is defined.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "last" rule.
        It contains only one item.
    default_notifies : list of boolean
        The notify flag stack.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    tree, = trees
    return _handle_tree(tree, default_notifies=default_notifies)


def _handle_trait(trees, default_notifies):
    """ Handle an element for a named trait.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "trait" rule.
        It contains only one item.
    default_notifies : list of boolean
        The notify flag stack.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    token, = trees
    # sanity check
    if token.type != _NAME_TOKEN:
        raise ValueError("Unexpected token: {!r}".format(token))
    name = token.value
    notify = default_notifies[-1]
    return _expr_module.trait(name, notify=notify)


def _handle_metadata(trees, default_notifies):
    """ Handle an element for filtering existing metadata.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "metadata" rule.
        It contains only one item.
    default_notifies : list of boolean
        The notify flag stack.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    raise NotImplementedError("metadata is not yet implemeneted.")


def _handle_items(trees, default_notifies):
    """ Handle keyword "items".

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "items" rule.
        It should be empty.
    default_notifies : list of boolean
        The notify flag stack.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    raise NotImplementedError("items is not yet implemeneted.")


def _handle_tree(tree, default_notifies=None):
    """ Handle a tree using the specified rule.

    Parameters
    ----------
    tree : lark.tree.Tree
        Tree to be converted to an Expression.
    default_notifies : list of boolean
        The notify flag stack.
        The last item is the current notify flag.
        See handlers for "notify" and "quiet", which
        push and pop a notify flag to this stack.

    Returns
    -------
    expression: traits.observers.expressions.Expression
    """
    if default_notifies is None:
        default_notifies = [True]

    # All handlers must be callable
    # with the signature (list of Tree, default_notifies)
    handlers = {
        "series": _handle_series,
        "parallel": _handle_parallel,
        "notify": _handle_notify,
        "quiet": _handle_quiet,
        "last": _handle_last,
        "trait": _handle_trait,
        "metadata": _handle_metadata,
        "items": _handle_items,
    }
    return handlers[tree.data](
        tree.children, default_notifies=default_notifies)


def parse(text):
    """ Top-level function for parsing user's text to an Expression.

    Parameters
    ----------
    text : str
        Text to be parsed.

    Returns
    -------
    expression : traits.observers.expressions.Expression
    """
    tree = _LARK_PARSER.parse(text)
    return _handle_tree(tree)
