from functools import reduce
import operator
import os
from lark import Lark

import poc.expressions as _expr_module

HERE = os.path.dirname(__file__)


with open(os.path.join(HERE, "grammar.lark"), "r") as p:
    grammar = p.read()

parser = Lark(grammar, parser="lalr")

#: Token annotation for a name (a trait name, or a metadata name, etc.)
_NAME_TOKEN = "NAME"


def handle_series(trees, default_notifies):
    return _expr_module.join_(
        *(handle_tree(tree, default_notifies=default_notifies) for tree in trees)
    )


def handle_parallel(trees, default_notifies):
    return reduce(
        operator.or_,
        (handle_tree(tree, default_notifies=default_notifies) for tree in trees)
    )


def handle_notify(trees, default_notifies):
    default_notifies.append(True)
    # Expect a single child as element
    tree, = trees
    expression = handle_tree(tree, default_notifies=default_notifies)
    notify = default_notifies.pop()
    if notify is not True:
        raise RuntimeError("Default notify flag unexpectedly changed.")
    return expression


def handle_quiet(trees, default_notifies):
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
    tree, = trees
    return handle_tree(tree, default_notifies=default_notifies)


def handle_trait(trees, default_notifies):
    token, = trees
    # sanity check
    if token.type != _NAME_TOKEN:
        raise ValueError("Unexpected token: {!r}".format(token))
    name = str(token)
    notify = default_notifies[-1]
    return _expr_module.t(name, notify=notify)


def handle_metadata(trees, default_notifies):
    token, = trees
    # sanity check
    if token.type != _NAME_TOKEN:
        raise ValueError("Unexpected token: {!r}".format(token))
    metadata_name = str(token)
    notify = default_notifies[-1]
    return _expr_module.metadata(metadata_name, notify=notify)


def handle_recursed(trees, default_notifies):
    tree, = trees
    return _expr_module.recursive(
        handle_tree(tree, default_notifies=default_notifies)
    )


def handle_items(trees, default_notifies):
    if trees:
        # Nothing should be wrapped in items
        raise ValueError("Unexpected tree: {!r}".format(trees))
    notify = default_notifies[-1]
    return reduce(
        operator.or_,
        (
            _expr_module.t("items", notify=notify, optional=True),
            _expr_module.list_items(notify=notify, optional=True),
            _expr_module.dict_items(notify=notify, optional=True),
            _expr_module.set_items(notify=notify, optional=True),
        )
    )


def handle_tree(tree, default_notifies=None):
    if default_notifies is None:
        default_notifies = [True]

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
    tree = parser.parse(text)
    return handle_tree(tree)
