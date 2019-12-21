#  Copyright (c) 2005-19, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!

import copy
import operator
from weakref import ref

from .trait_base import class_of, Undefined
from .trait_errors import TraitError


class TraitListEvent(object):
    """ An object reporting in-place changes to a traits list.
    """

    def __init__(self, index=0, removed=None, added=None):
        """
        Parameters
        ----------
        index : int
            The location of the first change in the list.
        added : list
            The list of values added to the list.
        removed : list
            The list of values removed from the list.
        """
        self.index = index

        if removed is None:
            removed = []
        self.removed = removed

        if added is None:
            added = []
        self.added = added


class TraitList(list):
    """ A subclass of list that notifies listeners of changes. """

    def validate(self, index, removed, value):
        if self.validator is None:
            return value
        else:
            return self.validator(self, index, removed, value)

    def notify(self, index, removed, added):
        if removed == added:
            return
        for notifier in self.notifiers:
            notifier(self, index, removed, added)

    def __deepcopy__(self, memo):
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        # notifiers are transient and should not be copied
        memo[id_self] = result = TraitList(
            [copy.deepcopy(x, memo) for x in self],
            validator=copy.deepcopy(self.validator, memo),
            notifiers=[],
        )

        return result

    def __getstate__(self):
        result = self.__dict__.copy()
        # notifiers are transient and should not be persisted
        result.pop("notifiers", None)
        return result

    def __setstate__(self, state):
        state['notifiers'] = []
        self.__dict__.update(state)

    def __init__(self, value=(), *, validator=None, notifiers=()):
        self.validator = validator
        self.notifiers = list(notifiers)
        value = self.validate(slice(0, 0), [], value)
        super().__init__(value)

    def __setitem__(self, index, value):
        removed = self._get_removed(index)
        if isinstance(index, slice):
            if len(removed) != len(value) and index.step not in {1, None}:
                # will fail with ValueError
                super().__setitem__(index, value)

            added = self.validate(index, removed, value)
            norm_index = self._normalize_slice(index)
            super().__setitem__(index, added)
        else:
            added = self.validate(index, removed, value)
            norm_index = self._normalize_index(index)
            super().__setitem__(index, added)

        self.notify(norm_index, removed, added)

    def __delitem__(self, index):
        removed = self._get_removed(index)
        if isinstance(index, slice):
            added = self.validate(index, removed, [])
            norm_index = self._normalize_slice(index)
            super().__delitem__(index)
        else:
            added = self.validate(index, removed, Undefined)
            norm_index = self._normalize_index(index)
            super().__delitem__(index)

        self.notify(norm_index, removed, added)

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __imul__(self, count):
        if count > 1:
            self.extend(self * (count-1))
        elif count == 0:
            self[:] = []
        return self

    def append(self, value):
        index = len(self)
        removed = Undefined
        added = self.validate(index, removed, value)

        super().append(added)

        self.notify(index, removed, added)

    def extend(self, value):
        index = slice(len(self), len(self))
        removed = []
        added = self.validate(index, removed, value)

        super().extend(added)

        self.notify(index, removed, added)

    def insert(self, index, value):
        removed = Undefined
        added = self.validate(index, removed, value)
        norm_index = self._normalize_index(index)

        super().insert(index, added)

        self.notify(norm_index, removed, added)

    def pop(self, *args):
        if len(args) >= 1:
            index = args[0]
        else:
            index = -1
        removed = self._get_removed(index)
        added = self.validate(index, removed, Undefined)
        norm_index = self._normalize_index(index)

        removed = super().pop(*args)

        self.notify(norm_index, removed, added)

        return removed

    def remove(self, value):
        index = self.index(value)
        added = self.validate(index, value, Undefined)

        super().remove(value)

        self.notify(index, value, added)

    def sort(self, *, key=None, reverse=False):
        self[:] = sorted(self, key=key, reverse=reverse)

    def reversed(self):
        self[:] = self[::-1]

    def _get_removed(self, index):
        try:
            return self[index]
        except Exception:
            if isinstance(index, slice):
                return []
            else:
                return Undefined

    def _normalize_index(self, index):
        index = operator.index(index)
        if index < 0:
            return max(0, len(self) + index)
        else:
            return min(len(self), index)

    def _normalize_slice(self, index):
        if index.step is None or index.step > 0:
            if index.start is not None:
                start = self._normalize_index(index.start)
            else:
                start = 0
            if index.stop is not None:
                stop = self._normalize_index(index.stop)
            else:
                stop = len(self)
        else:
            if index.start is not None:
                start = self._normalize_index(index.start)
            else:
                start = len(self)
            if index.stop is not None:
                stop = self._normalize_index(index.stop)
            else:
                stop = 0

        return slice(start, stop, index.step)

    def _clip(self, index):
        return min(max(index, 0), len(self))

    def object(self):
        """ Stub method to pass persistence tests. """
        # XXX fix persistence tests to not introspect this!
        return None


