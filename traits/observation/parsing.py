# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from functools import lru_cache

from traits.observation import _generated_parser
import traits.observation.expression as expression_module


_LARK_PARSER = _generated_parser.Lark_StandAlone()


def _handle_series(trees, notify):
    """ Handle an expression of the form "a.b" or "a:b".

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "series" rule. It should always
        contain exactly three items.
    notify : bool
        True if the final target should notify, else False.

    Returns
    -------
    expression : ObserverExpression
    """
    left, connector, right = trees
    notify_left = connector.data == "notify"
    return _handle_tree(left, notify_left).then(_handle_tree(right, notify))


def _handle_parallel(trees, notify):
    """ Handle an expression of the form "a, b".

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "parallel" rule. It should always
        contain exactly two items.
    notify : bool
        True if the final target should notify, else False.

    Returns
    -------
    expression : ObserverExpression
    """
    left, right = trees
    return _handle_tree(left, notify) | _handle_tree(right, notify)


def _handle_trait(trees, notify):
    """ Handle an element for a named trait.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "trait" rule.
        It contains only one item.
    notify : bool
        True if the final target should notify, else False.

    Returns
    -------
    expression : ObserverExpression
    """
    token, = trees
    name = token.value
    return expression_module.trait(name, notify=notify)


def _handle_anytrait(trees, notify):
    """ Handle an anytrait element.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "trait" rule. This should be empty.
    notify : bool
        True if the final target should notify, else False.

    Returns
    -------
    expression : ObserverExpression
    """
    return expression_module.anytrait(notify=notify)


def _handle_metadata(trees, notify):
    """ Handle an element for filtering existing metadata.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "metadata" rule.
        It contains only one item.
    notify : bool
        True if the final target should notify, else False.

    Returns
    -------
    expression : ObserverExpression
    """
    token, = trees
    metadata_name = token.value
    return expression_module.metadata(metadata_name, notify=notify)


def _handle_items(trees, notify):
    """ Handle keyword "items".

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "items" rule.
        It should be empty.
    notify : bool
        True if the final target should notify, else False.

    Returns
    -------
    expression : ObserverExpression
    """
    if trees:
        # Nothing should be wrapped in items
        raise ValueError("Unexpected tree: {!r}".format(trees))

    return (
        expression_module.trait("items", notify=notify, optional=True)
        | expression_module.dict_items(notify=notify, optional=True)
        | expression_module.list_items(notify=notify, optional=True)
        | expression_module.set_items(notify=notify, optional=True)
    )


def _handle_tree(tree, notify):
    """ Handle a tree using the specified rule.

    Parameters
    ----------
    tree : lark.tree.Tree
        Tree to be converted to an ObserverExpression.
    notify : bool
        True if the final target should notify, else False.

    Returns
    -------
    expression: ObserverExpression
    """
    # All handlers must be callable
    # with the signature (list of Tree, notify)
    handlers = {
        "series": _handle_series,
        "series_terminal": _handle_series,
        "parallel": _handle_parallel,
        "parallel_terminal": _handle_parallel,
        "trait": _handle_trait,
        "metadata": _handle_metadata,
        "items": _handle_items,
        "anytrait": _handle_anytrait,
    }
    return handlers[tree.data](tree.children, notify)


@lru_cache(maxsize=expression_module._OBSERVER_EXPRESSION_CACHE_MAXSIZE)
def parse(text):
    """ Top-level function for parsing user's text to an ObserverExpression.

    Parameters
    ----------
    text : str
        Text to be parsed.

    Returns
    -------
    expression : ObserverExpression

    Raises
    ------
    ValueError
        If the text is not a valid observe expression.
    """
    try:
        tree = _LARK_PARSER.parse(text)
    except _generated_parser.LarkError as parser_exception:
        raise ValueError(f"Invalid expression: {text!r}") from parser_exception

    return _handle_tree(tree, notify=True)


@lru_cache(maxsize=expression_module._OBSERVER_EXPRESSION_CACHE_MAXSIZE)
def compile_str(text):
    """ Compile a mini-language string to a list of ObserverGraph objects.

    Parameters
    ----------
    text : str
        Text to be parsed.

    Returns
    -------
    list of ObserverGraph
    """
    return expression_module.compile_expr(parse(text))
