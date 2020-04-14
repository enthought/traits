"""
Parse mini-language to expressions.
"""
import copy
from functools import reduce
from itertools import chain
import operator

import pyparsing as pp

from poc import expressions

LBRACK = pp.Suppress("[").setName("[")
RBRACK = pp.Suppress("]").setName("]")
COMMA = pp.Suppress(",")
DOT = pp.Word(".").setParseAction(lambda: True).setResultsName("notify")
COLON = pp.Word(":").setParseAction(lambda: False).setResultsName("notify")
LPAR = pp.Suppress("(")
RPAR = pp.Suppress(")")
ASTERISK = pp.Suppress("*")

NAME = pp.Word(pp.alphas, pp.alphanums + "_")
ITEMS = pp.Keyword("items")

NOTIFY = pp.Optional(pp.Or([DOT, COLON]), default=True)

# Match "name"

def parse_name(s, loc, toks):
    name, = toks.asList()
    return expressions.t(name=name)

name = NAME.copy().setName("name")
name = name.setParseAction(parse_name)

# Match the keyword "items"

def parse_items(s, loc, toks):
    return (
        expressions.t("items")
        | expressions.items()
    )

items = ITEMS.copy().setName("items")
items = items.setParseAction(parse_items)

# Match either plain name or the keyword items
items_or_name = (items | name).setName("items | name")

# Match "attr1.attr2", "attr1:attr2.attr3" and so
def join_action(s, loc, toks):

    if (len(toks) // 2) * 2 == len(toks):
        raise ValueError("Unexpected match: {!r}".format(s))

    toks.append(True)
    exprs = (
        last(expression, notify)
        for expression, notify in zip(toks[::2], toks[1::2])
    )

    return expressions.join_(*exprs)


expr = pp.Forward().setName("expr")

joined = (expr + pp.ZeroOrMore((DOT ^ COLON) + expr))
joined = joined.setParseAction(join_action)


# Match "attr1,attr2.attr3"
def or_action(s, loc, toks):
    expressions = chain.from_iterable(toks)
    return reduce(operator.or_, expressions)

or_expr = pp.delimitedList(pp.Group(joined))
or_expr = or_expr.setParseAction(or_action)


# Group using square brackets

def parse_group(s, loc, toks):
    expression, = toks.asList()
    return expression

grouped = LBRACK + or_expr + RBRACK
grouped = grouped.setParseAction(parse_group)


# Recursion with '*'

def parse_recurse(s, loc, toks):
    expression, = toks.asList()
    return expressions.recursive(expression)

recursed = ((items_or_name ^ grouped) + ASTERISK).setParseAction(parse_recurse)

expr <<= recursed ^ grouped ^ items_or_name

parser = or_expr


def parse(text):
    expression, = parser.parseString(text, parseAll=True).asList()
    return expression


#: FIXME
#: Replace this hack with a different parsing workflow such that
#: expressions are created with the correct notify flag at the
#: beginning.
def last(expression, notify, _memo=None):
    """ Return a new expression with the most nested leaf node's notify
    flag replaced with the new value.

    Parameters
    ----------
    notify : boolean

    Returns
    -------
    new_expression : Expressions
    """
    new = expression.copy()

    if _memo is None:
        _memo = {}

    def new_node(node, _memo):
        if node.notify is notify:
            return node
        if id(node) in _memo:
            return _memo[id(node)]
        node2 = copy.copy(node)
        node2.notify = notify
        _memo[id(node)] = node2
        return node2

    if new._levels:
        for i, (bnodes, cnodes) in enumerate(new._levels[::-1], start=1):
            if bnodes:
                bnodes, cnodes = new._levels[-1]
                new_bnodes = set(new_node(node, _memo) for node in bnodes)
                new._levels[-i] = (new_bnodes, cnodes)
                # Refresh the cycles.
                for i in range(len(new._levels) - i + 1, len(new._levels)):
                    bnodes, cnodes = new._levels[i]
                    new._levels[i] = (
                        bnodes,
                        set(_memo.get(id(node), node) for node in cnodes),
                    )
                return new

    # The leaf branches come from prior expressions...
    if new._prior_expressions is not None:
        prior_type, exprs = new._prior_expressions
        if prior_type is expressions._JOIN:
            exprs = exprs.copy()
            exprs[-1] = last(exprs[-1], notify, _memo)
        elif prior_type is expressions._OR:
            exprs = [
                last(expr, notify, _memo) for expr in exprs
            ]
        else:
            raise ValueError("Unknown prior expressions.")
        new._prior_expressions = (prior_type, exprs)

    # Refresh the cycles (if any)
    new._levels = [
        (
            bnodes,
            set(_memo.get(id(node), node) for node in cnodes),
        )
        for bnodes, cnodes in new._levels
    ]
    return new
