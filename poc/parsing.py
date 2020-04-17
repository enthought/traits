from functools import reduce
import operator

import poc.expressions as _expr_module
from poc.generated_parser import Lark_StandAlone as _Lark_StandAlone

parser = _Lark_StandAlone()

#: Token annotation for a name (a trait name, or a metadata name, etc.)
_NAME_TOKEN = "NAME"


def handle_series(trees, default_notifies):
    """ Handle expressions joined in series using "." or ":" connectors.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "series" rule.
        It should contain one or more items.

    Returns
    -------
    expression : Expression
    """
    expressions = (
        handle_tree(tree, default_notifies=default_notifies)
        for tree in trees
    )
    return _expr_module.join_(*expressions)


def handle_parallel(trees, default_notifies):
    """ Handle expressions joined in parallel using "," connectors.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "parallel" rule.
        It should contain one or more items.

    Returns
    -------
    expression : Expression
    """
    expressions = (
        handle_tree(tree, default_notifies=default_notifies) for tree in trees
    )
    return reduce(operator.or_, expressions)


def handle_notify(trees, default_notifies):
    """ Handle trees wrapped with the notify flag set to True,
    indicated by the existence of "." suffix to an element.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "notify" rule.
        It contains only one item.

    Returns
    -------
    expression : Expression
    """
    default_notifies.append(True)
    # Expect a single child as element
    tree, = trees
    expression = handle_tree(tree, default_notifies=default_notifies)
    notify = default_notifies.pop()
    if notify is not True:
        raise RuntimeError("Default notify flag unexpectedly changed.")
    return expression


def handle_quiet(trees, default_notifies):
    """ Handle trees wrapped with the notify flag set to True,
    indicated by the existence of ":" suffix to an element.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "quiet" rule.
        It contains only one item.

    Returns
    -------
    expression : Expression
    """
    #: TODO: Refactor this, which is basically identical to handle_notify
    #: apart from the flag.
    default_notifies.append(False)
    # Expect a single child as element
    tree, = trees
    expression = handle_tree(tree, default_notifies=default_notifies)
    notify = default_notifies.pop()
    if notify is not False:
        raise RuntimeError("Default notify flag unexpectedly changed.")
    return expression


def handle_last(trees, default_notifies):
    """ Handle trees when the notify is not immediately specified
    as a suffix. The last notify flag will be used.

    e.g. In "a.[b,c]:.d", the element "b" should receive a notify flag
    set to false, which is set after a parallel group is defined.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "last" rule.
        It contains only one item.

    Returns
    -------
    expression : Expression
    """
    tree, = trees
    return handle_tree(tree, default_notifies=default_notifies)


def handle_trait(trees, default_notifies):
    """ Handle an element for a named trait.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "trait" rule.
        It contains only one item.

    Returns
    -------
    expression : Expression
    """
    token, = trees
    # sanity check
    if token.type != _NAME_TOKEN:
        raise ValueError("Unexpected token: {!r}".format(token))
    name = token.value
    notify = default_notifies[-1]
    return _expr_module.trait(name, notify=notify)


def handle_metadata(trees, default_notifies):
    """ Handle an element for filtering existing metadata.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "metadata" rule.
        It contains only one item.

    Returns
    -------
    expression : Expression
    """
    token, = trees
    # sanity check
    if token.type != _NAME_TOKEN:
        raise ValueError("Unexpected token: {!r}".format(token))
    metadata_name = token.value
    notify = default_notifies[-1]
    return _expr_module.metadata(metadata_name, notify=notify)


def handle_recursed(trees, default_notifies):
    """ Handle trees to be wrapped with recursion.

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "recursed" rule.
        There should be only one item.

    Returns
    -------
    expression : Expression
    """
    tree, = trees
    return _expr_module.recursive(
        handle_tree(tree, default_notifies=default_notifies)
    )


def handle_items(trees, default_notifies):
    """ Handle keyword "items".

    Parameters
    ----------
    trees : list of lark.tree.Tree
        The children tree for the "items" rule.
        It should be empty.

    Returns
    -------
    expression : Expression
    """
    if trees:
        # Nothing should be wrapped in items
        raise ValueError("Unexpected tree: {!r}".format(trees))
    notify = default_notifies[-1]
    return reduce(
        operator.or_,
        (
            _expr_module.trait("items", notify=notify, optional=True),
            _expr_module.list_items(notify=notify, optional=True),
            _expr_module.dict_items(notify=notify, optional=True),
            _expr_module.set_items(notify=notify, optional=True),
        )
    )


def handle_tree(tree, default_notifies=None):
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
    expression: Expression
    """
    if default_notifies is None:
        default_notifies = [True]

    # All handlers must be callable
    # with the signature (list of Tree, default_notifies)
    handlers = {
        "series": handle_series,
        "parallel": handle_parallel,
        "recursed": handle_recursed,
        "notify": handle_notify,
        "quiet": handle_quiet,
        "last": handle_last,
        "trait": handle_trait,
        "metadata": handle_metadata,
        "items": handle_items,
    }
    return handlers[tree.data](tree.children, default_notifies=default_notifies)


def parse(text):
    """ Top-level function for parsing user's text to an Expression.

    Parameters
    ----------
    text : str
        Text to be parsed.

    Returns
    -------
    expression : Expression
    """
    tree = parser.parse(text)
    return handle_tree(tree)