class TraitListObject(TraitList):

    def __init__(self, trait, object, name, value, *, notifiers=[]):
        helper = TraitListObjectHelper(trait, object, name)
        super().__init__(
            value,
            validator=helper.validator,
            notifiers=[helper.notifier] + notifiers
        )


class TraitListObjectHelper:

    def __init__(self, trait, object, name):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

    def validator(self, trait_list, index, removed, value):
        object = self.object()
        trait = self.trait
        if object is None or trait is None:
            return value

        # check that length is within bounds
        if isinstance(index, slice):
            new_len = len(trait_list) - len(removed) + len(value)
        else:
            new_len = len(trait_list)
            if removed is Undefined:
                new_len += 1
            if value is Undefined:
                new_len -= 1
        if not trait.minlen <= new_len <= trait.maxlen:
            raise TraitError(
                "The '%s' trait of %s instance must be %s, "
                "but you attempted to change its length to %d element%s."
                % (
                    self.name,
                    class_of(object),
                    self.trait.full_info(object, self.name, Undefined),
                    new_len,
                    "s"[new_len == 1 :],
                )
            )

        # validate the new value(s)
        validate = trait.item_trait.handler.validate
        if validate is None:
            return value

        try:
            if isinstance(index, slice):
                return [
                    validate(object, self.name, item) for item in value
                ]
            elif value is Undefined:
                return Undefined
            else:
                return validate(object, self.name, value)
        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def notifier(self, trait_list, index, removed, added):
        if not hasattr(self, "trait") or self.trait is None or self.name_items is None:
            return

        object = self.object()
        if object is None:
            return

        # bug-for-bug conversion of parameters to TraitListEvent
        if isinstance(index, slice):
            if index.step in {1, None}:
                index = min(index.start, index.stop)
            else:
                if added:
                    added = [added]
                removed = [removed]
        else:
            if removed is Undefined:
                removed = []
            else:
                removed = [removed]
            if added is Undefined:
                added = []
            else:
                added = [added]
        event = TraitListEvent(index, removed, added)
        items_event = self.trait.items_event()
        if items_event is None:
            items_event = self.trait.items_event()

        object.trait_items_event(self.name_items, event, items_event)

    def __deepcopy__(self, memo):
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitListObjectHelper(
            self.trait,
            lambda: None,
            self.name,
        )

        return result

    def __getstate__(self):
        result = self.__dict__.copy()
        result.pop("object", None)
        result.pop("trait", None)

        return result

    def __setstate__(self, state):
        name = state.setdefault("name", "")
        object = state.pop("object", None)
        if object is not None:
            state['object'] = ref(object)
            trait = self.object()._trait(name, 0)
            if trait is not None:
                state['trait'] = trait.handler
        else:
            state['object'] = lambda: None
            state['trait'] = None

        self.__dict__.update(state)
