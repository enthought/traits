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

from .trait_base import Undefined
from .trait_errors import TraitError

# Set up a logger:
logger = logging.getLogger(__name__)


class TraitDictEvent(object):
    """ An object reporting in-place changes to a traits dict.

    Parameters
    ----------
    added : dict or None
        New keys and values, or optionally None if nothing was added.
    changed : dict or None
        Updated keys and their previous values, or optionally None if nothing
        was changed.
    removed : dict or None
        Old keys and values that were just removed, or optionally None if
        nothing was removed.

    Attributes
    ----------
    added : dict
        New keys and values.  If nothing was added this is an empty dict.
    changed : dict
        Updated keys and their previous values.  If nothing was changed this
        is an empty dict.
    removed : dict
        Old keys and values that were just removed.  If nothing was removed
        this is an empty dict.
    """

    def __init__(self, added=None, changed=None, removed=None):
        # Construct new empty dicts every time instead of using a default value
        # in the method argument, just in case someone gets the bright idea of
        # modifying the dict they get in-place.
        if added is None:
            added = {}
        self.added = added

        if changed is None:
            changed = {}
        self.changed = changed

        if removed is None:
            removed = {}
        self.removed = removed


class TraitDict(dict):

    def validate_key(self, key):
        if getattr(self, 'key_validator', None) is None:
            return key
        else:
            try:
                return self.key_validator(key)
            except TraitError as excep:
                excep.set_prefix("Each key of the")
                raise excep

    def validate_value(self, value):
        if getattr(self, 'value_validator', None) is None:
            return value
        else:
            try:
                return self.value_validator(value)
            except TraitError as excep:
                excep.set_prefix("Each value of the")
                raise excep

    def validate_dict(self, seq):
        if isinstance(seq, dict):
            items = seq.items()
        else:
            items = seq

        validated_items = []
        added = []
        changed = []
        for key, value in items:
            key = self.validate_key(key)
            value = self.validate_value(value)
            validated_items.append((key, value))
            if key in self:
                changed.append((key, value))
            else:
                added.append((key, value))
        return dict(validated_items), dict(added), dict(changed)

    def notifiy(self, added={}, changed={}, removed={}):

        if added is None:
            added = {}
        if changed is None:
            changed = {}
        if removed is None:
            removed = {}

        for notifier in getattr(self, 'notifiers', []):
            notifier(self, added, changed, removed)

    def __init__(self, value={}, *, key_validator=None, value_validator=None,
                 notifiers=()):
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.notifiers = list(notifiers)
        value, _, _ = self.validate_dict(value)
        super().__init__(value)

    def __deepcopy__(self, memo):
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

    def __setitem__(self, key, value):
        key = self.validate_key(key)
        value = self.validate_value(value)

        entry = {key: value}
        added = changed = removed = {}

        if key in self:
            changed = entry
        else:
            added = entry

        self.notifiy(added, changed, removed)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        key = self.key_validator(key)
        if key in self:
            removed = {key: self[key]}
            self.notifiy(removed=removed)
            super().__delitem__(key)

    def clear(self):
        if self != {}:
            removed = self.copy()
            self.notifiy(removed=removed)
            super().clear()

    def update(self, dic):
        validated_dict, added, changed = self.validate_dict(dic)
        self.notifiy(added, changed)
        super().update(validated_dict)

    def setdefault(self, key, value=None):
        key = self.key_validator(key)
        if key in self:
            return self[key]

        self[key] = value
        added = {key: value}
        self.notifiy(added)
        return value

    def pop(self, key, value):
        key = self.key_validator(key)
        if key in self:
            removed = {key: self[key]}
            result = super().pop(key)
            self.notifiy(removed=removed)
            return result
        else:
            return value

    def popitem(self):
        item = super().popitem()
        self.notifiy(removed=dict([item]))
        return item

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


class TraitDictObject(TraitDict):
    def __init__(self, trait, object, name, value, notifiers=[]):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        super().__init__(value, key_validator=self.key_validator,
                         value_validator=self.value_validator,
                         notifiers=[self.notifier] + notifiers)

    def __deepcopy__(self, memo):
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
        result = self.__dict__.copy()
        result.pop("object", None)
        result.pop("trait", None)
        return result

    def __setstate__(self, state):
        name = state.setdefault("name", "")
        object = state.pop("object", None)
        if object is not None:
            state[object] = ref(object)
            trait = self.object()._trait(name, 0)
            if trait is not None:
                state['trait'] = trait.handler

        else:
            state['object'] = lambda: None
            state['trait'] = None

        self.__dict__.update(state)

    def key_validator(self, key):
        object = self.object()
        trait = self.trait
        if object is None or trait is None:
            return key

        validate = trait.key_trait.handler.validator
        if validate is None:
            return key

        return self.validate(object, self.name, key)

    def value_validator(self, value):
        object = self.object()
        trait = self.trait
        if object is None or trait is None:
            return value

        validate = trait.value_trait.handler.validator
        if validate is None:
            return value

        return self.validate(object, self.name, value)

    def notifier(self, trait_list, added, changed, removed):
        is_trait_none = self.trait is None
        is_name_items_none = self.name_items is None
        if not hasattr(self, "trait") or is_trait_none or is_name_items_none:
            return
        object = self.object()
        if object is None:
            return

        event = TraitDictEvent(added, changed, removed)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)
