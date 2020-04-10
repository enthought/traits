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
import logging
from weakref import ref

from traits.trait_base import Undefined
from traits.trait_errors import TraitError

# Set up a logger:
logger = logging.getLogger(__name__)


class TraitDictEvent(object):
    """ An object reporting in-place changes to a traits dict.

    Parameters
    ----------
    added : dict
        New keys and values that were just added.
    changed : dict
        Updated keys and their previous values.
    removed : dict
        Old keys and values that were just removed.

    Attributes
    ----------
    added : dict
        New keys and values that were just added.
    changed : dict
        Updated keys and their previous values.
    removed : dict
        Old keys and values that were just removed.

    """

    def __init__(self, added=None, changed=None, removed=None):
        if added is None:
            added = {}
        self.added = added

        if changed is None:
            changed = {}
        self.changed = changed

        if removed is None:
            removed = {}
        self.removed = removed


# Default item validator for TraitDict.


def accept_anything(item):
    """
    Item validator which accepts any item and returns it unaltered.
    """
    return item


class TraitDict(dict):
    """ A subclass of dict that validates keys and values and notifies
    listeners of any change.

    Parameters
    ----------
    value : dict, optional
        The initial dict.
    key_validator : callable, optional
        Called to validate a key in the dict.
        The callable must accept a single key and
        return a validated key or raise a TraitError
        If not provided, all keys are considered valid.
    value_validator : callable, optional
        Called to validate a value in the dict.
        The callable must accept a single value and
        return a validated value or raise a TraitError
        If not provided, all values are considered valid.
    notifiers : list, optional
        A list of callables with the signature::

            notifier(trait_dict, added, changed, removed)

        Where 'added' is a dict of new key-values that have been added.
        'changed' is a dict with old values previously associated with the key.
        'removed' is a dict of key-values that are no longer in the dictionary.

    Attributes
    ----------
    key_validator : callable, optional
        Called to validate a key in the dict.
        The callable must accept a single key and
        return a validated key or raise a TraitError
        If not provided, all keys are considered valid.
    value_validator : callable, optional
        Called to validate a value in the dict.
        The callable must accept a single value and
        return a validated value or raise a TraitError
        If not provided, all values are considered valid.
    notifiers : list, optional
        A list of callables with the signature::

            notifier(trait_dict, added, changed, removed)

        Where 'added' is a dict of new key-values that have been added.
        'changed' is a dict with old values previously associated with the key.
        'removed' is a dict of key-values that are no longer in the dictionary.

    """

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.key_validator = accept_anything
        self.value_validator = accept_anything
        self.notifiers = []
        return self

    def __init__(self, value=None, *, key_validator=None,
                 value_validator=None, notifiers=None):

        if key_validator is not None:
            self.key_validator = key_validator

        if value_validator is not None:
            self.value_validator = value_validator

        if notifiers is None:
            notifiers = []
        self.notifiers = list(notifiers)

        if value is None:
            value = {}

        value = {self.key_validator(key): self.value_validator(value)
                 for key, value in value.items()}

        super().__init__(value)

    def notify(self, added, changed, removed):
        """ Call all notifiers.

        This simply calls all notifiers provided by the class, if any.
        The notifiers are expected to have the signature::

            notifier(trait_dict, added, changed, removed)

        Any return values are ignored.

        """

        for notifier in self.notifiers:
            notifier(self, added, changed, removed)

    # -- dict interface -------------------------------------------------------

    def __setitem__(self, key, value):
        """ Set a value for the key, implements self[key] = value.

        Parameters
        ----------
        key : A hashable type.
            The key for the value.
        value : any
            The value to set for the corresponding key.

        """

        removed = {}
        validated_key = self.key_validator(key)
        validated_value = self.value_validator(value)

        if key in self:
            changed = {key: self[key]}
            added = {}
        else:
            changed = {}
            added = {validated_key: validated_value}

        super().__setitem__(validated_key, validated_value)
        self.notify(added, changed, removed)

    def __delitem__(self, key):
        """ Delete the item from the dict indicated by the key.

        Parameters
        ----------
        key : A hashable type.
            The key to be deleted.

        Raises
        ------
        KeyError
            If the key is not found.


        """
        removed = {key: self[key]}
        super().__delitem__(key)
        self.notify(added={}, changed={}, removed=removed)

    def clear(self):
        """ Remove all items from the dict. """
        if self != {}:
            removed = self.copy()
            super().clear()
            self.notify(added={}, changed={}, removed=removed)

    def update(self, adict):
        """ Update the values in the dict by the new dict.

        Parameters
        ----------
        adict : dict
            The dict from which values will be updated into this dict.
        """

        validated_dict = {}
        added = {}
        changed = {}

        for key, value in adict.items():
            validated_key = self.key_validator(key)
            validated_value = self.value_validator(value)

            if key in self:
                changed[key] = self[key]
            else:
                added[validated_key] = validated_value

            validated_dict[validated_key] = validated_value

        super().update(validated_dict)
        self.notify(added=added, changed=changed, removed={})

    def setdefault(self, key, value=None):
        """ Returns the value if key is present in the dict, else creates the
        key-value pair and returns the value.

        Parameters
        ----------
        key : A hashable type.
            Key to the item.
        """

        if key in self:
            return self[key]

        key = self.key_validator(key)
        value = self.value_validator(value)

        if key in self:
            changed = {key: self[key]}
            added = {}
        else:
            changed = {}
            added = {key: value}

        super().__setitem__(key, value)

        self.notify(added=added, changed=changed, removed={})

        return value

    def pop(self, key, value=Undefined):
        """ Remove specified key and return the corresponding
        value. If key is not found, the default value is returned
        if given, otherwise KeyError is raised.

        Parameters
        ----------
        key : A hashable type.
            Key to the dict item.

        value : any
            Value to return if key is absent.
        """

        if value is Undefined or key in self:
            removed = super().pop(key)
            self.notify(
                added={},
                changed={},
                removed={key: removed}
            )
            return removed
        return value

    def popitem(self):
        """ Remove and return some(key, value) pair as a tuple. Raise KeyError
        if dict is empty.

        Returns
        -------
        key_value : tuple
            Some 2-tuple from the dict.

        Raises
        ------
        KeyError
            If the dict is empty
        """

        item = super().popitem()
        self.notify(added={}, changed={}, removed=dict([item]))
        return item

    # -- pickle and copy support ----------------------------------------------

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

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """
        result = TraitDict(
            dict(copy.deepcopy(x, memo) for x in self.items()),
            key_validator=copy.deepcopy(self.key_validator, memo),
            value_validator=copy.deepcopy(self.value_validator, memo),
            notifiers=[]
        )
        return result


class TraitDictObject(TraitDict):
    """ A subclass of TraitDict that fires trait events when mutated.
    This is for backward compatibility with Traits 6.0 and lower.

    This is used by the Dict trait type, and all values set into a Dict
    trait will be copied into a new TraitDictObject instance.

    Mutation of the TraitDictObject will fire a "name_items" event with
    appropriate added, changed and removed values.

    Parameters
    ----------
    trait : CTrait instance
        The CTrait instance associated with the attribute that this dict
        has been set to.
    object : HasTraits instance
        The HasTraits instance that the dict has been set as an attribute for.
    name : str
        The name of the attribute on the object.
    value : dict
        The dict of values to initialize the TraitDictObject with.

    Attributes
    ----------
    trait : CTrait instance
        The CTrait instance associated with the attribute that this dict
        has been set to.
    object : weak reference to a HasTraits instance
        A weak reference to a HasTraits instance that the dict has been set
        as an attribute for.
    name : str
        The name of the attribute on the object.
    name_items : str
        The name of the items event trait that the trait dict will fire when
        mutated.
    """

    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        super().__init__(value, key_validator=self._key_validator,
                         value_validator=self._value_validator,
                         notifiers=[self.notifier])

    def _key_validator(self, key):
        """ Calls the trait's key_trait.handler.validate.

        Parameters
        ----------
        key : A hashable type.
            The key to validate.

        Returns
        -------
        validated_key : A hashable type.
            The validated key.

        Raises
        ------
        TraitError
            If the validation fails.

        """
        trait = getattr(self, 'trait', None)
        object_ref = getattr(self, 'object', None)
        if object_ref is None or trait is None:
            return key

        object = object_ref()

        validate = trait.key_trait.handler.validate
        if validate is None:
            return key

        try:
            return validate(object, self.name, key)
        except TraitError as excep:
            excep.set_prefix("Each key of the")
            raise excep

    def _value_validator(self, value):
        """ Calls the trait's value_handler.validate

        Parameters
        ----------
        value : any
            The value to validate.

        Returns
        -------
        validated_value : any
            The validated value.

        Raises
        ------
        TraitError
            If the validation fails.

        """
        trait = getattr(self, 'trait', None)
        object_ref = getattr(self, 'object', None)
        if object_ref is None or trait is None:
            return value

        object = object_ref()

        validate = trait.value_handler.validate
        if validate is None:
            return value

        try:
            return validate(object, self.name, value)
        except TraitError as excep:
            excep.set_prefix("Each value of the")
            raise excep

    def notifier(self, trait_dict, added, changed, removed):
        """ Fire the TraitDictEvent with the provided parameters.

        Parameters
        ----------
        trait_dict : dict
            The complete dictionary.
        added : dict
            Dict of added items.
        changed : dict
            Dict of changed items.
        removed : dict
            Dict of removed items.

        Returns
        -------
        None

        """
        trait = getattr(self, 'trait', None)
        name_items = getattr(self, 'name_items', None)
        object_ref = getattr(self, 'object', None)
        if trait is None or name_items is None or object_ref is None:
            return

        object = object_ref()

        if object is None:
            return

        event = TraitDictEvent(added, changed, removed)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)

    # -- pickle and copy support ----------------------------------------------

    def __getstate__(self):
        """ Get the state of the object for serialization.

        Object and trait should not be serialized.
        """

        result = super().__getstate__()
        del result["object"]
        del result["trait"]
        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.
        """

        state.setdefault("name", "")
        state["notifiers"] = [self.notifier]
        state["object"] = lambda: None
        state['trait'] = None
        self.__dict__.update(state)

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation..

        Object is a weakref and should not be copied.
        """
        result = TraitDictObject(
            self.trait,
            lambda: None,
            self.name,
            dict(copy.deepcopy(x, memo) for x in self.items()),
        )

        return result
