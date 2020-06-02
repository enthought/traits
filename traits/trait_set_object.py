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
from itertools import chain
from weakref import ref

from traits.observation._i_observable import IObservable
from traits.trait_base import _validate_everything
from traits.trait_errors import TraitError


class TraitSetEvent(object):
    """ An object reporting in-place changes to a traits sets.

    Parameters
    ----------
    removed : set, optional
        Old values that were removed from the set.
    added : set, optional
        New values added to the set.

    Attributes
    ----------
    removed : set
        Old values that were removed from the set.
    added : set
        New values added to the set.
    """

    def __init__(self, *, removed=None, added=None):

        if removed is None:
            removed = set()
        self.removed = removed

        if added is None:
            added = set()
        self.added = added

    def __repr__(self):
        return "TraitSetEvent(removed={!r}, added={!r})".format(
            self.removed, self.added
        )


@IObservable.register
class TraitSet(set):
    """ A subclass of set that validates and notifies listeners of changes.

    Parameters
    ----------
    value : iterable, optional
        Iterable providing the items for the set.
    item_validator : callable, optional
        Called to validate and/or transform items added to the set. The
        callable should accept a single item and return the transformed
        item, raising TraitError for invalid items. If not given, no
        item validation is performed.
    notifiers : list of callable, optional
        A list of callables with the signature::

            notifier(trait_set, removed, added)

        Where 'added' is a set containing new values that have been added.
        And 'removed' is a set containing old values that have been removed.

        If this argument is not given, the list of notifiers is initially
        empty.

    Attributes
    ----------
    item_validator : callable
        Called to validate and/or transform items added to the set. The
        callable should accept a single item and return the transformed
        item, raising TraitError for invalid items.
    notifiers : list of callable
        A list of callables with the signature::

            notifier(trait_set, removed, added)

        where 'added' is a set containing new values that have been added
        and 'removed' is a set containing old values that have been removed.
    """

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.item_validator = _validate_everything
        self.notifiers = []
        return self

    def __init__(self, value=(), *, item_validator=None, notifiers=None):
        if item_validator is not None:
            self.item_validator = item_validator
        super().__init__(self.item_validator(item) for item in value)
        if notifiers is not None:
            self.notifiers = notifiers

    def notify(self, removed, added):
        """ Call all notifiers.

        This simply calls all notifiers provided by the class, if any.
        The notifiers are expected to have the signature::

            notifier(trait_set, removed, added)

        Any return values are ignored. Any exceptions raised are not
        handled. Notifiers are therefore expected not to raise any
        exceptions under normal use.

        Parameters
        ----------
        removed : set
            The items that have been removed.
        added : set
            The new items that have been added to the set.
        """
        for notifier in self.notifiers:
            notifier(self, removed, added)

    # -- set interface -------------------------------------------------------

    def __iand__(self, value):
        """  Return self &= value.

        Parameters
        ----------
        value : set or frozenset
            A value.

        Returns
        -------
        self : TraitSet
            The updated set.
        """

        old_set = self.copy()
        retval = super().__iand__(value)
        removed = old_set.difference(self)

        if len(removed) > 0:
            self.notify(removed, set())

        return retval

    def __ior__(self, value):
        """ Return self |= value.

        Parameters
        ----------
        value : set or frozenset
            A value.

        Returns
        -------
        self : TraitSet
            The updated set.
        """
        old_set = self.copy()

        # Validate each item in value, only if value is a set or frozenset.
        # We do not want to convert any other iterable type to a set
        # so that super().__ior__ raises the appropriate error message
        # for all other iterables.
        if isinstance(value, (set, frozenset)):
            value = {self.item_validator(item)
                     for item in value}

        retval = super().__ior__(value)

        added = self.difference(old_set)

        if len(added) > 0:
            self.notify(set(), added)

        return retval

    def __isub__(self, value):
        """ Return self-=value.

        Parameters
        ----------
        value : set or frozenset
            A value.

        Returns
        -------
        self : TraitSet
            The updated set.
        """

        old_set = self.copy()
        retval = super().__isub__(value)
        removed = old_set.difference(self)

        if len(removed) > 0:
            self.notify(removed, set())

        return retval

    def __ixor__(self, value):
        """ Return self ^= value.

        Parameters
        ----------
        value : set or frozenset
            A value.

        Returns
        -------
        self : TraitSet
            The updated set.
        """

        removed = set()
        added = set()

        # Validate each item in value, only if value is a set or frozenset.
        # We do not want to convert any other iterable type to a set
        # so that super().__ixor__ raises the appropriate error message
        # for all other iterables.
        if isinstance(value, (set, frozenset)):
            values = set(value)
            removed = self.intersection(values)
            raw_added = values.difference(removed)
            validated_added = {self.item_validator(item) for item in
                               raw_added}
            added = validated_added.difference(self)
            value = added | removed

        retval = super().__ixor__(value)

        if removed or added:
            self.notify(removed, added)

        return retval

    def add(self, value):
        """ Add an element to a set.

        This has no effect if the element is already present.

        Parameters
        ----------
        value : any
            The value to add to the set.
        """

        value = self.item_validator(value)
        value_in_self = value in self
        super().add(value)
        if not value_in_self:
            self.notify(set(), {value})

    def clear(self):
        """ Remove all elements from this set. """

        removed = set(self)
        super().clear()
        if removed:
            self.notify(removed, set())

    def discard(self, value):
        """ Remove an element from the set if it is a member.

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

    def difference_update(self, *args):
        """  Remove all elements of another set from this set.

        Parameters
        ----------
        args : iterables
            The other iterables.
        """

        old_set = self.copy()
        super().difference_update(*args)
        removed = old_set.difference(self)

        if len(removed) > 0:
            self.notify(removed, set())

    def intersection_update(self, *args):
        """  Update the set with the intersection of itself and another set.

        Parameters
        ----------
        args : iterables
            The other iterables.
        """

        old_set = self.copy()
        super().intersection_update(*args)
        removed = old_set.difference(self)

        if len(removed) > 0:
            self.notify(removed, set())

    def pop(self):
        """ Remove and return an arbitrary set element.

        Raises KeyError if the set is empty.

        Returns
        -------
        item : any
            An element from the set.

        Raises
        ------
        KeyError
            If the set is empty.
        """

        removed = super().pop()
        self.notify({removed}, set())
        return removed

    def remove(self, value):
        """ Remove an element that is a member of the set.

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
        self.notify({value}, set())

    def symmetric_difference_update(self, value):
        """ Update the set with the symmetric difference of itself and another.

        Parameters
        ----------
        value : iterable
        """

        values = set(value)
        removed = self.intersection(values)
        raw_result = values.difference(removed)
        validated_result = {self.item_validator(item) for item in raw_result}
        added = validated_result.difference(self)

        super().symmetric_difference_update(removed | added)
        if removed or added:
            self.notify(removed, added)

    def update(self, *args):
        """ Update the set with the union of itself and others.

        Parameters
        ----------
        args : iterables
            The other iterables.
        """

        validated_values = {self.item_validator(item)
                            for item in chain.from_iterable(args)}
        added = validated_values.difference(self)
        super().update(added)

        if len(added) > 0:
            self.notify(set(), added)

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

    # -- Implement IObservable ------------------------------------------------

    def _notifiers(self, force_create):
        """ Return a list of callables where each callable is a notifier.
        The list is expected to be mutated for contributing or removing
        notifiers from the object.

        Parameters
        ----------
        force_create: boolean
            Not used here.
        """
        return self.notifiers


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
        value : any
            The value to be validated.

        Returns
        -------
        value : any
            The validated value.

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

    def notifier(self, trait_set, removed, added):
        """ Converts and consolidates the parameters to a TraitSetEvent and
        then fires the event.

        Parameters
        ----------
        trait_set : set
            The complete set
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

        if getattr(object, self.name) is not self:
            # Workaround having this set inside another container which
            # also uses the name_items trait for notification.
            # Similar to enthought/traits#25
            return

        event = TraitSetEvent(removed=removed, added=added)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)

    # -- pickle and copy support ----------------------------------------------
    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """

        result = TraitSetObject(
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
        del result["object"]
        del result["trait"]
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

    def __reduce_ex__(self, protocol=None):
        """ Overridden to make sure we call our custom __getstate__.
        """
        return (
            copyreg._reconstructor,
            (type(self), set, list(self)),
            self.__getstate__(),
        )
