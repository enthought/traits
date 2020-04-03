# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import collections.abc
import copy
import copyreg
from weakref import ref

from traits.trait_errors import TraitError


def adapt_trait_validator(trait_validator, name="items"):
    """ Adapt a trait validator to work as a trait set validator.

    Parameters
    ----------
    trait_validator : callable
        A callable validator.
    name : str
        The name of the trait on the object.

    The trait validator is expected to have the signature::

        validator(object, name, value)


    Returns
    -------
    set_trait_validator : callable
        The trait validator that has been adapted for sets.

    """

    def validator(obj, value):
        try:
            return {
                trait_validator(obj, name, item)
                for item in value
            }
        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    return validator


class TraitSetEvent(object):
    """ An object reporting in-place changes to a traits sets.

    Parameters
    ----------
    added : set
        New values added to the set
    removed : set
        Old values that were removed from the set.

    Attributes
    ----------
    added : set
        New values added to the set
    removed : set
        Old values that were removed from the set.
    """

    def __init__(self, removed=set(), added=set()):
        self.removed = removed
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

            notifier(removed, added)

    Attributes
    ----------
    value : set
        The value for the set
    validator : callable
        Called to validate items in the set
    notifiers : list of callable
        A list of callables with the signature::

            notifier(removed, added)

    """

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.validator = None
        instance.notifiers = []
        return instance

    def __init__(self, value=(), *, validator=None, notifiers=None):
        self.validator = validator

        if notifiers is None:
            notifiers = []
        self.notifiers = list(notifiers)

        value = self.validate(set(value))
        super().__init__(value)

    # ------------------------------------------------------------------------
    # TraitSet interface
    # ------------------------------------------------------------------------

    def validate(self, value):
        """ Validate the set of values.

        This simply calls the validator provided by the class, if any.
        The validator is expected to have the signature::

            validator(original_set, added)

        and return a set of validated values or raise TraitError.

        Parameters
        ----------
        value : set
            The new items being added to the set.

        Returns
        -------
        values : set
            The set of validated values.

        Raises
        ------
        TraitError : Exception
            If validation fails.
        """

        if self.validator is None:
            return value
        else:
            return self.validator(self, value)

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
        for notifier in self.notifiers:
            notifier(removed, added)

    # ------------------------------------------------------------------------
    # set interface
    # ------------------------------------------------------------------------

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
        value : any
            The value to add to the set.

        Notes
        -----
        Parameters in the notification:
            removed : set
                An empty set.
            added : set
                A set containing the added value.

        """
        validated_values = self.validate(set([value]))
        if len(validated_values) > 1:
            raise ValueError("Validator returned {} values "
                             "where 1 value is "
                             "expected".format(len(validated_values)))

        value = next(iter(validated_values))
        if value not in self:
            super().add(value)
            self.notify(set(), validated_values)

    def remove(self, value):
        """ Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.

        Parameters
        ----------
        value : any
            An element in the set

        Raises
        ------
        KeyError
            If the value is not found in the set.

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed value.
            added : set
                An empty set.

        """
        super().remove(value)
        self.notify(set([value]), set())

    def update(self, value=()):
        """ Update a set with the union of itself and others.

        Parameters
        ----------
        value : iterable
            The other iterable.

        Notes
        -----
        Parameters in the notification:
            removed : set
                An empty set.
            added : set
                A set containing the added values.

        """
        validated_values = self.validate(set(value))
        added = validated_values.difference(self)

        if len(added) > 0:
            super().update(added)
            self.notify(set(), added)

    def difference_update(self, value=()):
        """  Remove all elements of another set from this set.

        Parameters
        ----------
        value : iterable
            The other iterable.

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed values.
            added : set
                An empty set.

        """
        removed = self.intersection(value)

        if len(removed) > 0:
            super().difference_update(removed)
            self.notify(removed, set())

    def intersection_update(self, value=None):
        """  Update a set with the intersection of itself and another.

        Parameters
        ----------
        value : iterable
            The other iterable.

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed values.
            added : set
                An empty set.


        """
        if value is None:
            return
        removed = self.difference(value)
        if len(removed) > 0:
            super().intersection_update(value)
            self.notify(removed, set())

    def symmetric_difference_update(self, value):
        """ Update a set with the symmetric difference of itself and another.

        Parameters
        ----------
        value : iterable

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed values.
            added : set
                A set containing the added values.

        """
        values = set(value)
        removed = self.intersection(values)
        to_be_added = values.difference(removed)
        added = self.validate(to_be_added)

        if removed or added:
            super().symmetric_difference_update(removed | added)
            self.notify(removed, added)

    def discard(self, value):
        """ Remove an element from a set if it is a member.

        If the element is not a member, do nothing.

        Parameters
        ----------
        value : any
            An item in the set

        Notes
        -----
        Parameters in the notification:
            Fired if a value is removed.

            removed : set
                A set containing the removed values.
            added : set
                An empty set.

        """
        if value in self:
            self.remove(value)
            self.notify({value}, set())

    def pop(self):
        """ Remove and return an arbitrary set element.
        Raises KeyError if the set is empty.

        Returns
        -------
        item : any
            An element from the set.

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed values.
            added : set
                An empty set.

        """
        removed = super().pop()
        self.notify({removed}, set())
        return removed

    def clear(self):
        """ Remove all elements from this set.

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed values.
            added : set
                An empty set.

        """
        removed = set(self)
        super().clear()
        self.notify(removed, set())

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
        value : any
            A value.

        Returns
        -------
        self : set
            The updated set.

        Notes
        -----
        Parameters in the notification:
            removed : set
                An empty set.
            added : set
                Set of added values.

        """
        self.update(value)
        return self

    def __iand__(self, value):
        """  Return self&=value.

        Parameters
        ----------
        value : any
            A value.

        Returns
        -------
        self : set
            The updated set.

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed values.
            added : set
                An empty set.


        """
        self.intersection_update(value)
        return self

    def __ixor__(self, value):
        """ Return self ^= value.

        Parameters
        ----------
        value : any
            A value.

        Returns
        -------
        self : set
            The updated set.

        Notes
        -----
        Parameters in the notification:
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
        value : any
            A value.

        Returns
        -------
        self : set
            The updated set.

        Notes
        -----
        Parameters in the notification:
            removed : set
                A set containing the removed values.
            added : Undefined
                Will be Undefined.

        """
        self.difference_update(value)
        return self


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

    def validator(self, current_set, value):
        """ Validates the value by calling the inner trait's validate method
        and also ensures that the size of the list is within the specified
        bounds.

        Parameters
        ----------
        current_set : set
            The current contents of the set.
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
        object_ref = getattr(self, 'object', None)
        trait = getattr(self, 'trait', None)

        if object_ref is None or trait is None:
            return value

        object = object_ref()

        # validate the new value(s)
        validate = trait.item_trait.handler.validate
        if validate is None:
            return value

        validate = adapt_trait_validator(validate, name=self.name)
        return validate(object, value)

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
        is_trait_none = getattr(self, 'trait', None) is None
        is_name_items_none = getattr(self, 'name_items', None) is None
        is_object_ref_none = getattr(self, 'object', None) is None
        if is_trait_none or is_name_items_none or is_object_ref_none:
            return

        object = self.object()
        if object is None:
            return

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
