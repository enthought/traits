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
import copyreg
from weakref import ref

from traits.trait_base import Undefined
from traits.trait_errors import TraitError


class TraitSetEvent(object):
    """ An object reporting in-place changes to a traits sets.

    Parameters
    ----------
    added : dict or None
        New values added to the set, or optionally None if nothing was added.
    removed : dict or None
        Old values that were removed, or optionally None if nothing was
        removed.

    Attributes
    ----------
    added : dict
        New values added to the set. If nothing was added this is an empty
        set.
    removed : dict
        Old values that were removed. If nothing was removed this is an empty
        set.
    """

    def __init__(self, removed=None, added=None):
        if removed is None:
            removed = set()
        self.removed = removed

        if added is None:
            added = set()
        self.added = added


class TraitSet(set):
    """ A subclass of set that validates and notifies listeners of changes.

    Parameters
    ----------
    value : set
        The value for the set
    validator : callable
        Called to validate items in the set
    notifiers : list of callable
        A list of callables with the signature::

         notifier(trait_set, removed, added)

    Attributes
    ----------
    value : set
        The value for the set
    validator : callable
        Called to validate items in the set
    notifiers : list of callable
        A list of callables with the signature::

         notifier(trait_set, removed, added)

    """

    # ------------------------------------------------------------------------
    # TraitSet interface
    # ------------------------------------------------------------------------

    def validate(self, value):
        """ Validate the set of values.

        This simply calls the validator provided by the class, if any.
        The validator is expected to have the signature::

            validator(value)

        and return a set of validated values or raise TraitError.

        Parameters
        ----------
        value : set
            The new item or items being added to the set.

        Returns
        -------
        values : set
            The set of validated values.

        Raises
        ------
        TraitError : Exception
            If validation fails.
        """

        if not isinstance(value, set):
            if self._is_non_str_iterable(value):
                value = set(value)
            else:
                value = {value}

        # Use getattr as pickle can call `extend` before validator is set.
        if getattr(self, 'validator', None) is None:
            return value
        else:
            return self.validator(value)

    def notify(self, removed, added):
        """ Call all notifiers.

        This simply calls all notifiers provided by the class, if any.
        The notifiers are expected to have the signature::

            notifier(removed, added)

        Any return values are ignored.

        Parameters
        ----------
        removed : set
            The items to be removed.
        added : set
            The new items being added to the set.
        """
        if removed == added:
            return

        if removed is Undefined:
            removed = set()

        if added is Undefined:
            added = set()

        # Use getattr as pickle can call `extend` before notifiers are set.
        for notifier in getattr(self, 'notifiers', []):
            notifier(removed, added)

    def object(self):
        """ Stub method to pass persistence tests. """
        # XXX fix persistence tests to not introspect this!
        return None

    # ------------------------------------------------------------------------
    # set interface
    # ------------------------------------------------------------------------

    def __init__(self, value=(), *, validator=None, notifiers=()):
        self.validator = validator
        self.notifiers = list(notifiers)
        value = self.validate(value)
        super().__init__(value)

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        # notifiers are transient and should not be copied
        memo[id_self] = result = TraitSet(
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

    def add(self, value):
        """ Add an element to a set.

        This has no effect if the element is already present.

        Parameters
        ----------
        value : Any
            The value to add to the set.

        Notes
        -----
        Notification:
            removed : Undefined
                Will be Undefined.
            added : set
                A set containing the added value.

        """
        validated_values = self.validate(value)
        if len(validated_values) > 1:
            raise TypeError()

        value = validated_values.pop()
        if value not in self:
            super().add(value)
            self.notify(Undefined, {value})

    def remove(self, value):
        """ Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.

        Parameters
        ----------
        value : Any
            An element in the set

        Raises
        ------
        KeyError : Exception
            If the value is not found in the set.

        Notes
        -----
        Notification:
            removed : set
                A set containing the removed value.
            added : Undefined
                Will be Undefined.

        """
        validated_values = self.validate(value)
        if len(validated_values) > 1:
            raise TypeError()

        value = validated_values.pop()
        super().remove(value)
        self.notify({value}, Undefined)

    def update(self, value):
        """ Update a set with the union of itself and others.

        Parameters
        ----------
        value : iterable
            The other iterable.

        Notes
        -----
        Notification:
            removed : Undefined
                Will be Undefined.
            added : set
                A set containing the added values.

        """
        validated_values = self.validate(value)
        added = validated_values.difference(self)

        if len(added) > 0:
            self.notify(Undefined, added)

        super().update(added)

    def difference_update(self, value):
        """  Remove all elements of another set from this set.

        Parameters
        ----------
        value : iterable
            The other iterable.

        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.

        """
        validated_values = self.validate(value)
        removed = self.intersection(value)
        super().difference_update(validated_values)

        if len(removed) > 0:
            self.notify(removed, Undefined)

    def intersection_update(self, value):
        """  Remove all elements of set which are not common to another set.

        Parameters
        ----------
        value : iterable
            The other iterable.

        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.


        """
        validated_values = self.validate(value)
        removed = self.difference(self.intersection(validated_values))
        super().intersection_update(validated_values)
        if len(removed) > 0:
            self.notify(removed, Undefined)

    def symmetric_difference_update(self, value):
        """ Return the symmetric difference of two sets as a new set.

        (i.e. all elements that are in exactly one of the sets.)

        Parameters
        ----------
        value : iterable

        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : set
                A set containing the added values.

        """
        validated_values = self.validate(value)

        removed = self.intersection(validated_values)
        added = validated_values.difference(self)

        super().symmetric_difference_update(validated_values)

        if len(removed) + len(added) > 0:
            self.notify(removed, added)

    def discard(self, value):
        """ Remove an element from a set if it is a member.

        If the element is not a member, do nothing.

        Parameters
        ----------
        value : Any
            An item in the set
        Notes
        -----
        Notification:
            Fired if a value is removed.

            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.

        """
        try:
            self.remove(value)
        except KeyError:
            pass

    def pop(self):
        """ Remove and return an arbitrary set element.
        Raises KeyError if the set is empty.

        Returns
        -------
        item : Any
            An element from the set.

        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.

        """
        removed = super().pop()
        self.notify({removed}, Undefined)
        return removed

    def clear(self):
        """ Remove all elements from this set.
        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.

        """
        removed = set(self)
        super().clear()
        self.notify(removed, Undefined)

    def __reduce_ex__(self, protocol=None):
        """ Overridden to make sure we call our custom __getstate__.
        """
        return (
            copyreg._reconstructor,
            (type(self), set, list(self)),
            self.__getstate__(),
        )

    def __ior__(self, value):
        """ Return self|=value.

        Parameters
        ----------
        value : Any
            A value.

        Returns
        -------
        self : set
            The updated set.

        Notes
        -----
        Notification:
            removed : Undefined
                Will be Undefined.
            added : set
                Set of added values.

        """
        self.update(value)
        return self

    def __iand__(self, value):
        """  Return self&=value.

        Parameters
        ----------
        value : Any
            A value.

        Returns
        -------
        self : set
            The updated set.

        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.


        """
        self.intersection_update(value)
        return self

    def __ixor__(self, value):
        """ Return self ^= value.

        Parameters
        ----------
        value : Any
            A value.

        Returns
        -------
        self : set
            The updated set.
        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : set
                A set containing the added values.

        """
        self.symmetric_difference_update(value)
        return self

    def __isub__(self, value):
        """ Return self-=value.

        Parameters
        ----------
        value : Any
            A value.

        Returns
        -------
        self : set
            The updated set.
        Notes
        -----
        Notification:
            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.

        """
        self.difference_update(value)
        return self

    def _is_non_str_iterable(self, value):
        """ Returns True if the value is an iterable, but is not a string.

        Parameters
        ----------
        value : Any
            The value to test.

        Returns
        -------
        is_iterable : bool
            True if not a str type and is a iterable.

        """
        if isinstance(value, str):
            return False
        try:
            iter(value)
            return True
        except TypeError:
            return False


class TraitSetObject(TraitSet):
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

        super().__init__(value, validator=self.validator,
                         notifiers=[self.notifier] + notifiers)

    def validator(self, value):
        """ Validates the value by calling the inner trait's validate method
        and also ensures that the size of the list is within the specified
        bounds.

        Parameters
        ----------
        value : set
            set of values that need to be validated.

        Returns
        -------
        value : set of validated values

        Raises
        ------
        TraitError
            On validation failure for the inner trait or if the size of the
            list exceeds the specified bounds.

        """
        object = self.object()
        trait = self.trait
        if object is None or trait is None:
            return value

        # validate the new value(s)
        validate = trait.item_trait.handler.validate
        if validate is None:
            return value

        try:
            if value is Undefined:
                return Undefined
            else:
                return {validate(object, self.name, item) for item in value}

        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def notifier(self, removed, added):
        """ Converts and consolidates the parameters to a TraitSetEvent and
        then fires the event.

        Parameters
        ----------
        removed : set
            Set of values that were removed.
        added : set
            Set of values that were added.

        Returns
        -------
        None

        """
        is_trait_none = self.trait is None
        is_name_items_none = self.name_items is None
        if not hasattr(self, "trait") or is_trait_none or is_name_items_none:
            return

        object = self.object()
        if object is None:
            return

        if added is Undefined:
            added = set()

        if removed is Undefined:
            removed = set()

        event = TraitSetEvent(removed, added)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitSetObject(
            self.trait,
            lambda: None,
            self.name,
            {copy.deepcopy(x, memo) for x in self},
        )

        return result

    def __getstate__(self):
        """ Get the state of the object for serialization.

        Notifiers are transient and should not be serialized.
        """
        result = self.__dict__.copy()
        result.pop("object", None)
        result.pop("trait", None)

        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.

        Notifiers are transient and are restored to the empty list.
        """
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
