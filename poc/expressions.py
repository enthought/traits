
import copy
from itertools import chain
from poc.observe import (
    ListenerPath,
    NamedTraitListener,
    _FilteredTraitListener,
    ListItemListener,
)


def _anytrait_filter(name, trait):
    return True


def _add_paths(path, others, seen=None):

    if seen is None:
        seen = []
    else:
        seen = seen.copy()
    seen.append(path)

    def is_seen(p):
        return any(p2 is p for p2 in seen)

    unseen_paths = []
    for p in path.nexts:
        if not is_seen(p):
            unseen_paths.append(p)

    for unseen in unseen_paths:
        _add_paths(unseen, others, seen=seen)
    if not unseen_paths:
        path.nexts.extend(others)


class Expression:

    def __init__(self, paths=None):
        self._paths = [] if paths is None else paths

    def as_paths(self):
        return self._paths

    def _new_with_paths(self, others):
        if not self._paths:
            return type(self)(paths=copy.deepcopy(others))

        paths = copy.deepcopy(self._paths)
        for path in paths:
            _add_paths(path, copy.deepcopy(others))
        return type(self)(paths=paths)

    def t(self, name, notify=True, optional=False):
        return self._new_with_paths([
            ListenerPath(
                node=NamedTraitListener(name, notify, optional),
                nexts=[]
            )
        ])

    def list_items(self, notify=True):
        return self._new_with_paths([
            ListenerPath(
                node=ListItemListener(notify=notify),
                nexts=[]
            )
        ])

    def dict_items(self, notify=True):
        pass

    def set_items(self, notify=True):
        pass

    def items(self, notify=True):
        # equivalent to list_items or dict_items or set_items
        # this complicates the code path, so maybe not introduce this?
        pass

    def anytrait(self, notify=True):
        return self._new_with_paths([
            ListenerPath(
                node=_FilteredTraitListener(
                    notify=notify,
                    filter=_anytrait_filter,
                ),
                nexts=[]
            )
        ])

    def __or__(self, expression):
        return Expression(
            paths=self.as_paths() + expression.as_paths()
        )

    def __call__(self, expression):
        return self._new_with_paths(expression.as_paths())

    def recursive(self, name, notify=True, optional=True):
        node = NamedTraitListener(
            name=name, notify=notify, optional=optional,
        )
        path = ListenerPath(node=node, nexts=[])
        path.nexts.append(path)
        return self._new_with_paths([path])


def t(name, notify=True, optional=False):
    return Expression().t(name=name, notify=notify, optional=optional)


def parse(text):
    return Expression()


def anytrait(notify=True):
    return Expression().anytrait(notify=notify)
