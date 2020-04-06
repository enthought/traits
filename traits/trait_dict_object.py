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
        New keys and values or None.
    changed : dict
        Updated keys and their previous values or None.
    removed : dict
        Old keys and values that were just removed or None.

    Attributes
    ----------
    added : dict
        New keys and values or None.
    changed : dict
        Updated keys and their previous values or None.
    removed : dict
        Old keys and values that were just removed or None.

    """

    def __init__(self, added=None, changed=None, removed=None):
        self.added = added
        self.changed = changed
        self.removed = removed


class TraitDict(dict):
    """ A subclass of dict that validates keys and values and notifies
    listeners of any change.

    Parameters
    ----------
    value : dict
        The initial dict.
    key_validator : callable
        Called to validate a key in the dict.
    value_validator : callable
        Called to validate a value in the dict.

    Attributes
    ----------
    value : dict
        The initial dict.
    key_validator : callable
        Called to validate a key in the dict.
    value_validator : callable
        Called to validate a value in the dict.

    """

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.key_validator = None
        instance.value_validator = None
        instance.notifiers = []
        return instance

    def __init__(self, value={}, *, key_validator=None,
                 value_validator=None, notifiers=None):
        self.key_validator = key_validator
        self.value_validator = value_validator

        if notifiers is None:
            notifiers = []

        self.notifiers = list(notifiers)

        value, _, _ = self._validate_dict(value)

        super().__init__(value)

    # ------------------------------------------------------------------------
    # TraitDict interface
    # ------------------------------------------------------------------------

    def validate_key(self, key):
        """ Validates the key with the key_validator for the TraitDict

        Parameters
        ----------
        key : A hashable type.
            The key to be validated.

        Returns
        -------
        validated_key : A hashable type.
            The validated key.

        Raises
        ------
        TraitError
            If the value cannot be validated.

        """
        return self._validate(self.key_validator, key, msg="Each key of the")

    def validate_value(self, value):
        """ Validates the value with the value_validator for the TraitDict.

        Parameters
        ----------
        value : any
            The value to be validated.

        Returns
        -------
        validated_value : any
            The validated value.

        Raises
        ------
        TraitError
            If the value cannot be validated.
        """
        return self._validate(self.value_validator, value,
                              msg="Each value of the")

    def notifiy(self, added={}, changed={}, removed={}):
        """ Call all notifiers.

        This simply calls all notifiers provided by the class, if any.
        The notifiers are expected to have the signature::

            notifier(trait_dict, added, changed, removed)

        Any return values are ignored.

        Parameters
        ----------
        added : dict
            A dictionary of items that were added to the dict.
        changed : dict
            A dictionary of items that were changed in the dict. This will
            contain the values before the change.
        removed : dict
            A dictionary of items that were removed from the dict.
        """

        for notifier in self.notifiers:
            notifier(self, added, changed, removed)

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation.

        Notifiers are transient and should not be copied.
        """

        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitDict(
            dict(copy.deepcopy(x, memo) for x in self.items()),
            key_validator=copy.deepcopy(self.key_validator, memo),
            value_validator=copy.deepcopy(self.value_validator, memo),
            notifiers=[]
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

    # ------------------------------------------------------------------------
    # dict interface
    # ------------------------------------------------------------------------

    def __setitem__(self, key, value):
        """ Set a value for the key, implements self[key] = value.

        Parameters
        ----------
        key : A hashable type.
            The key for the value.
        value : any
            The value to set for the corresponding key.

        Notes
        -----
        Parameters in the notification:
            added : dict
                The dict of the item that was added.
            changed : dict
                A dict of the previous key value pair, if the key was present,
                else an empty dict.
            removed : dict
                Will be an empty dict.

        """
        validated_key = self.validate_key(key)
        validated_value = self.validate_value(value)

        added = changed = removed = {}

        if validated_key in self:
            changed = {validated_key: self[validated_key]}
        else:
            added = {validated_key: validated_value}

        super().__setitem__(validated_key, validated_value)
        self.notifiy(added, changed, removed)

    def __delitem__(self, key):
        """ Delete the item from the dict indicated by the key.

        Parameters
        ----------
        key : A hashable type.
            The key to be deleted.

        Notes
        -----
        Parameters in the notification:
            added : dict
                Will be an empty dict.
            changed : dict
                Will be an empty dict.
            removed : dict
                The dict of the item that was removed.

        """
        removed = {key: self[key]}
        super().__delitem__(key)
        self.notifiy(added={}, changed={}, removed=removed)

    def clear(self):
        """ Remove all items from the dict.

        Notes
        -----
        Parameters in the notification:
            added : dict
                Will be an empty dict.
            changed : dict
                Will be an empty dict.
            removed : dict
                A copy of the dict before it was removed.

        """
        if self != {}:
            removed = self.copy()
            super().clear()
            self.notifiy(removed=removed)

    def update(self, adict):
        """ Update the values in the dict by the new dict.

        Parameters
        ----------
        adict : dict
            The dict from which values will be updated into this dict.

        Notes
        -----
        Parameters in the notification:
            added : dict
                The dict of the item that was added.
            changed : dict
                The dict of the item that was changed.
            removed : dict
                Will be an empty dict.

        """

        validated_dict, added, changed = self._validate_dict(adict)
        super().update(validated_dict)
        self.notifiy(added, changed)

    def setdefault(self, key, value=None):
        """ Returns the value if key is present in the dict, else creates the
        key-value pair and returns the value.

        Parameters
        ----------
        key : A hashable type.
            Key to the item.

        Notes
        -----
        Parameters in the notification:
            added : dict
                The dict of the item that was added, notification is fired
                only if the key was absent.
            changed : dict
                The dict of the item that was changed.
            removed : dict
                Will be an empty dict.

        """
        if key in self:
            return self[key]

        key = self.validate_key(key)
        value = self.validate_value(value)

        if key in self:
            changed = {key: self[key]}
            added = {}
        else:
            changed = {}
            added = {key: value}

        super().__setitem__(key, value)

        self.notifiy(added=added, changed=changed, removed={})

        return value

    def pop(self, key, value=Undefined):
        """ Remove the key from the dict if present and return the key-value
        pair. If key is absent, the default value is returned and the dict
        is left unmodified.

        Parameters
        ----------
        key : A hashable type.
            Key to the dict item.

        value : any
            Value to return if key is absent.

        Notes
        -----
        Parameters in the notification:
            added : dict
                Will be an empty dict
            changed : dict
                The dict of the item that was changed
            removed : dict
                The dict of the item that was removed, notification fired only
                if the key was present.

        """
        if value is Undefined or key in self:
            removed = super().pop(key)
            self.notifiy(
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

        Notes
        -----
        Parameters in the notification:
            added : dict
                Will be an empty dict
            changed : dict
                Will be an empty dict
            removed : dict
                The dict of the item that was removed.

        """
        item = super().popitem()
        self.notifiy(removed=dict([item]))
        return item

    # ------------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------------

    def _validate_dict(self, adict):
        """ A convenience method to validate each of the key value pairs in a
        dictionary and return the validated dict, a dict of added items and
        a dict of changed items.

        Parameters
        ----------
        adict : dict
            The dictionary to validate

        Returns
        -------
        validated_dict : dict
            The validated dict.
        added : dict
            The added items as a dict.
        changed : dict
            The changed items as a dict.

        """

        validated_items = []
        added = []
        changed = []

        for key, value in adict.items():
            key = self.validate_key(key)
            value = self.validate_value(value)
            validated_items.append((key, value))
            if key in self:
                changed.append((key, self[key]))
            else:
                added.append((key, value))

        return dict(validated_items), dict(added), dict(changed)

    def _validate(self, validator, value, msg=""):
        """ Calls the validator with the value as an argument and returns
        a validated value or raises an error.

        Parameters
        ----------
        validator : callable
            The validator callable
        value : any
            The value to be validated.
        msg : str
            Error message on failure.

        Returns
        -------
        validated_value : any
            The validated value.

        Raises
        ------
        TraitError
            If the value cannot be validated.

        """
        if validator is None:
            return value
        else:
            try:
                return validator(value)
            except TraitError as excep:
                excep.set_prefix(msg)
                raise excep


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

    def key_validator(self, key):
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

        return validate(object, self.name, key)

    def value_validator(self, value):
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

        return validate(object, self.name, value)

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

        if object is None or not hasattr(self, "trait"):
            return

        event = TraitDictEvent(added, changed, removed)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)

    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        super().__init__(value, key_validator=self.key_validator,
                         value_validator=self.value_validator,
                         notifiers=[self.notifier])

    def __deepcopy__(self, memo):
        """ Perform a deepcopy operation..

        Object is a weakref and should not be copied.
        """
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitDictObject(
            self.trait,
            lambda: None,
            self.name,
            dict(copy.deepcopy(x, memo) for x in self.items()),
        )

        return result

    def __getstate__(self):
        """ Get the state of the object for serialization.

        Object and trait should not be serialized.
        """

        result = super().__getstate__()
        result.pop("object", None)
        result.pop("trait", None)
        return result

    def __setstate__(self, state):
        """ Restore the state of the object after serialization.
        """

        state.setdefault("name", "")
        state["notifiers"] = [self.notifier]
        state["object"] = lambda: None
        state['trait'] = None
        self.__dict__.update(state)
