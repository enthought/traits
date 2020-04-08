# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# XXX Put notification information back into docstrings? Or not? Should be
#     possible to interpret it without knowledge of the particular operation
#     performed, so it doesn't belong in individual docstrings. Instead, put
#     information into the main docstring.

import copy
import operator
from weakref import ref

from traits.trait_base import class_of, Undefined
from traits.trait_errors import TraitError


class TraitListEvent(object):
    """ An object reporting in-place changes to a trait list.

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


def _normalize_index(index, length):
    """ Normalize integer index to range 0 to len (inclusive). """
    index = operator.index(index)
    if index < 0:
        return max(0, length + index)
    else:
        return min(length, index)


def _normalize_slice(index, length):
    """ Normalize slice start and stop to range 0 to len (inclusive). """

    # Do not normalize if step is negative.
    if index.step is not None and index.step < 0:
        return index

    return slice(
        _normalize_index(0 if index.start is None else index.start, length),
        _normalize_index(length if index.stop is None else index.stop, length),
        index.step,
    )


# Default item validator for TraitList.


def accept_anything(item):
    """
    List item validator which accepts any item and returns it unaltered.
    """
    return item


class TraitList(list):
    """ A subclass of list that validates and notifies listeners of changes.

    Parameters
    ----------
    value : iterable
        Iterable providing the items for the list
    item_validator : callable, optional
        Called to validate and/or transform items added to the list. The
        callable should accept a single item from the list and return
        the transformed item, raising TraitError for invalid items. If
        not given, no item validation is performed.
    notifiers : list of callable, optional
        A list of callables with the signature::

            notifier(trait_list, index, removed, added)

        If this argument is not given, the list of notifiers is initially
        empty.

    Attributes
    ----------
    item_validator : callable
        Called to validate and/or transform items added to the list. The
        callable should accept a single item from the list and return
        the transformed item, raising TraitError for invalid items.
    notifiers : list of callable
        A list of callables with the signature::

            notifier(trait_list, index, removed, added)
    """

    def __new__(cls, *args, **kwargs):
        # We need a __new__ in addition to __init__ in order to properly
        # support unpickling: the 'append' or 'extend' methods may be
        # called during unpickling, triggering item validation.
        self = super().__new__(cls)
        self.item_validator = accept_anything
        self.notifiers = []
        return self

    def __init__(self, iterable=(), *, item_validator=None, notifiers=None):
        if item_validator is not None:
            self.item_validator = item_validator
        super().__init__(self.item_validator(item) for item in iterable)
        if notifiers is not None:
            self.notifiers = list(notifiers)

    def notify(self, index, removed, added):
        """ Call all notifiers.

        This simply calls all notifiers provided by the class, if any.
        The notifiers are expected to have the signature::

            notifier(trait_list, index, removed, added)

        Any return values are ignored.

        Parameters
        ----------
        index : int or slice
            The indices being modified by the operation.
        removed : list
            The items to be removed.
        added : list
            The items being added to the list.
        """
        for notifier in self.notifiers:
            notifier(self, index, removed, added)

    # -- list interface -------------------------------------------------------

    def __delitem__(self, key):
        """ Delete self[key].

        Parameters
        ----------
        key : integer or slice
            Index of the element(s) to be deleted.
        """

        if isinstance(key, slice):
            removed = self[key]
            normalized_index = _normalize_slice(key, len(self))
        else:
            # Suppress IndexError. If the lookup fails, __delitem__ should also
            # fail, and we want to allow the __delitem__ error to propagate.
            try:
                removed = [self[key]]
            except IndexError:
                pass
            normalized_index = _normalize_index(key, len(self))
        super().__delitem__(key)
        if removed:
            self.notify(normalized_index, removed, [])

    def __iadd__(self, value):
        """ Implement self += value.

        Parameters
        ----------
        value : iterable
            The items to be added.

        Returns
        -------
        self : TraitList
            The modified list.
        """

        original_length = len(self)
        added = [self.item_validator(item) for item in value]
        extended = super().__iadd__(added)
        if added:
            self.notify(slice(original_length, len(self)), [], added)
        return extended

    def __imul__(self, value):
        """ Implement self *= value.

        Parameters
        ----------
        value : integer
            The multiplier.

        Returns
        -------
        self : TraitList
            The modified list.
        """

        if value < 1:
            removed = self.copy()
            multiplied = super().__imul__(value)
            if removed:
                self.notify(slice(0, len(removed)), removed, [])
        else:
            original_length = len(self)
            multiplied = super().__imul__(value)
            new_length = len(self)
            if new_length > original_length:
                index = slice(original_length, new_length)
                self.notify(index, [], self[index])
        return multiplied

    def __setitem__(self, key, value):
        """ Set self[key] to value.

        Parameters
        ----------
        key : integer or slice
            Index of the element(s) to be replaced.
        value : iterable
            Replacement values.

        Raises
        ------
        IndexError
            If key is an integer index and is out of range.
        ValueError
            If key is an extended slice (that is, it's a slice whose step
            is not 1 and not None) and the number of replacement elements
            doesn't match the number of removed elements.
        """

        if isinstance(key, slice):
            value = [self.item_validator(item) for item in value]
            normalized_index = _normalize_slice(key, len(self))
            added = value
            removed = self[key]
        else:
            value = self.item_validator(value)
            normalized_index = _normalize_index(key, len(self))
            added = [value]
            # Suppress IndexError. If the lookup fails, __setitem__ should also
            # fail, and we want to allow the __setitem__ error to propagate.
            try:
                removed = [self[key]]
            except IndexError:
                pass
        super().__setitem__(key, value)

        if added != removed:
            self.notify(normalized_index, removed, added)

    def append(self, object):
        """ Append object to the end of the list.

        Parameters
        ----------
        object : any
            The object to append.
        """

        original_length = len(self)
        super().append(self.item_validator(object))
        self.notify(original_length, [], self[original_length:])

    def clear(self):
        """ Remove all items from list. """

        removed = self.copy()
        super().clear()
        if removed:
            self.notify(slice(0, len(removed)), removed, [])

    def extend(self, iterable):
        """ Extend list by appending elements from the iterable.

        Parameters
        ----------
        iterable : iterable
            The elements to append.
        """

        original_length = len(self)
        added = [self.item_validator(item) for item in iterable]
        super().extend(added)
        if added:
            self.notify(slice(original_length, len(self)), [], added)

    def insert(self, index, object):
        """ Insert object before index.

        Parameters
        ----------
        index : integer
            The position at which to insert.
        object : object
            The object to insert.
        """

        original_length = len(self)
        super().insert(index, self.item_validator(object))
        normalized_index = _normalize_index(index, original_length)
        self.notify(normalized_index, [], [self[normalized_index]])

    def pop(self, index=-1):
        """ Remove and return item at index (default last).

        Parameters
        ----------
        index : int, optional
            Index at which to remove item. If not given, the
            last item of the list is removed.

        Returns
        -------
        item : object
            The removed item.

        Raises
        ------
        IndexError
            If list is empty or index is out of range.
        """

        original_length = len(self)
        item = super().pop(index)
        normalized_index = _normalize_index(index, original_length)
        self.notify(normalized_index, [item], [])
        return item

    def remove(self, value):
        """ Remove first occurrence of value.

        Notes
        -----
        The value is not validated or converted before removal.

        Parameters
        ----------
        value : object
            Value to be removed.

        Raises
        ------
        ValueError
            If the value is not present.
        """
        # Suppress ValueError. If the index call fails because the item is not
        # in the list, remove should also fail, and we want to allow the remove
        # error to propagate.
        try:
            index = self.index(value)
        except ValueError:
            pass
        else:
            removed = [self[index]]
        super().remove(value)
        self.notify(index, removed, [])

    def reverse(self):
        """ Reverse the items in the list in place. """
        removed = self.copy()
        super().reverse()
        self.notify(slice(0, len(self)), removed, self.copy())

    def sort(self, *, key=None, reverse=False):
        """ Sort the list in ascending order and return None.

        The sort is in-place (i.e. the list itself is modified) and stable
        (i.e. the order of two equal elements is maintained).

        If a key function is given, apply it once to each list item and sort
        them, ascending or descending, according to their function values.

        The reverse flag can be set to sort in descending order.

        Parameters
        ----------
        key : callable
            Custom function that accepts a single item from the list and
            returns the key to be used in comparisons.
        reverse : bool
            If true, the resulting list will be sorted in descending order.
        """
        removed = self.copy()
        super().sort(key=key, reverse=reverse)
        self.notify(slice(0, len(self)), removed, self.copy())

    # -- pickle and copy support ----------------------------------------------

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """
        id_self = id(self)
        if id_self not in memo:
            # notifiers are transient and should not be copied
            memo[id_self] = type(self)(
                [copy.deepcopy(x, memo) for x in self],
                item_validator=copy.deepcopy(self.item_validator, memo),
            )
        return memo[id_self]

    def __getstate__(self):
        """ Get the state of the object for serialization.

        Notifiers are transient and should not be serialized.
        """
        result = self.__dict__.copy()
        result.pop("notifiers", None)
        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.

        Notifiers are transient and are restored to the empty list.
        """
        state["notifiers"] = []
        self.__dict__.update(state)


class TraitListObject(TraitList):
    """ A specialization of LengthConstrainedTraitList with a default
    validator and notifier which provide bug-for-bug compatibility with the
    TraitListObject from Traits versions before 6.0.

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

    Attributes
    ----------
    trait : CTrait
        The trait that the list has been assigned to.
    object : HasTraits
        The object the list belongs to.
    name : str
        The name of the trait on the object.
    value : iterable
        The initial value of the list.
    """

    def __init__(self, trait, object, name, value):

        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        # Convert to an explicit list so that we can validate the length.
        value = list(value)
        self._validate_length(len(value))

        super().__init__(
            value,
            item_validator=self._item_validator,
            notifiers=[self.notifier],
        )

    def notifier(self, trait_list, index, removed, added):
        """ Converts and consolidates the parameters to a TraitListEvent and
        then fires the event.

        Parameters
        ----------
        trait_list : list
            The list
        index : int or slice
            Index or slice that was modified
        removed : list
            Values that were removed
        added : list
            Values that were added

        """
        is_trait_none = self.trait is None
        is_name_items_none = self.name_items is None
        if not hasattr(self, "trait") or is_trait_none or is_name_items_none:
            return

        object = self.object()
        if object is None:
            return

        # bug-for-bug conversion of parameters to TraitListEvent
        if isinstance(index, slice):
            if index.step is None or index.step == 1:
                index = min(index.start, index.stop)

        event = TraitListEvent(index, removed, added)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)

    # -- list interface -------------------------------------------------------

    def __delitem__(self, key):
        """ Delete self[key].

        Parameters
        ----------
        key : integer or slice
            Index of the element(s) to be deleted.
        """
        removed_count = len(self[key]) if isinstance(key, slice) else 1
        self._validate_length(len(self) - removed_count)
        super().__delitem__(key)

    def __iadd__(self, value):
        """ Implement self += value.

        Parameters
        ----------
        value : iterable
            The items to be added.

        Returns
        -------
        self : LengthConstrainedTraitList
            The modified list.
        """

        # Convert input to a concrete list for length-checking purposes.
        value = list(value)
        self._validate_length(len(self) + len(value))
        return super().__iadd__(value)

    def __imul__(self, value):
        """ Implement self *= value.

        Parameters
        ----------
        value : integer
            The multiplier.

        Returns
        -------
        self : LengthConstrainedTraitList
            The modified list.
        """

        self._validate_length(len(self) * value)
        return super().__imul__(value)

    def __setitem__(self, key, value):
        """ Set self[key] to value.

        Parameters
        ----------
        key : integer or slice
            Index of the element(s) to be replaced.
        value : iterable
            Replacement values.

        Raises
        ------
        IndexError
            If key is an integer index and is out of range.
        ValueError
            If key is an extended slice (that is, it's a slice whose step
            is not 1 and not None) and the number of replacement elements
            doesn't match the number of removed elements.
        """

        if isinstance(key, slice):
            value = list(value)
            if key.step is None or key.step == 1:
                self._validate_length(len(self) - len(self[key]) + len(value))
            else:
                # No length change possible, so no need to validate length. But
                # for backwards compatibility we simulate Python's complaint
                # about any length difference before validating items.
                if len(value) != len(self[key]):
                    raise ValueError(
                        "attempt to assign sequence of size {} "
                        "to extended slice of size {}".format(
                            len(value), len(self[key])
                        )
                    )
        super().__setitem__(key, value)

    def append(self, object):
        """ Append object to the end of the list.

        Parameters
        ----------
        object : any
            The object to append.
        """

        self._validate_length(len(self) + 1)
        super().append(object)

    def clear(self):
        """ Remove all items from list. """

        self._validate_length(0)
        super().clear()

    def extend(self, iterable):
        """ Extend list by appending elements from the iterable.

        Parameters
        ----------
        iterable : iterable
            The elements to append.
        """

        # Convert input to a concrete list for length-checking purposes.
        items = list(iterable)
        self._validate_length(len(self) + len(items))
        super().extend(items)

    def insert(self, index, object):
        """ Insert object before index.

        Parameters
        ----------
        index : integer
            The position at which to insert.
        object : object
            The object to insert.
        """

        self._validate_length(len(self) + 1)
        super().insert(index, object)

    def pop(self, index=-1):
        """ Remove and return item at index (default last).

        Parameters
        ----------
        index : int, optional
            Index at which to remove item. If not given, the
            last item of the list is removed.

        Returns
        -------
        item : object
            The removed item.

        Raises
        ------
        IndexError
            If list is empty or index is out of range.
        """

        self._validate_length(len(self) - 1)
        return super().pop(index)

    def remove(self, value):
        """ Remove first occurrence of value.

        Notes
        -----
        The value is not validated or converted before removal.

        Parameters
        ----------
        value : object
            Value to be removed.

        Raises
        ------
        ValueError
            If the value is not present.
        """

        self._validate_length(len(self) - 1)
        super().remove(value)

    # -- pickle and copy support ----------------------------------------------

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """
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

    def __getstate__(self):
        """ Get the state of the object for serialization.

        Notifiers are transient and should not be serialized.
        """
        result = super().__getstate__()
        result.pop("object", None)
        result.pop("trait", None)

        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.

        Notifiers are transient and are restored to the empty list.
        """
        name = state.setdefault("name", "")
        state["notifiers"] = [self.notifier]
        object = state.pop("object", None)
        if object is not None:
            state["object"] = ref(object)
            trait = self.object()._trait(name, 0)
            if trait is not None:
                state["trait"] = trait.handler
        else:
            state["object"] = lambda: None
            state["trait"] = None

        self.__dict__.update(state)

    # -- private methods ------------------------------------------------------

    def _item_validator(self, value):
        """
        Validate an item that's being added to the list.
        """
        object = self.object()
        if object is None:
            return value

        trait_validator = self.trait.item_trait.handler.validate
        if trait_validator is None:
            return value

        try:
            return trait_validator(object, self.name, value)
        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise

    def _validate_length(self, new_length):
        """
        Validate the new length for a proposed operation.

        Parameters
        ----------
        new_length : int
            New length of the list.

        Raises
        ------
        TraitError
            If the proposed new length would violate the length constraints
            of the list.
        """
        trait = getattr(self, "trait", None)
        if trait is None:
            return

        if not trait.minlen <= new_length <= trait.maxlen:
            raise TraitError(
                "The '%s' trait of %s instance must be %s, "
                "but you attempted to change its length to %d %s."
                % (
                    self.name,
                    class_of(object),
                    self.trait.full_info(object, self.name, Undefined),
                    new_length,
                    "element" if new_length == 1 else "elements",
                )
            )
