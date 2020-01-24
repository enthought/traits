# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import copy
from weakref import ref

from .trait_base import class_of, Undefined
from .trait_errors import TraitError


class TraitListEvent(object):
    """ An object reporting in-place changes to a traits list.

    Parameters
    ----------
    index : int or slice
        An index or slice indicating the location of the changes to the list.
    added : list or None
        The list of values added to the list, or optionally None if nothing
        is added.
    removed : list or None
        The list of values removed from the list, or optionally None if
        nothing is removed.

    Attributes
    ----------
    index : int or slice
        An index or slice indicating the location of the changes to the list.
    added : list
        The list of values added to the list.  If nothing was added this is
        an empty list.
    removed : list
        The list of values removed from the list.  If nothing was removed
        this is an empty list.
    """

    def __init__(self, index=0, removed=None, added=None):
        self.index = index

        if removed is None:
            removed = []
        self.removed = removed

        if added is None:
            added = []
        self.added = added


class TraitListObject(list):
    """ A subclass of list that fires trait events when mutated.

    This is used by the List trait type, and all values set into a List
    trait will be copied into a new TraitListObject instance.

    Mutation of the TraitListObject will fire a "name_items" event with
    appropriate index, added and removed values.  In the case of setting
    or deleting items with a slice, the index will hold either:

    - the location of the first element changed, if the step is 1.  In
      this case the last element changed can be inferred from the
      length of the removed values.
    - the slice that was used, otherwise.

    Parameters
    ----------
    trait : CTrait instance
        The CTrait instance associated with the attribute that this list
        has been set to.
    object : HasTraits instance
        The HasTraits instance that the list has been set as an attribute for.
    name : str
        The name of the attribute on the object.
    value : list
        The list of values to initialize the TraitListObject with.

    Attributes
    ----------
    trait : CTrait instance
        The CTrait instance associated with the attribute that this list
        has been set to.
    object : weak reference to a HasTraits instance
        A weak reference to a HasTraits instance that the list has been set
        as an attribute for.
    name : str
        The name of the attribute on the object.
    name_items : str
        The name of the items event trait that the trait list will fire when
        mutated.
    """

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
                    index = key
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
        else:
            delta = 1
            index = len(self) + key + 1 if key < 0 else key
            removed = [removed]

        if not (trait.minlen <= (len(self) - delta)):
            self.len_error(len(self) - delta)
            return

        list.__delitem__(self, key)

        if self.name_items is not None and removed:
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

    def clear(self):
        if self.trait.minlen > 0:
            self.len_error(0)

        if len(self) == 0:
            list.clear(self)
            return

        removed = self.copy()
        list.clear(self)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitListEvent(0, removed)
            )

    def len_error(self, len):
        """ Utility method that raises an error if length is incorrect. """
        raise TraitError(
            "The '%s' trait of %s instance must be %s, "
            "but you attempted to change its length to %d element%s."
            % (
                self.name,
                class_of(self.object()),
                self.trait.full_info(self.object(), self.name, Undefined),
                len,
                "s"[len == 1:],
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
