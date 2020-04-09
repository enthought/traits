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

from traits.trait_errors import TraitError


class TraitSetEvent(object):
    """ An object reporting in-place changes to a traits sets.

    Parameters
    ----------
    added : set, optional
        New values added to the set.
    removed : set, optional
        Old values that were removed from the set.

    Attributes
    ----------
    added : set
        New values added to the set.
    removed : set
        Old values that were removed from the set.
    """

    def __init__(self, removed=None, added=None):

        if removed is None:
            removed = set()
        self.removed = removed

        if added is None:
            added = set()
        self.added = added


# Default item validator for TraitList.

def accept_anything(item):
    """
    Item validator which accepts any item and returns it unaltered.
    """
    return item


class TraitSet(set):
    """ A subclass of set that validates and notifies listeners of changes.

    Parameters
    ----------
    value : iterable
        Iterable providing the items for the set.
    item_validator : callable, optional
        Called to validate and/or transform items added to the list. The
        callable should accept a single item from the list and return
        the transformed item, raising TraitError for invalid items. If
        not given, no item validation is performed.
    notifiers : list of callable
        A list of callables with the signature::

            notifier(removed, added)

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

            notifier(removed, added)

    """

    def __new__(cls, *args, **kwargs):
        # We need a __new__ in addition to __init__ in order to properly
        # support unpickling: the 'append' or 'extend' methods may be
        # called during unpickling, triggering item validation.
        self = super().__new__(cls)
        self.item_validator = accept_anything
        self.notifiers = []
        return self

    def __init__(self, value=(), *, item_validator=None, notifiers=None):
        if item_validator is not None:
            self.item_validator = item_validator
        super().__init__(self.item_validator(item) for item in value)
        if notifiers is not None:
            self.notifiers = list(notifiers)

    def notify(self, removed, added):
        """ Call all notifiers.

        This simply calls all notifiers provided by the class, if any.
        The notifiers are expected to have the signature::

            notifier(removed, added)

        Any return values are ignored. Any exceptions raised are not
        handled. Notifiers are therefore not expected to raise any
        exceptions under normal use.

        Parameters
        ----------
        removed : set
            The items to be removed.
        added : set
            The new items being added to the set.
        """
        for notifier in self.notifiers:
            notifier(removed, added)

    # -- set interface -------------------------------------------------------

    def __ior__(self, value):
        """ Return self |= value.

        Parameters
        ----------
        value : any
            The value to update the set with.

        Returns
        -------
        self : set
            The updated set.
        """

        self.update(value)
        return self

    def __iand__(self, value):
        """  Return self &= value.

        Parameters
        ----------
        value : any
            A value.

        Returns
        -------
        self : set
            The updated set.
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
        """

        self.difference_update(value)
        return self

    def add(self, value):
        """ Add an element to a set.

        This has no effect if the element is already present.

        Parameters
        ----------
        value : any
            The value to add to the set.
        """

        value = self.item_validator(value)
        if value not in self:
            super().add(value)
            self.notify(set(), {value})

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
        """

        super().remove(value)
        self.notify(set([value]), set())

    def update(self, value=()):
        """ Update a set with the union of itself and others.

        Parameters
        ----------
        value : iterable
            The other iterable.
        """

        validated_values = {self.item_validator(item) for item in value}
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
        """

        removed = self.intersection(value)
        super().difference_update(value)

        if len(removed) > 0:
            self.notify(removed, set())

    def intersection_update(self, value=None):
        """  Update a set with the intersection of itself and another.

        Parameters
        ----------
        value : iterable
            The other iterable.
        """

        if value is None:
            return

        value = set(value)
        removed = self.difference(value)
        super().intersection_update(value)

        if len(removed) > 0:
            self.notify(removed, set())

    def symmetric_difference_update(self, value):
        """ Update a set with the symmetric difference of itself and another.

        Parameters
        ----------
        value : iterable
        """

        values = set(value)
        removed = self.intersection(values)
        added = values.difference(removed)
        if added:
            added = {self.item_validator(item) for item in added}
        added = added.difference(self)

        if removed or added:
            super().difference_update(removed)
            super().update(added)
            self.notify(removed, added)

    def discard(self, value):
        """ Remove an element from a set if it is a member.

        If the element is not a member, do nothing.

        Parameters
        ----------
        value : any
            An item in the set
        """

        value_in_self = value in self
        super().discard(value)

        if value_in_self:
            self.notify({value}, set())

    def pop(self):
        """ Remove and return an arbitrary set element.
        Raises KeyError if the set is empty.

        Returns
        -------
        item : any
            An element from the set.
        """

        removed = super().pop()
        self.notify({removed}, set())
        return removed

    def clear(self):
        """ Remove all elements from this set. """

        if not self:
            return
        removed = set(self)
        super().clear()
        self.notify(removed, set())

    # -- pickle and copy support ----------------------------------------------

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """
        # notifiers are transient and should not be copied
        result = TraitSet(
            [copy.deepcopy(x, memo) for x in self],
            item_validator=copy.deepcopy(self.validator, memo),
            notifiers=[],
        )

        return result

    def __getstate__(self):
        """ Get the state of the object for serialization.

        Notifiers are transient and should not be serialized.
        """
        result = self.__dict__.copy()
        # notifiers are transient and should not be serialized
        del result["notifiers"]
        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.

        Notifiers are transient and are restored to the empty list.
        """
        state['notifiers'] = []
        self.__dict__.update(state)

    def __reduce_ex__(self, protocol=None):
        """ Overridden to make sure we call our custom __getstate__.
        """
        return (
            copyreg._reconstructor,
            (type(self), set, list(self)),
            self.__getstate__(),
        )


class TraitSetObject(TraitSet):
    """ A specialization of TraitSet with a default validator and notifier
    for compatibility with Traits versions before 6.0.

    Parameters
    ----------
    trait : CTrait
        The trait that the set has been assigned to.
    object : HasTraits
        The object the set belongs to.
    name : str
        The name of the trait on the object.
    value : iterable
        The initial value of the set.

    Attributes
    ----------
    trait : CTrait
        The trait that the set has been assigned to.
    object : HasTraits
        The object the set belongs to.
    name : str
        The name of the trait on the object.
    value : iterable
        The initial value of the set.
    """

    def __init__(self, trait, object, name, value):

        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        super().__init__(value, item_validator=self._validator,
                         notifiers=[self.notifier])

    def _validator(self, value):
        """ Validates the value by calling the inner trait's validate method.

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
            On validation failure for the inner trait.
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

        try:
            return validate(object, self.name, value)
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
        """

        if self.name_items is None:
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

        result = super().__getstate__()
        result.pop("object", None)
        result.pop("trait", None)

        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.

        Notifiers are transient and are restored to the empty list.
        """

        state.setdefault("name", "")
        state["notifiers"] = [self.notifier]
        state["object"] = lambda: None
        state["trait"] = None
        self.__dict__.update(state)
