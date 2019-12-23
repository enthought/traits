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


def adapt_trait_validator(trait_validator):
    """ Adapt a trait validator to work as a trait list validator.
    """

    def validator(trait_list, index, removed, value):
        try:
            if isinstance(index, slice):
                return [
                    trait_validator(trait_list, "items", item)
                    for item in value
                ]
            else:
                return trait_validator(trait_list, "items", value)
        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    return validator


class TraitList(list):
    """ A subclass of list that validates and notifies listeners of changes.
    """

    # ------------------------------------------------------------------------
    # TraitList interface
    # ------------------------------------------------------------------------

    def validate(self, index, removed, value):
        """ Validate values for given index and removed values.

        This simply calls the validator provided by the class, if any.
        The validator is expected to have the signature::

            validator(trait_list, index, removed, value)

        and return a list of validated values or raise TraitError.

        Parameters
        ----------
        index : int or slice
            The indices being modified by the operation.
        removed : object or list
            The item or items to be removed.
        value : object or iterable
            The new item or items being added to the list.

        Returns
        -------
        values : object or list
            The validated values

        Raises
        ------
        TraitError
            If validatation fails.
        """
        if self.validator is None:
            if isinstance(index, slice):
                return list(value)
            else:
                return value
        else:
            return self.validator(self, index, removed, value)

    def notify(self, index, removed, added):
        """ Call all notifiers

        This simply calls all notifiers provided by the class, if any.
        The notifiers are expected to have the signature::

            notifier(trait_list, index, removed, added)

        Any return values are ignored.

        Parameters
        ----------
        index : int or slice
            The indices being modified by the operation.
        removed : object or list
            The item or items to be removed.
        added : object or list
            The new item or items being added to the list.
        """
        if removed == added:
            return
        for notifier in self.notifiers:
            notifier(self, index, removed, added)

    def object(self):
        """ Stub method to pass persistence tests. """
        # XXX fix persistence tests to not introspect this!
        return None

    # ------------------------------------------------------------------------
    # list interface
    # ------------------------------------------------------------------------

    def __init__(self, value=(), *, validator=None, notifiers=()):
        self.validator = validator
        self.notifiers = list(notifiers)
        value = self.validate(slice(0, 0), [], value)
        super().__init__(value)

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """
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
        """ Get the state of the object for serialization.

        Notifiers are transient and should not be serialized.
        """
        result = self.__dict__.copy()
        # notifiers are transient and should not be serialized
        result.pop("notifiers", None)
        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.

        Notifiers are transient and are restored to the empty list.
        """
        state['notifiers'] = []
        self.__dict__.update(state)

    def __setitem__(self, index, value):
        """ Set self[index] to value. """
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
        """ Delete self[index]. """
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
        """ Implement self += value. """
        self.extend(other)
        return self

    def __imul__(self, count):
        """ Implement self *= value. """
        if count > 1:
            self.extend(self * (count-1))
        elif count == 0:
            self[:] = []
        return self

    def append(self, object):
        """ Append object to end """
        index = len(self)
        removed = Undefined
        added = self.validate(index, removed, object)

        super().append(added)

        self.notify(index, removed, added)

    def extend(self, iterable):
        """ Extend list by appending elements from the iterable """
        index = slice(len(self), len(self))
        removed = []
        added = self.validate(index, removed, iterable)

        super().extend(added)

        self.notify(index, removed, added)

    def insert(self, index, object):
        """ Insert object before index """
        removed = Undefined
        added = self.validate(index, removed, object)
        norm_index = self._normalize_index(index)

        super().insert(index, added)

        self.notify(norm_index, removed, added)

    def pop(self, index=-1):
        """ Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        removed = self._get_removed(index)
        added = self.validate(index, removed, Undefined)
        norm_index = self._normalize_index(index)

        removed = super().pop(index)

        self.notify(norm_index, removed, added)

        return removed

    def remove(self, value):
        """ Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        index = self.index(value)
        added = self.validate(index, value, Undefined)

        super().remove(value)

        self.notify(index, value, added)

    def sort(self, key=None, reverse=False):
        """ Stable sort *IN PLACE* """
        self[:] = sorted(self, key=key, reverse=reverse)

    def reversed(self):
        """ Reverse *IN PLACE* """
        self[:] = self[::-1]

    # ------------------------------------------------------------------------
    # Private interface
    # ------------------------------------------------------------------------

    def _get_removed(self, index):
        """ Compute removed values given index. """
        try:
            return self[index]
        except Exception:
            if isinstance(index, slice):
                return []
            else:
                return Undefined

    def _normalize_index(self, index):
        """ Normalize integer index to range 0 to len (inclusive). """
        index = operator.index(index)
        if index < 0:
            return max(0, len(self) + index)
        else:
            return min(len(self), index)

    def _normalize_slice(self, index):
        """ Normalize slice start and stop to range 0 to len (inclusive). """
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


def TraitListObject(trait, object, name, value, notifiers=[]):
    """ Factory function for backward compatible traits lists.

    This creates a TraitList with default validator and notifier which
    provide bug-for-bug compatibility with the TraitsListObject from
    Traits versions before 6.0.

    The state required is encapsulated in a helper object.

    Parameters
    ----------
    trait : CTrait
        The trait that the list has been assigned to.
    object : HasTraits
        The object the list belongs to.
    name : str
        The name of the trait on the object.
    value : iterable
        The initial value of the list.
    notifiers : list
        Additional notifiers for the list.

    Returns
    -------
    trait_list : TraitList
        A configured trait list.
    """
    helper = TraitListObjectHelper(trait, object, name)
    return TraitList(
        value,
        validator=helper.validator,
        notifiers=[helper.notifier] + notifiers
    )


class TraitListObjectHelper:
    """ Helper object for backward compatible traits lists.

    The object encapsulates the state required for backward compatible
    behaviour and provides a validator and a listener method that
    produce compatible result.

    Attributes
    ----------
    trait : CTrait
        The trait that the list has been assigned to.
    object : HasTraits
        The object the list belongs to.
    name : str
        The name of the trait on the object.
    name_items : str
        The name of the "items" trait on the object.
    """

    def __init__(self, trait, object, name):
        """ TraitListObjectHelper initializer.

        Parameters
        ----------
        trait : CTrait
            The trait that the list has been assigned to.
        object : HasTraits
            The object the list belongs to.
        name : str
            The name of the trait on the object.
        """
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


class TraitListEvent(object):
    """ An object reporting in-place changes to a traits list.

    Attributes
    ----------
    index : int or slice
        The index of the change in the list.
    added : list
        The list of values added to the list.
    removed : list
        The list of values removed from the list.
    """

    def __init__(self, index=0, removed=None, added=None):
        """
        Parameters
        ----------
        index : int or slice
            The index of the change in the list.
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
