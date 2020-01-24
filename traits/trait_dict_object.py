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


class TraitDictObject(dict):
    """ A subclass of dict that fires trait events when mutated.

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

        if len(value) > 0:
            dict.update(self, self._validate_dic(value))

    def _send_trait_items_event(self, name, event, items_event=None):
        """ Send a TraitDictEvent to the owning object if there is one.
        """
        object = self.object()
        if object is not None:
            if items_event is None and hasattr(self, "trait"):
                items_event = self.trait.items_event()
            object.trait_items_event(name, event, items_event)

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

    def __setitem__(self, key, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            dict.__setitem__(self, key, value)
            return

        object = self.object()
        try:
            validate = trait.key_trait.handler.validate
            if validate is not None:
                key = validate(object, self.name, key)

        except TraitError as excp:
            excp.set_prefix("Each key of the")
            raise excp

        try:
            validate = trait.value_handler.validate
            if validate is not None:
                value = validate(object, self.name, value)

            if self.name_items is not None:
                if key in self:
                    added = None
                    old = self[key]
                    changed = {key: old}
                else:
                    added = {key: value}
                    changed = None

            dict.__setitem__(self, key, value)

            if self.name_items is not None:
                if added is None:
                    try:
                        if old == value:
                            return
                    except Exception:
                        # Treat incomparable objects as unequal:
                        pass
                self._send_trait_items_event(
                    self.name_items,
                    TraitDictEvent(added, changed),
                    trait.items_event(),
                )

        except TraitError as excp:
            excp.set_prefix("Each value of the")
            raise excp

    def __delitem__(self, key):
        if self.name_items is not None:
            removed = {key: self[key]}

        dict.__delitem__(self, key)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitDictEvent(removed=removed)
            )

    def clear(self):
        if len(self) > 0:
            if self.name_items is not None:
                removed = self.copy()

            dict.clear(self)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitDictEvent(removed=removed)
                )

    def update(self, dic):
        trait = getattr(self, "trait", None)
        if trait is None:
            dict.update(self, dic)
            return

        if len(dic) > 0:
            new_dic = self._validate_dic(dic)

            if self.name_items is not None:
                added = {}
                changed = {}
                for key, value in new_dic.items():
                    if key in self:
                        changed[key] = self[key]
                    else:
                        added[key] = value

                dict.update(self, new_dic)

                self._send_trait_items_event(
                    self.name_items,
                    TraitDictEvent(added=added, changed=changed),
                )
            else:
                dict.update(self, new_dic)

    def setdefault(self, key, value=None):
        if key in self:
            return self[key]

        self[key] = value
        result = self[key]

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitDictEvent(added={key: result})
            )

        return result

    def pop(self, key, value=Undefined):
        if (value is Undefined) or key in self:
            result = dict.pop(self, key)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitDictEvent(removed={key: result})
                )

            return result

        return value

    def popitem(self):
        result = dict.popitem(self)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitDictEvent(removed={result[0]: result[1]})
            )

        return result

    def rename(self, name):
        trait = self.object()._trait(name, 0)
        if trait is not None:
            self.name = name
            self.trait = trait.handler
        else:
            logger.debug(
                "rename: No 'trait' in %s for '%s'" % (self.object(), name)
            )

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

    # -- Private Methods ------------------------------------------------------------

    def _validate_dic(self, dic):
        name = self.name
        new_dic = {}

        key_validate = self.trait.key_trait.handler.validate
        if key_validate is None:
            key_validate = lambda object, name, key: key

        value_validate = self.trait.value_trait.handler.validate
        if value_validate is None:
            value_validate = lambda object, name, value: value

        object = self.object()
        for key, value in dic.items():
            try:
                key = key_validate(object, name, key)
            except TraitError as excp:
                excp.set_prefix("Each key of the")
                raise excp

            try:
                value = value_validate(object, name, value)
            except TraitError as excp:
                excp.set_prefix("Each value of the")
                raise excp

            new_dic[key] = value

        return new_dic
