#####
# Copy from enthought/traits#912
#####

import copy
import operator
from weakref import ref

from traits.trait_base import class_of, Undefined
from traits.trait_errors import TraitError

def adapt_trait_validator(trait_validator):
    """ Adapt a trait validator to work as a trait list validator.

    Parameters
    ----------
    trait_validator : callable
    The trait validator is expected to have the signature::

        validator(object, name, value)


    Returns
    -------
    list_trait_validator : callable
        The trait validator that has been adapted for lists.

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


class TraitList(list):
    """ A subclass of list that validates and notifies listeners of changes.

    Parameters
    ----------
    value : list
        The value for the list
    validator : callable
        Called to validate items in the list
    notifiers : list of callable
        A list of callables with the signature::

         notifier(trait_list, index, removed, added)

    Attributes
    ----------
    value : list
        The value for the list
    validator : callable
        Called to validate items in the list
    notifiers : list of callable
        A list of callables with the signature::

         notifier(trait_list, index, removed, added)

    """

    # ------------------------------------------------------------------------
    # TraitList interface
    # ------------------------------------------------------------------------

    def validate(self, index, removed, added):
        """ Validate values for given index and removed values.

        This simply calls the validator provided by the class, if any.
        The validator is expected to have the signature::

            validator(trait_list, index, removed, added)

        and return a validated added value or list of added values
        or raise a TraitError.

        Parameters
        ----------
        index : int or slice
            The indices being modified by the operation.
        removed : list
            The items to be removed.
        added : list
            The new items being added to the list.

        Returns
        -------
        values : list
            The validated values that must be added to the list.

        Raises
        ------
        TraitError
            If validation fails.
        """

        # Use getattr as pickle can call `extend` before validator is set.
        if getattr(self, 'validator', None) is None:
            return added
        else:
            return self.validator(self, index, removed, added)

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
        removed : list
            The items to be removed.
        added : list
            The items being added to the list.
        """
        # Use getattr as pickle can call `extend` before notifiers are set.
        for notifier in getattr(self, 'notifiers', []):
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
        result.pop("notifiers", None)
        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.

        Notifiers are transient and are restored to the empty list.
        """
        state['notifiers'] = []
        self.__dict__.update(state)

    def __setitem__(self, index, value):
        """ Set a value at index, implements self[index] = value

        Parameters
        ----------
        index : int
            Index at which the value will be set.
        value : Any
            The value to set at the index.

        Notes
        -----
        Notification:
            index : int
                The index of the value.
            added : list
                The value that is set, as a list.
            removed : list
                The value that is removed, as a list.

        """
        removed = self._get_removed(index)

        if isinstance(index, slice):
            if len(removed) != len(value) and index.step not in {1, None}:
                raise ValueError

        value, unwrap_value = self._as_list(index, value)

        norm_index = self._normalize(index)

        added = self.validate(norm_index, removed, value)

        if unwrap_value:
            item = added[0]
        else:
            item = added

        super().__setitem__(index, item)

        if self._should_notify(removed, added):
            self.notify(norm_index, removed, added)

    def __delitem__(self, index):
        """ Delete an item from the list at index.

        Parameters
        ----------
        index : int
            Index of the element to be deleted.

        Notes
        -----
        Notification:
            index : int
                The index of the value that is deleted.
            added : list
            removed : list
                The removed value, as a list.

        """
        added = []
        removed = self._get_removed(index)
        norm_index = self._normalize(index)
        self.validate(norm_index, removed, added)

        super().__delitem__(index)

        if self._should_notify(removed, added):
            self.notify(norm_index, removed, added)

    def append(self, object):
        """ Append an item to the end of the list.

        Parameters
        ----------
        object : Any
            The item to append to the list.


        Notes
        -----
        Notification:
            index : int
                The index of the newly appended item.
            added : list
                The new item, as a list
            removed : list
                Will be []

        """
        index = len(self)

        removed = []
        object, unwrap_object = self._as_list(index, object)
        added = self.validate(index, removed, object)

        if unwrap_object:
            object = added[0]
        else:
            object = added

        super().append(object)

        if self._should_notify(removed, added):
            self.notify(index, removed, added)

    def extend(self, iterable):
        """ Extend list by appending elements from the iterable.

        Parameters
        ----------
        iterable : iterable
            Any iterable type


        Notes
        -----
        Notification:
            index : slice
                The slice(current_length,new_length) if successful if
                the iterable supports len() else the slice(current_len,None,1).
            added : list
                The newly added items.
            removed : list
                Will be []

        """
        iterable = list(iterable)
        try:
            index = slice(len(self), len(self) + len(iterable))
        except TypeError:
            index = slice(len(self), None, 1)

        removed = []
        iterable, unwrap_iterable = self._as_list(index, iterable)
        added = self.validate(index, removed, iterable)

        if unwrap_iterable:
            value = added[0]
        else:
            value = added

        super().extend(value)

        if self._should_notify(removed, added):
            self.notify(index, removed, added)

    def insert(self, index, object):
        """ Insert an object to the list before index.

        Parameters
        ----------
        index : int
            The index before which to insert the object.
        object : Any
            The object to insert.


        Notes
        -----
        Notification:
            index : int
                The index before which the item was inserted.
            added : list
                The newly added item(s) as a list.
            removed : list
                Will be []

        """
        removed = []
        object, unwrap_object = self._as_list(index, object)
        norm_index = self._normalize_index(index)
        added = self.validate(norm_index, removed, object)

        if unwrap_object:
            added_value = added[0]
        else:
            added_value = added

        super().insert(index, added_value)

        if self._should_notify(removed, added):
            self.notify(norm_index, removed, added)

    def clear(self):
        """ Remove all items from the list


        Notes
        -----
        Notification:
            index : slice
                The range of the slice will be 0 to len(self).
            added : list
                The empty list [].
            removed : list
                The removed items.

        """
        index = slice(0, len(self), None)
        removed = self.copy()
        self.validate(index, removed, [])
        super().clear()

        if self._should_notify(removed, []):
            self.notify(index, removed, [])

    def pop(self, index=-1):
        """ Remove and return item at index (default last).

        Parameters
        ----------
        index: int
            Index at which item has to be removed.

        Returns
        -------
        item : An item in the list at given index, last item if no index given.

        Raises
        ------
        IndexError
            If list is empty or index is out of range.

        Notes
        -----
        Notification:
            index : int
                The normalized index between 0 and len(self).
            added : list
                Will be []
            removed : list
                The removed item, as a list.

        """

        added = []
        removed = self._get_removed(index)
        norm_index = self._normalize_index(index)
        self.validate(norm_index, removed, added)

        removed_item = super().pop(index)

        if self._should_notify(removed, added):
            self.notify(norm_index, removed, added)

        return removed_item

    def remove(self, value):
        """ Remove first occurrence of value.

        Parameters
        ----------
        value : Any
            A value contained in the list.

        Raises
        ------
        ValueError
            If the value is not present.

        Notes
        -----
        Notification:
            index : int
                The index between 0 and len(self).
            added : list
                Will be [].
            removed : list
                The removed item, as a list.

        """
        index = self.index(value)
        removed, _ = self._as_list(index, value)

        self.validate(index, removed, [])

        super().remove(value)

        if self._should_notify(removed, []):
            self.notify(index, removed, [])

    def sort(self, key=None, reverse=False):
        """ Sort the items in the list in ascending order, *IN PLACE*.
        A custom key function can be supplied to customize
        the sort order, and the reverse flag can be set to request the result
        in descending order.

        Parameters
        ----------
        key : Callable
            Custom function.
        reverse : bool
            If true, the resulting list will be sorted in descending order.

        Notes
        -----
        Notification:
            index : slice
                The slice between 0 and len(self)
            added : list
                A copy of the list after sorting elements.
            removed : list
                A copy of the list before sorting elements.

        """

        removed = self[:]
        self[:] = sorted(self, key=key, reverse=reverse)
        added = self[:]
        index = slice(0, len(self), None)

        self.notify(index, removed, added)

    def reverse(self):
        """ Reverse the order of the items in the list *IN PLACE*.

        Notes
        -----
        Notification:
            index : slice
                The slice between 0 and len(self).
            added : list
                A copy of the list after reversing the order of items.
            removed : list.
                A copy of the list before reversing the order of items.

        """
        removed = self[:]
        self[:] = self[::-1]
        added = self[:]

        index = slice(0, len(self), None)

        self.notify(index, removed, added)

    def __iadd__(self, other):
        """ Implements the self += value operator.

        Parameters
        ----------
        other : Any
            The item to add to the list.

        Notes
        -----
        Notification:
            index : slice
                Slice ranging from current_length to new_length.
            added : list
                The  new values that were added.
            removed : list
                The empty list [].

        """
        self.extend(other)
        return self

    def __imul__(self, count):
        """ Implements the self *= value operator.

        Parameters
        ----------
        count : int
            Number of times to duplicate the list.

        Notes
        -----
        Notification:
            index : slice
                Slice ranging from current_length to new_length.
            added : list
                The  new values that were added.
            removed : list
                The empty list [].

        """
        if count > 1:
            self.extend(self * (count - 1))
        elif count == 0:
            self[:] = []
        return self

    # ------------------------------------------------------------------------
    # Private interface
    # ------------------------------------------------------------------------

    def _get_removed(self, index):
        """ Compute removed values given index. """
        try:
            if not isinstance(index, slice):
                return [self[index]]
            else:
                return self[index]
        except IndexError:
            return []

    def _normalize(self, index):
        if isinstance(index, slice):
            return self._normalize_slice(index)
        else:
            return self._normalize_index(index)

    def _normalize_index(self, index):
        """ Normalize integer index to range 0 to len (inclusive). """
        index = operator.index(index)
        if index < 0:
            return max(0, len(self) + index)
        else:
            return min(len(self), index)

    def _normalize_slice(self, index):
        """ Normalize slice start and stop to range 0 to len (inclusive). """

        # Do not normalize if step is negative.
        if index.step is not None and index.step < 0:
            return index

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

    def _should_notify(self, removed, added):
        return True

    def _as_list(self, index, value):
        if not isinstance(index, slice):
            return [value], True
        return value, False


class TraitListObject(TraitList):
    """ A specialization of TraitList with a default validator and notifier
    which provide bug-for-bug compatibility with the TraitsListObject from
    Traits versions before 6.0.
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
    notifiers : list
        Additional notifiers for the list.
    """

    def __init__(self, trait, object, name, value, notifiers=[]):

        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        # ------------------------------
        # Added for observer
        from traits.trait_types import Event
        self._event_ctrait = Event().as_ctrait()
        # ------------------------------

        super().__init__(value, validator=self.validator,
                         notifiers=[self.notifier] + notifiers)

    def validator(self, trait_list, index, removed, added):
        """ Validates the value by calling the inner trait's validate method
        and also ensures that the size of the list is within the specified
        bounds.
        Parameters
        ----------
        trait_list : list
            The current list.
        index : index or slice
            Index or slice corresponding to the values added/removed.
        removed : list
            values that are removed.
        added : list
            value or list of values that are added.
        Returns
        -------
        value : validated value or list of validated values.
        Raises
        ------
        TraitError : Exception
            On validation failure for the inner trait or if the size of the
            list exceeds the specified bounds
        """
        object = self.object()
        trait = self.trait

        if object is None or trait is None:
            return added

        # check that length is within bounds
        new_len = len(trait_list) - self._get_length(
            removed) + self._get_length(added)
        if not trait.minlen <= new_len <= trait.maxlen:
            raise TraitError(
                "The '%s' trait of %s instance must be %s, "
                "but you attempted to change its length to %d element%s."
                % (
                    self.name,
                    class_of(object),
                    self.trait.full_info(object, self.name, Undefined),
                    new_len,
                    "s"[new_len == 1:],
                )
            )

        added_value = added
        if not isinstance(index, slice):
            if len(added) > 0:
                added_value = added[0]

        # validate the new value(s)
        validate = trait.item_trait.handler.validate
        if validate is None or added == []:
            if not isinstance(index, slice):
                if not isinstance(added_value, list):
                    return [added_value]
            return added_value

        try:
            if isinstance(index, slice):
                return [
                    validate(object, self.name, item) for item in added_value
                ]

            return [validate(object, self.name, added_value)]

        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def notifier(self, trait_list, index, removed, added):
        """ Converts and consolidates the parameters to a TraitListEvent and
        then fires the event.
        Parameters
        ----------
        trait_list : list
            The list
        index : int or slice
            Index or slice that was modified
        removed : value or list of values
            Value or list of values that were removed
        added : value or list of values
            Value or list of values that were added
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
            if index.step in {1, None}:
                index = min(index.start, index.stop)

        event = TraitListEvent(index, removed, added)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)

        # -------------------------------------------
        # Added for observer

        # Is this right?
        event = (trait_list, index, removed, added)
        for notifier in self._notifiers(True):
            # We don't actually have the old copy of the list
            notifier(object, self.name, trait_list, event)
        # -------------------------------------------

    # -------------------------------------------
    # Added for observer
    def _notifiers(self, force_create):
        return self._event_ctrait._notifiers(force_create)
    # -------------------------------------------

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
        super().__setstate__(state)
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

    def _get_length(self, object):
        if isinstance(object, list):
            return len(object)
        else:
            return 1


from interfaces import INotifiableObject

INotifiableObject.register(TraitListObject)
