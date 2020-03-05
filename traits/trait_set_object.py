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

from .trait_errors import TraitError


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


class TraitSetObject(set):
    """ A subclass of set that fires trait events when mutated.

    This is used by the Set trait type, and all values set into a Set
    trait will be copied into a new TraitSetObject instance.

    Mutation of the TraitSetObject will fire a "name_items" event with
    appropriate added and removed values.

    Parameters
    ----------
    trait : CTrait instance
        The CTrait instance associated with the attribute that this Set
        has been set to.
    object : HasTraits instance
        The HasTraits instance that the set has been set as an attribute for.
    name : str
        The name of the attribute on the object.
    value : set
        The set of values to initialize the TraitSetObject with.

    Attributes
    ----------
    trait : CTrait instance
        The CTrait instance associated with the attribute that this set
        has been set to.
    object : weak reference to a HasTraits instance
        A weak reference to a HasTraits instance that the set has been set
        as an attribute for.
    name : str
        The name of the attribute on the object.
    name_items : str
        The name of the items event trait that the trait set will fire when
        mutated.
    """

    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        # Validate and assign the initial set value:
        try:
            validate = trait.item_trait.handler.validate
            if validate is not None:
                value = [validate(object, name, val) for val in value]

            super(TraitSetObject, self).__init__(value)

            return

        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def _send_trait_items_event(self, name, event, items_event=None):
        """ Send a TraitSetEvent to the owning object if there is one.
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

        memo[id_self] = result = TraitSetObject(
            self.trait,
            lambda: None,
            self.name,
            [copy.deepcopy(x, memo) for x in self],
        )

        return result

    def update(self, value):
        if not hasattr(self, "trait"):
            return set.update(self, value)
        try:
            if not isinstance(value, set):
                value = set(value)
            added = value.difference(self)
            if len(added) > 0:
                object = self.object()
                validate = self.trait.item_trait.handler.validate
                if validate is not None:
                    name = self.name
                    added = set(
                        [validate(object, name, item) for item in added]
                    )

                set.update(self, added)

                if self.name_items is not None:
                    self._send_trait_items_event(
                        self.name_items, TraitSetEvent(None, added)
                    )
        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def intersection_update(self, value):
        removed = self.difference(value)
        if len(removed) > 0:
            set.difference_update(self, removed)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitSetEvent(removed)
                )

    def difference_update(self, value):
        removed = self.intersection(value)
        if len(removed) > 0:
            set.difference_update(self, removed)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitSetEvent(removed)
                )

    def symmetric_difference_update(self, value):
        if not hasattr(self, "trait"):
            return set.symmetric_difference_update(self, value)
        if not isinstance(value, set):
            value = set(value)
        removed = self.intersection(value)
        added = value.difference(self)
        if (len(removed) > 0) or (len(added) > 0):
            object = self.object()
            set.difference_update(self, removed)

            if len(added) > 0:
                validate = self.trait.item_trait.handler.validate
                if validate is not None:
                    name = self.name
                    added = set(
                        [validate(object, name, item) for item in added]
                    )

                set.update(self, added)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitSetEvent(removed, added)
                )

    def add(self, value):
        if not hasattr(self, "trait"):
            return set.add(self, value)
        if value not in self:
            try:
                object = self.object()
                validate = self.trait.item_trait.handler.validate
                if validate is not None:
                    value = validate(object, self.name, value)

                set.add(self, value)

                if self.name_items is not None:
                    self._send_trait_items_event(
                        self.name_items, TraitSetEvent(None, set([value]))
                    )
            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

    def remove(self, value):
        set.remove(self, value)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitSetEvent(set([value]))
            )

    def discard(self, value):
        if value in self:
            self.remove(value)

    def pop(self):
        value = set.pop(self)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitSetEvent(set([value]))
            )

        return value

    def clear(self):
        removed = set(self)
        set.clear(self)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitSetEvent(removed)
            )

    def __reduce_ex__(self, protocol=None):
        """ Overridden to make sure we call our custom __getstate__.
        """
        return (
            copyreg._reconstructor,
            (type(self), set, list(self)),
            self.__getstate__(),
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

    def __ior__(self, value):
        self.update(value)
        return self

    def __iand__(self, value):
        self.intersection_update(value)
        return self

    def __ixor__(self, value):
        self.symmetric_difference_update(value)
        return self

    def __isub__(self, value):
        self.difference_update(value)
        return self
