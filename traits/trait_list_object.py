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

        memo[id_self] = result = TraitList(
            [copy.deepcopy(x, memo) for x in self],
            validator=self.validator,
            notifiers=copy.copy(self.notifiers),
        )

        return result

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


class TraitListObject(TraitList):

    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"
        super().__init__(
            value,
            validator=self.validator,
            notifiers=[self._items_changed_notifier],
        )

    def validator(self, trait_list, index, removed, value):
        object = self.object()
        validate = self.trait.item_trait.handler.validate
        if object is None or validate is None:
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

    def validate(self, index, removed, added):
        if self.trait is None:
            return added
        if isinstance(index, slice):
            new_len = len(self) - len(removed) + len(added)
        else:
            new_len = len(self)
            if removed is Undefined:
                new_len += 1
            if added is Undefined:
                new_len -= 1
        if self.trait.minlen <= new_len <= self.trait.maxlen:
            return super().validate(index, removed, added)
        else:
            self.len_error(new_len)

    def len_error(self, len):
        raise TraitError(
            "The '%s' trait of %s instance must be %s, "
            "but you attempted to change its length to %d element%s."
            % (
                self.name,
                class_of(self.object()),
                self.trait.full_info(self.object(), self.name, Undefined),
                len,
                "s"[len == 1 :],
            )
        )

    def _items_changed_notifier(self, trait_list, index, removed, added):
        if self.trait is None or self.name_items is None:
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

        self._send_trait_items_event(
            self.name_items, event, self.trait.items_event()
        )

    def _send_trait_items_event(self, name, event, items_event=None):
        """ Send a TraitListEvent to the owning object if there is one.
        """
        object = self.object()
        if object is not None:
            if items_event is None and hasattr(self, "trait"):
                items_event = self.trait.items_event()
            object.trait_items_event(name, event, items_event)

    def __deepcopy__(self, memo):
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitListObject(
            self.trait,
            lambda: None,
            self.name,
            [copy.deepcopy(x, memo) for x in self],
        )

        return result

    def rename(self, name):
        trait = self.object()._trait(name, 0)
        if trait is not None:
            self.name = name
            self.trait = trait.handler

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

'''
class TraitListObject(list):
    """ A subclass of list that fires trait events when mutated. """

    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        # Do the validated 'setslice' assignment without raising an
        # 'items_changed' event:
        if trait.minlen <= len(value) <= trait.maxlen:
            try:
                validate = trait.item_trait.handler.validate
                if validate is not None:
                    value = [validate(object, name, val) for val in value]

                list.__setitem__(self, slice(0, 0), value)

                return

            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

        self.len_error(len(value))

    def _send_trait_items_event(self, name, event, items_event=None):
        """ Send a TraitListEvent to the owning object if there is one.
        """
        object = self.object()
        if object is not None:
            if items_event is None and hasattr(self, "trait"):
                items_event = self.trait.items_event()
            object.trait_items_event(name, event, items_event)

    def __deepcopy__(self, memo):
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitListObject(
            self.trait,
            lambda: None,
            self.name,
            [copy.deepcopy(x, memo) for x in self],
        )

        return result

    def __setitem__(self, key, value):
        self_trait = getattr(self, "trait", None)
        if self_trait is None:
            return list.__setitem__(self, key, value)
        try:
            removed = self[key]
        except Exception:
            removed = []
        try:
            object = self.object()
            validate = self.trait.item_trait.handler.validate
            name = self.name

            if isinstance(key, slice):
                values = value
                slice_len = len(removed)

                delta = len(values) - slice_len
                step = 1 if key.step is None else key.step
                if step != 1 and delta != 0:
                    raise ValueError(
                        "attempt to assign sequence of size %d to extended slice of size %d"
                        % (len(values), slice_len)
                    )
                newlen = len(self) + delta
                if not (self_trait.minlen <= newlen <= self_trait.maxlen):
                    self.len_error(newlen)
                    return

                if validate is not None:
                    values = [
                        validate(object, name, value) for value in values
                    ]
                value = values
                if step == 1:
                    # FIXME: Bug-for-bug compatibility with old __setslice__ code.
                    # In this case, we return a TraitListEvent with an
                    # index=key.start and the removed and added lists as they
                    # are.
                    index = 0 if key.start is None else key.start
                else:
                    # Otherwise, we have an extended slice which was handled,
                    # badly, by __setitem__ before. In this case, we return the
                    # removed and added lists wrapped in another list.
                    index = key
                    values = [values]
                    removed = [removed]
            else:
                if validate is not None:
                    value = validate(object, name, value)

                values = [value]
                removed = [removed]
                delta = 0

                index = len(self) + key if key < 0 else key

            list.__setitem__(self, key, value)
            if self.name_items is not None:
                if delta == 0:
                    try:
                        if removed == values:
                            return
                    except Exception:
                        # Treat incomparable values as equal:
                        pass
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed, values)
                )

        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def __delitem__(self, key):
        trait = getattr(self, "trait", None)
        if trait is None:
            return list.__delitem__(self, key)

        try:
            removed = self[key]
        except Exception:
            removed = []

        if isinstance(key, slice):
            slice_len = len(removed)
            delta = slice_len
            step = 1 if key.step is None else key.step
            if step == 1:
                # FIXME: See corresponding comment in __setitem__() for
                # explanation.
                index = 0 if key.start is None else key.start
            else:
                index = key
                removed = [removed]
        else:
            delta = 1
            index = len(self) + key + 1 if key < 0 else key
            removed = [removed]

        if not (trait.minlen <= (len(self) - delta)):
            self.len_error(len(self) - delta)
            return

        list.__delitem__(self, key)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitListEvent(index, removed)
            )

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __imul__(self, count):
        trait = getattr(self, "trait", None)
        if trait is None:
            return list.__imul__(self, count)

        original_len = len(self)

        if trait.minlen <= original_len * count <= trait.maxlen:
            if self.name_items is not None:
                removed = None if count else self[:]

            result = list.__imul__(self, count)

            if self.name_items is not None:
                added = self[original_len:] if count else None
                index = original_len if count else 0
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed, added)
                )

            return result
        else:
            self.len_error(original_len * count)

    def append(self, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            list.append(self, value)
            return

        if trait.minlen <= (len(self) + 1) <= trait.maxlen:
            try:
                validate = trait.item_trait.handler.validate
                object = self.object()
                if validate is not None:
                    value = validate(object, self.name, value)
                list.append(self, value)
                if self.name_items is not None:
                    self._send_trait_items_event(
                        self.name_items,
                        TraitListEvent(len(self) - 1, None, [value]),
                        trait.items_event(),
                    )
                return

            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

        self.len_error(len(self) + 1)

    def insert(self, index, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            return list.insert(self, index, value)
        if trait.minlen <= (len(self) + 1) <= trait.maxlen:
            try:
                validate = trait.item_trait.handler.validate
                object = self.object()
                if validate is not None:
                    value = validate(object, self.name, value)

                list.insert(self, index, value)

                if self.name_items is not None:
                    # Length before the insertion.
                    original_len = len(self) - 1

                    # Indices outside [-original_len, original_len] are clipped.
                    # This matches the behaviour of insert on the
                    # underlying list.
                    if index < 0:
                        index += original_len
                        if index < 0:
                            index = 0
                    elif index > original_len:
                        index = original_len

                    self._send_trait_items_event(
                        self.name_items,
                        TraitListEvent(index, None, [value]),
                        trait.items_event(),
                    )

                return

            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

        self.len_error(len(self) + 1)

    def extend(self, xlist):
        trait = getattr(self, "trait", None)
        if trait is None:
            list.extend(self, xlist)

            return

        try:
            len_xlist = len(xlist)
        except Exception:
            raise TypeError("list.extend() argument must be iterable")

        if trait.minlen <= (len(self) + len_xlist) <= trait.maxlen:
            object = self.object()
            name = self.name
            validate = trait.item_trait.handler.validate
            try:
                if validate is not None:
                    xlist = [validate(object, name, value) for value in xlist]

                list.extend(self, xlist)

                if (self.name_items is not None) and (len(xlist) != 0):
                    self._send_trait_items_event(
                        self.name_items,
                        TraitListEvent(len(self) - len(xlist), None, xlist),
                        trait.items_event(),
                    )

                return

            except TraitError as excp:
                excp.set_prefix("The elements of the")
                raise excp

        self.len_error(len(self) + len(xlist))

    def remove(self, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            list.remove(self, value)
            return
        if trait.minlen < len(self):
            try:
                index = self.index(value)
                removed = [self[index]]
            except Exception:
                pass

            list.remove(self, value)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed)
                )
        elif len(self) == 0:
            # Let whatever system error (ValueError) should be raised be raised.
            list.remove(self, value)
        else:
            self.len_error(len(self) - 1)

    def sort(self, key=None, reverse=False):
        removed = self[:]
        list.sort(self, key=key, reverse=reverse)
        if (
            getattr(self, "name_items", None) is not None
            and getattr(self, "trait", None) is not None
        ):
            self._send_trait_items_event(
                self.name_items, TraitListEvent(0, removed, self[:])
            )

    def reverse(self):
        removed = self[:]
        if len(self) > 1:
            list.reverse(self)
            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(0, removed, self[:])
                )

    def pop(self, *args):
        if not hasattr(self, "trait"):
            return list.pop(self, *args)
        if self.trait.minlen < len(self):
            if len(args) > 0:
                index = args[0]
            else:
                index = -1

            try:
                removed = [self[index]]
            except Exception:
                pass

            result = list.pop(self, *args)

            if self.name_items is not None:
                if index < 0:
                    index = len(self) + index + 1

                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed)
                )

            return result

        else:
            self.len_error(len(self) - 1)

    def rename(self, name):
        trait = self.object()._trait(name, 0)
        if trait is not None:
            self.name = name
            self.trait = trait.handler

    def len_error(self, len):
        raise TraitError(
            "The '%s' trait of %s instance must be %s, "
            "but you attempted to change its length to %d element%s."
            % (
                self.name,
                class_of(self.object()),
                self.trait.full_info(self.object(), self.name, Undefined),
                len,
                "s"[len == 1 :],
            )
        )

    def __getstate__(self):
        result = self.__dict__.copy()
        result.pop("object", None)
        result.pop("trait", None)

        return result

    def __setstate__(self, state):
        name = state.setdefault("name", "")
        object = state.pop("object", None)
        if object is not None:
            self.object = ref(object)
            self.rename(name)
        else:
            self.object = lambda: None

        self.__dict__.update(state)
'''