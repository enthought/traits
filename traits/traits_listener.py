# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines classes used to implement and manage various trait listener
    patterns.
"""

import re
import string
import weakref
from string import whitespace
from types import MethodType

from .constants import DefaultValue
from .trait_base import Undefined, Uninitialized
from .trait_errors import TraitError
from .trait_notifiers import TraitChangeNotifyWrapper
from .util.weakiddict import WeakIDKeyDict

# Constants

# The name of the dictionary used to store active listeners
TraitsListener = "__traits_listener__"

# End of String marker
EOS = "\0"

# Types of traits that can be listened to

ANYTRAIT_LISTENER = "_register_anytrait"
SIMPLE_LISTENER = "_register_simple"
LIST_LISTENER = "_register_list"
DICT_LISTENER = "_register_dict"
SET_LISTENER = "_register_set"

# Mapping from trait default value types to listener types
type_map = {
    DefaultValue.trait_list_object: LIST_LISTENER,
    DefaultValue.trait_dict_object: DICT_LISTENER,
    DefaultValue.trait_set_object: SET_LISTENER,
}

# Listener types:
ANY_LISTENER = 0
SRC_LISTENER = 1
DST_LISTENER = 2

ListenerType = {
    0: ANY_LISTENER,
    1: DST_LISTENER,
    2: DST_LISTENER,
    3: SRC_LISTENER,
    4: SRC_LISTENER,
}

# Invalid destination (object, name) reference marker (i.e. ambiguous):
INVALID_DESTINATION = (None, None)

# Regular expressions used by the parser:
simple_pat = re.compile(r"^([a-zA-Z_]\w*)(\.|:)([a-zA-Z_]\w*)$")
name_pat = re.compile(r"([a-zA-Z_]\w*)\s*(.*)")

# Characters valid in a traits name:
name_chars = string.ascii_letters + string.digits + "_"


# Utility functions

def indent(text, first_line=True, n=1, width=4):
    """ Indent lines of text.

    Parameters
    ----------
    text : str
        The text to indent.
    first_line : bool, optional
        If False, then the first line will not be indented (default: True).
    n : int, optional
        The level of indentation (default: 1).
    width : int, optional
        The number of spaces in each level of indentation (default: 4).

    Returns
    -------
    indented : str
    """
    lines = text.split("\n")
    if not first_line:
        first = lines[0]
        lines = lines[1:]

    spaces = " " * (width * n)
    lines2 = [spaces + x for x in lines]

    if not first_line:
        lines2.insert(0, first)

    indented = "\n".join(lines2)

    return indented


# Metadata filters

def is_not_none(value):
    return value is not None


def is_none(value):
    return value is None


def not_event(value):
    return value != "event"


class ListenerBase:
    """
    Abstract base class for both ListenerItem and ListenerGroup.
    """

    def set_notify(self, notify):
        """ Set notify state on this listener.

        Parameters
        ----------
        notify : bool
            True if this listener should notify, else False.
        """
        raise NotImplementedError

    def set_next(self, next):
        """ Set the child listener for this listener.

        Parameters
        ----------
        next : ListenerBase
            The next level (if any) of ListenerBase object to be called when
            any of our listened to traits is changed:
        """
        raise NotImplementedError

    def register(self, new):
        """ Registers new listeners.
        """
        raise NotImplementedError

    def unregister(self, old):
        """ Unregisters any existing listeners.
        """
        raise NotImplementedError

    def handle(self, object, name, old, new):
        """ Handles a trait change for a simple trait.
        """
        raise NotImplementedError

    def handle_list(self, object, name, old, new):
        """ Handles a trait change for a list trait.
        """
        raise NotImplementedError

    def handle_list_items(self, object, name, old, new):
        """ Handles a trait change for a list traits items.
        """
        raise NotImplementedError

    def handle_dict(self, object, name, old, new):
        """ Handles a trait change for a dictionary trait.
        """
        raise NotImplementedError

    def handle_dict_items(self, object, name, old, new):
        """ Handles a trait change for a dictionary traits items.
        """
        raise NotImplementedError


class ListenerItem(ListenerBase):
    """
    Listener description for a single item.

    Parameters
    ----------
    name : str
        The name of the trait to listen to.
    metadata_name : str, optional
        The name of any metadata that must be present (or not present).
    metadata_defined : bool, optional
        True if the specified metadata needs to be defined; False if the
        specified metadata needs to be not defined.
    handler : ListenerHandler, optional
        Zero-argument callable that returns the actual handler when called (or
        Undefined if that handler is no longer available).
    wrapped_handler_ref : weakref.ref, optional
        Weak reference to a ListenerNotifyWrapper wrapping the actual handler.
    dispatch : str
        The dispatch mechanism to use when invoking the handler.
    priority : bool, optional
        True if the handler goes at the beginning of the notification handlers
        list, else False.
    next : ListenerBase or None, optional
        The next level (if any) of ListenerBase object to be called when any
        of this object's listened-to traits is changed. The default is None.
    type : int
        The type of handler being used. One of ANY_LISTENER, SRC_LISTENER,
        DST_LISTENER.
    notify : bool, optional
        True if changes to this item should generate a notification to
        the handler; False otherwise. The default is True.
    deferred : bool, optional
        True if registering listeners for items reachable from this listener
        item should be deferred until the associated trait is first read or
        set.
    is_anytrait : bool, optional
        True if this is an "anytrait" change listener. False if it creates
        explicit listeners for each individual trait.
    is_list_handler : bool, optional
        True if the associated handler is a special list handler that handles
        both "foo" and "foo_items" events. False otherwise.
    """

    def __init__(
        self,
        *,
        name,
        metadata_name="",
        metadata_defined=True,
        handler=None,
        wrapped_handler_ref=None,
        dispatch,
        priority=False,
        next=None,
        type,
        notify=True,
        deferred=False,
        is_anytrait=False,
        is_list_handler=False,
    ):
        self.name = name
        self.notify = notify
        self.handler = handler
        self.wrapped_handler_ref = wrapped_handler_ref
        self.dispatch = dispatch
        self.priority = priority
        self.deferred = deferred
        self.type = type
        self.next = next
        self.metadata_name = metadata_name
        self.metadata_defined = metadata_defined
        self.is_anytrait = is_anytrait
        self.is_list_handler = is_list_handler
        self.active = WeakIDKeyDict()
        self._metadata = None

    # -- 'ListenerBase' Class Method Implementations --------------------------

    def __repr__(self, seen=None):
        """Returns a string representation of the object.

        Since the object graph may have cycles, we extend the basic __repr__
        API to include a set of objects we've already seen while constructing
        a string representation. When this method tries to get the repr of
        a ListenerItem or ListenerGroup, we will use the extended API and build
        up the set of seen objects. The repr of a seen object will just be
        '<cycle>'.
        """
        if seen is None:
            seen = set()

        seen.add(self)
        next_repr = "None"
        next = self.next
        if next is not None:
            if next in seen:
                next_repr = "<cycle>"
            else:
                next_repr = next.__repr__(seen)

        return """%s(
    name = %r,
    metadata_name = %r,
    metadata_defined = %r,
    is_anytrait = %r,
    dispatch = %r,
    notify = %r,
    is_list_handler = %r,
    type = %r,
    next = %s,
)""" % (
            self.__class__.__name__,
            self.name,
            self.metadata_name,
            self.metadata_defined,
            self.is_anytrait,
            self.dispatch,
            self.notify,
            self.is_list_handler,
            self.type,
            indent(next_repr, False),
        )

    def set_notify(self, notify):
        """ Set notify state on this listener.

        Parameters
        ----------
        notify : bool
            True if this listener should notify, else False.
        """
        self.notify = notify

    def set_next(self, next):
        """ Set the child listener for this one.

        Parameters
        ----------
        next : ListenerBase
            The next level (if any) of ListenerBase object to be called when
            any of our listened to traits is changed:
        """
        self.next = next

    def register(self, new):
        """ Registers new listeners.
        """
        # Make sure we actually have an object to set listeners on and that it
        # has not already been registered (cycle breaking):
        if (new is None) or (new is Undefined) or (new in self.active):
            return INVALID_DESTINATION

        # Create a dictionary of {name: trait_values} that match the object's
        # definition for the 'new' object:
        name = self.name
        last = name[-1:]
        if last == "*":
            # Handle the special case of an 'anytrait' change listener:
            if self.is_anytrait:
                try:
                    self.active[new] = [("", ANYTRAIT_LISTENER)]
                    return self._register_anytrait(new, "", False)
                except TypeError:
                    # This error can occur if 'new' is a list or other object
                    # for which a weakref cannot be created as the dictionary
                    # key for 'self.active':
                    return INVALID_DESTINATION

            # Handle trait matching based on a common name prefix and/or
            # matching trait metadata:
            metadata = self._metadata
            if metadata is None:
                self._metadata = metadata = {"type": not_event}
                if self.metadata_name != "":
                    if self.metadata_defined:
                        metadata[self.metadata_name] = is_not_none
                    else:
                        metadata[self.metadata_name] = is_none

            # Get all object traits with matching metadata:
            names = new.trait_names(**metadata)

            # If a name prefix was specified, filter out only the names that
            # start with the specified prefix:
            name = name[:-1]
            if name != "":
                n = len(name)
                names = [aname for aname in names if name == aname[:n]]

            # Create the dictionary of selected traits:
            bt = new.base_trait
            traits = dict([(name, bt(name)) for name in names])

            # Handle any new traits added dynamically to the object:
            new.on_trait_change(self._new_trait_added, "trait_added")
        else:
            # Determine if the trait is optional or not:
            optional = last == "?"
            if optional:
                name = name[:-1]

            # Else, no wildcard matching, just get the specified trait:
            trait = new.base_trait(name)

            # Try to get the object trait:
            if trait is None:
                # Raise an error if trait is not defined and not optional:

                # fixme: Properties which are lists don't implement the
                # '..._items' sub-trait, which can cause a failure here when
                # used with an editor that sets up listeners on the items...
                if not optional:
                    raise TraitError(
                        "'%s' object has no '%s' trait"
                        % (new.__class__.__name__, name)
                    )

                # Otherwise, just skip it:
                traits = {}
            else:
                # Create a result dictionary containing just the single trait:
                traits = {name: trait}

        # For each item, determine its type (simple, list, dict):
        self.active[new] = active = []
        for name, trait in traits.items():

            # Determine whether the trait type is simple, list, set or
            # dictionary:
            type = SIMPLE_LISTENER
            handler = trait.handler
            if handler is not None:
                type = type_map.get(
                    handler.default_value_type, SIMPLE_LISTENER
                )

            # Add the name and type to the list of traits being registered:
            active.append((name, type))

            # Set up the appropriate trait listeners on the object for the
            # current trait:
            value = getattr(self, type)(new, name, False)

        if len(traits) == 1:
            return value

        return INVALID_DESTINATION

    def unregister(self, old):
        """ Unregisters any existing listeners.
        """
        if old is not None and old is not Uninitialized:
            try:
                active = self.active.pop(old, None)
                if active is not None:
                    for name, type in active:
                        getattr(self, type)(old, name, True)
            except TypeError:
                # An error can occur if 'old' is a list or other object for
                # which a weakref cannot be created and used an a key for
                # 'self.active':
                pass

    def handle_simple(self, object, name, old, new):
        """ Handles a trait change for an intermediate link trait.
        """
        self.next.unregister(old)
        self.next.register(new)

    def handle_dst(self, object, name, old, new):
        """ Handles a trait change for an intermediate link trait when the
            notification is for the final destination trait.
        """
        self.next.unregister(old)
        object, name = self.next.register(new)
        if old is not Uninitialized:
            if object is None:
                raise TraitError(
                    "on_trait_change handler signature is "
                    "incompatible with a change to an intermediate trait"
                )

            wh = self.wrapped_handler_ref()
            if wh is not None:
                wh(object, name, old, getattr(object, name, Undefined))

    def handle_list(self, object, name, old, new):
        """ Handles a trait change for a list (or set) trait.
        """
        if old is not None and old is not Uninitialized:
            unregister = self.next.unregister
            for obj in old:
                unregister(obj)

        register = self.next.register
        for obj in new:
            register(obj)

    def handle_list_items(self, object, name, old, new):
        """ Handles a trait change for items of a list (or set) trait.
        """
        self.handle_list(object, name, new.removed, new.added)

    def handle_list_items_special(self, object, name, old, new):
        """ Handles a trait change for items of a list (or set) trait with
            notification.
        """
        wh = self.wrapped_handler_ref()
        if wh is not None:
            wh(object, name, new.removed, new.added)

    def handle_dict(self, object, name, old, new):
        """ Handles a trait change for a dictionary trait.
        """
        if old is not Uninitialized:
            unregister = self.next.unregister
            for obj in old.values():
                unregister(obj)

        register = self.next.register
        for obj in new.values():
            register(obj)

    def handle_dict_items(self, object, name, old, new):
        """ Handles a trait change for items of a dictionary trait.
        """
        self.handle_dict(object, name, new.removed, new.added)

        if len(new.changed) > 0:
            # If 'name' refers to the '_items' trait, then remove the '_items'
            # suffix to get the actual dictionary trait.
            #
            # fixme: Is there ever a case where 'name' *won't* refer to the
            # '_items' trait?
            if name.endswith("_items"):
                name = name[: -len("_items")]

            dict = getattr(object, name)
            unregister = self.next.unregister
            register = self.next.register
            for key, obj in new.changed.items():
                unregister(obj)
                register(dict[key])

    def handle_error(self, obj, name, old, new):
        """ Handles an invalid intermediate trait change to a handler that must
            be applied to the final destination object.trait.
        """
        if old is not None and old is not Uninitialized:
            raise TraitError(
                "on_trait_change handler signature is "
                "incompatible with a change to an intermediate trait"
            )

    # -- Private Methods ------------------------------------------------------

    def _register_anytrait(self, object, name, remove):
        """ Registers any 'anytrait' listener.
        """
        handler = self.handler()
        if handler is not Undefined:
            object._on_trait_change(
                handler,
                remove=remove,
                dispatch=self.dispatch,
                priority=self.priority,
                target=self._get_target(),
            )

        return (object, name)

    def _register_simple(self, object, name, remove):
        """ Registers a handler for a simple trait.
        """
        next = self.next
        if next is None:
            handler = self.handler()
            if handler is not Undefined:
                object._on_trait_change(
                    handler,
                    name,
                    remove=remove,
                    dispatch=self.dispatch,
                    priority=self.priority,
                    target=self._get_target(),
                )

            return (object, name)

        tl_handler = self.handle_simple
        if self.notify:
            if self.type == DST_LISTENER:
                if self.dispatch != "same":
                    raise TraitError(
                        "Trait notification dispatch type '%s' "
                        "is not compatible with handler signature and "
                        "extended trait name notification style"
                        % self.dispatch
                    )
                tl_handler = self.handle_dst
            else:
                handler = self.handler()
                if handler is not Undefined:
                    object._on_trait_change(
                        handler,
                        name,
                        remove=remove,
                        dispatch=self.dispatch,
                        priority=self.priority,
                        target=self._get_target(),
                    )

        object._on_trait_change(
            tl_handler,
            name,
            remove=remove,
            dispatch="extended",
            priority=self.priority,
            target=self._get_target(),
        )

        if remove:
            return next.unregister(getattr(object, name))

        if not self.deferred or name in object.__dict__:
            # Sometimes, the trait may already be assigned. This can happen
            # when there are chains of dynamic initializers and 'delegate'
            # notifications. If 'trait_a' and 'trait_b' have dynamic
            # initializers and 'trait_a's initializer creates 'trait_b', *and*
            # we have a DelegatesTo trait that delegates to 'trait_a', then the
            # listener that implements the delegate will create 'trait_a' and
            # thus 'trait_b'. If we are creating an extended trait change
            # listener on 'trait_b.something', and the 'trait_a' delegate
            # listeners just happen to get hooked up before this one, then
            # 'trait_b' will have been initialized already, and the
            # registration that we are deferring will never happen.
            return next.register(getattr(object, name))

        return (object, name)

    def _register_list(self, object, name, remove):
        """ Registers a handler for a list trait.
        """
        next = self.next
        if next is None:
            handler = self.handler()
            if handler is not Undefined:
                object._on_trait_change(
                    handler,
                    name,
                    remove=remove,
                    dispatch=self.dispatch,
                    priority=self.priority,
                    target=self._get_target(),
                )

                if self.is_list_handler:
                    object._on_trait_change(
                        self.handle_list_items_special,
                        name + "_items",
                        remove=remove,
                        dispatch=self.dispatch,
                        priority=self.priority,
                        target=self._get_target(),
                    )

                elif self.type == ANY_LISTENER:
                    object._on_trait_change(
                        handler,
                        name + "_items",
                        remove=remove,
                        dispatch=self.dispatch,
                        priority=self.priority,
                        target=self._get_target(),
                    )

            return (object, name)

        tl_handler = self.handle_list
        tl_handler_items = self.handle_list_items
        if self.notify:
            if self.type == DST_LISTENER:
                tl_handler = tl_handler_items = self.handle_error
            else:
                handler = self.handler()
                if handler is not Undefined:
                    object._on_trait_change(
                        handler,
                        name,
                        remove=remove,
                        dispatch=self.dispatch,
                        priority=self.priority,
                        target=self._get_target(),
                    )

                    if self.is_list_handler:
                        object._on_trait_change(
                            self.handle_list_items_special,
                            name + "_items",
                            remove=remove,
                            dispatch=self.dispatch,
                            priority=self.priority,
                            target=self._get_target(),
                        )
                    elif self.type == ANY_LISTENER:
                        object._on_trait_change(
                            handler,
                            name + "_items",
                            remove=remove,
                            dispatch=self.dispatch,
                            priority=self.priority,
                            target=self._get_target(),
                        )

        object._on_trait_change(
            tl_handler,
            name,
            remove=remove,
            dispatch="extended",
            priority=self.priority,
            target=self._get_target(),
        )

        object._on_trait_change(
            tl_handler_items,
            name + "_items",
            remove=remove,
            dispatch="extended",
            priority=self.priority,
            target=self._get_target(),
        )

        if remove:
            handler = next.unregister
        elif self.deferred:
            return INVALID_DESTINATION
        else:
            handler = next.register

        for obj in getattr(object, name):
            handler(obj)

        return INVALID_DESTINATION

    # Handle 'sets' the same as 'lists':
    # Note: Currently the behavior of sets is almost identical to that of
    # lists, so we are able to share the same code for both. This includes some
    # 'duck typing' that occurs with the TraitListEvent and TraitSetEvent, that
    # define 'removed' and 'added' attributes that behave similarly enough
    # (from the point of view of this module) that they can be treated as
    # equivalent. If the behavior of sets ever diverges from that of lists,
    # then this code may need to be changed.
    _register_set = _register_list

    def _register_dict(self, object, name, remove):
        """ Registers a handler for a dictionary trait.
        """
        next = self.next
        if next is None:
            handler = self.handler()
            if handler is not Undefined:
                object._on_trait_change(
                    handler,
                    name,
                    remove=remove,
                    dispatch=self.dispatch,
                    priority=self.priority,
                    target=self._get_target(),
                )

                if self.type == ANY_LISTENER:
                    object._on_trait_change(
                        handler,
                        name + "_items",
                        remove=remove,
                        dispatch=self.dispatch,
                        priority=self.priority,
                        target=self._get_target(),
                    )

            return (object, name)

        tl_handler = self.handle_dict
        tl_handler_items = self.handle_dict_items
        if self.notify:
            if self.type == DST_LISTENER:
                tl_handler = tl_handler_items = self.handle_error
            else:
                handler = self.handler()
                if handler is not Undefined:
                    object._on_trait_change(
                        handler,
                        name,
                        remove=remove,
                        dispatch=self.dispatch,
                        priority=self.priority,
                        target=self._get_target(),
                    )

                    if self.type == ANY_LISTENER:
                        object._on_trait_change(
                            handler,
                            name + "_items",
                            remove=remove,
                            dispatch=self.dispatch,
                            priority=self.priority,
                            target=self._get_target(),
                        )

        object._on_trait_change(
            tl_handler,
            name,
            remove=remove,
            dispatch=self.dispatch,
            priority=self.priority,
            target=self._get_target(),
        )

        object._on_trait_change(
            tl_handler_items,
            name + "_items",
            remove=remove,
            dispatch=self.dispatch,
            priority=self.priority,
            target=self._get_target(),
        )

        if remove:
            handler = next.unregister
        elif self.deferred:
            return INVALID_DESTINATION
        else:
            handler = next.register

        for obj in getattr(object, name).values():
            handler(obj)

        return INVALID_DESTINATION

    def _new_trait_added(self, object, name, new_trait):
        """ Handles new traits being added to an object being monitored.
        """
        # Set if the new trait matches our prefix and metadata:
        if new_trait.startswith(self.name[:-1]):
            trait = object.base_trait(new_trait)
            for meta_name, meta_eval in self._metadata.items():
                if not meta_eval(getattr(trait, meta_name)):
                    return

            # Determine whether the trait type is simple, list, set or
            # dictionary:
            type = SIMPLE_LISTENER
            handler = trait.handler
            if handler is not None:
                type = type_map.get(handler.default_value_, SIMPLE_LISTENER)

            # Add the name and type to the list of traits being registered:
            self.active[object].append((new_trait, type))

            # Set up the appropriate trait listeners on the object for the
            # new trait:
            getattr(self, type)(object, new_trait, False)

    def _get_target(self):
        """ Get the target object from the ListenerNotifyWrapper.
        """
        target = None
        lnw = self.wrapped_handler_ref()
        if lnw is not None:
            target_ref = getattr(lnw, "object", None)
            if target_ref is not None:
                target = target_ref()
        return target


class ListenerGroup(ListenerBase):
    """
    Listener description for a collection of items.

    The ListenerParser produces a ListenerGroup rather than a ListenerItem
    when parsing strings like ``[abc,def]``.

    Parameters
    ----------
    items : list
        List of ListenerItem objects representing the components of the group.
    """

    # -- 'ListenerBase' Class Method Implementations --------------------------

    def __init__(self, *, items):
        self.items = items
        self.next = None

    def __repr__(self, seen=None):
        """Returns a string representation of the object.

        Since the object graph may have cycles, we extend the basic __repr__
        API to include a set of objects we've already seen while constructing
        a string representation. When this method tries to get the repr of
        a ListenerItem or ListenerGroup, we will use the extended API and build
        up the set of seen objects. The repr of a seen object will just be
        '<cycle>'.
        """
        if seen is None:
            seen = set()

        seen.add(self)

        lines = ["%s(items = [" % self.__class__.__name__]

        for item in self.items:
            lines.extend(indent(item.__repr__(seen), True).split("\n"))
            lines[-1] += ","

        lines.append("])")

        return "\n".join(lines)

    def set_notify(self, notify):
        """ Set notify state on this listener.

        Parameters
        ----------
        notify : bool
            True if this listener should notify, else False.
        """
        for item in self.items:
            item.set_notify(notify)

    def set_next(self, next):
        """ Set the child listener for this one.

        Parameters
        ----------
        next : ListenerBase
            The next level (if any) of ListenerBase object to be called when
            any of our listened to traits is changed:
        """
        for item in self.items:
            item.set_next(next)
        self.next = next if self.items else None

    def register(self, new):
        """ Registers new listeners.
        """
        for item in self.items:
            item.register(new)

        return INVALID_DESTINATION

    def unregister(self, old):
        """ Unregisters any existing listeners.
        """
        for item in self.items:
            item.unregister(old)


class ListenerParser:

    # -- Property Implementations ---------------------------------------------

    @property
    def next(self):
        """The next character from the string being parsed."""
        index = self.index
        self.index += 1
        if index >= self.len_text:
            return EOS

        return self.text[index]

    @property
    def backspace(self):
        """Backspaces to the last character processed."""
        self.index = max(0, self.index - 1)

    @property
    def skip_ws(self):
        """The next non-whitespace character."""
        while True:
            c = self.next
            if c not in whitespace:
                return c

    @property
    def name(self):
        """The next Python attribute name within the string."""
        match = name_pat.match(self.text, self.index - 1)
        if match is None:
            return ""

        self.index = match.start(2)

        return match.group(1)

    # -- object Method Overrides ----------------------------------------------

    def __init__(
        self,
        text,
        *,
        handler=None,
        wrapped_handler_ref=None,
        dispatch="",
        priority=False,
        deferred=False,
        handler_type=ANY_LISTENER,
    ):
        #: The text being parsed.
        self.text = text

        #: The length of the string being parsed.
        self.len_text = len(self.text)

        #: The current parse index within the string.
        self.index = 0

        #: The handler to be called when any listened-to trait is changed.
        self.handler = handler

        #: A weakref 'wrapped' version of 'handler'.
        self.wrapped_handler_ref = wrapped_handler_ref

        #: The dispatch mechanism to use when invoking the handler.
        self.dispatch = dispatch

        #: Does the handler go at the beginning (True) or end (False) of the
        #: notification handlers list?
        self.priority = priority

        #: The parsed listener.
        self.listener = self.parse(deferred, handler_type)

    # -- Private Methods ------------------------------------------------------

    def parse(self, deferred, handler_type):
        """ Parses the text and returns the appropriate collection of
            ListenerBase objects described by the text.

        Parameters
        ----------
        deferred : bool
            Should registering listeners for items reachable from this listener
            item be deferred until the associated trait is first read or set?
        handler_type : int
            The type of handler being used; one of {ANY_LISTENER, SRC_LISTENER,
            DST_LISTENER}.
        """
        # Try a simple case of 'name1.name2'. The simplest case of a single
        # Python name never triggers this parser, so we don't try to make that
        # a shortcut too. Whitespace should already have been stripped from the
        # start and end.

        if self.text.strip().endswith(","):
            self.error("Error parsing name. Trailing ',' is not allowed")

        # TODO: The use of regexes should be used throughout all of the parsing
        # functions to speed up all aspects of parsing.
        match = simple_pat.match(self.text)
        if match is not None:
            return ListenerItem(
                name=match.group(1),
                notify=match.group(2) == ".",
                next=ListenerItem(
                    name=match.group(3),
                    handler=self.handler,
                    wrapped_handler_ref=self.wrapped_handler_ref,
                    dispatch=self.dispatch,
                    priority=self.priority,
                    # Bug-for-bug compatibility with old behaviour: don't
                    # propagate the 'deferred' or 'handler_type' values for the
                    # child item. Ref: enthought/traits#537.
                    deferred=False,
                    type=ANY_LISTENER,
                ),
                handler=self.handler,
                wrapped_handler_ref=self.wrapped_handler_ref,
                dispatch=self.dispatch,
                priority=self.priority,
                deferred=deferred,
                type=handler_type,
            )

        return self.parse_group(
            terminator=EOS,
            deferred=deferred,
            handler_type=handler_type,
        )

    def parse_group(self, *, terminator, deferred, handler_type):
        """ Parses the contents of a group.

        Parameters
        ----------
        terminator : str or EOS
            Character on which to halt parsing of this item.
        deferred : bool
            Should registering listeners for items reachable from this listener
            item be deferred until the associated trait is first read or set?
        handler_type : int
            The type of handler being used; one of {ANY_LISTENER, SRC_LISTENER,
            DST_LISTENER}.
        """
        items = []
        while True:
            items.append(
                self.parse_item(
                    terminator=terminator,
                    deferred=deferred,
                    handler_type=handler_type,
                )
            )

            c = self.skip_ws
            if c == terminator:
                break

            if c != ",":
                if terminator == EOS:
                    self.error("Expected ',' or end of string")
                else:
                    self.error("Expected ',' or '%s'" % terminator)

        if len(items) == 1:
            return items[0]

        return ListenerGroup(items=items)

    def parse_item(self, *, terminator, deferred, handler_type):
        """ Parses a single, complete listener item or group string.

        Parameters
        ----------
        terminator : str or EOS
            Character on which to halt parsing of this item.
        deferred : bool
            Should registering listeners for items reachable from this listener
            item be deferred until the associated trait is first read or set?
        handler_type : int
            The type of handler being used; one of {ANY_LISTENER, SRC_LISTENER,
            DST_LISTENER}.
        """
        c = self.skip_ws
        if c == "[":
            result = self.parse_group(
                terminator="]",
                deferred=deferred,
                handler_type=handler_type,
            )
            c = self.skip_ws
        else:
            name = self.name
            if name != "":
                c = self.next

            result = ListenerItem(
                name=name,
                handler=self.handler,
                wrapped_handler_ref=self.wrapped_handler_ref,
                dispatch=self.dispatch,
                priority=self.priority,
                deferred=deferred,
                type=handler_type,
            )

            if c in "+-":
                result.name += "*"
                result.metadata_defined = c == "+"
                cn = self.skip_ws
                result.metadata_name = metadata = self.name
                if metadata != "":
                    cn = self.skip_ws

                result.is_anytrait = (
                    (c == "-") and (name == "") and (metadata == "")
                )
                c = cn

                if result.is_anytrait and (
                    not (
                        (c == terminator)
                        or ((c == ",") and (terminator == "]"))
                    )
                ):
                    self.error("Expected end of name")
            elif c == "?":
                if len(name) == 0:
                    self.error("Expected non-empty name preceding '?'")
                result.name += "?"
                c = self.skip_ws

        cycle = c == "*"
        if cycle:
            c = self.skip_ws

        if c in ".:":
            result.set_notify(c == ".")
            # Bug-for-bug compatibility with old behaviour: don't propagate the
            # 'deferred' or 'handler_type' values for the child item.
            # Ref: enthought/traits#537.
            next = self.parse_item(
                terminator=terminator,
                deferred=False,
                handler_type=ANY_LISTENER,
            )
            if cycle:
                last = result
                while last.next is not None:
                    last = last.next
                lg = ListenerGroup(items=[next, result])
                last.set_next(lg)
                result = lg
            else:
                result.set_next(next)

            return result

        if c == "[":
            is_closing_bracket = self.skip_ws == "]"
            next_char = self.skip_ws
            item_complete = next_char == terminator or next_char == ","
            if is_closing_bracket and item_complete:
                self.backspace
                result.is_list_handler = True
            else:
                self.error("Expected '[]' at the end of an item")
        else:
            self.backspace

        if cycle:
            result.set_next(result)

        return result

    def parse_metadata(self, item):
        """ Parses the metadata portion of a listener item.
        """
        self.skip_ws
        item.metadata_name = name = self.name
        if name == "":
            self.backspace

    def error(self, msg):
        """ Raises a syntax error.
        """
        raise TraitError(
            "%s at column %d of '%s'" % (msg, self.index, self.text)
        )


class ListenerNotifyWrapper(TraitChangeNotifyWrapper):

    # -- TraitChangeNotifyWrapper Method Overrides ----------------------------

    def __init__(self, handler, owner, id, listener, target=None):
        self.type = ListenerType.get(
            self.init(handler, weakref.ref(owner, self.owner_deleted), target)
        )
        self.id = id
        self.listener = listener

    def listener_deleted(self, ref):
        owner = self.owner()
        if owner is not None:
            dict = owner.__dict__.get(TraitsListener)
            listeners = dict.get(self.id)
            listeners.remove(self)
            if len(listeners) == 0:
                del dict[self.id]
                if len(dict) == 0:
                    del owner.__dict__[TraitsListener]
                # fixme: Is the following line necessary, since all registered
                # notifiers should be getting the same 'listener_deleted' call:
                self.listener.unregister(owner)

        self.object = self.owner = self.listener = None

    def owner_deleted(self, ref):
        self.object = self.owner = None


class ListenerHandler(object):
    """
    Wrapper for trait change handlers that avoids strong references to methods.

    For a bound method handler, this wrapper prevents us from holding a
    strong reference to the object bound to that bound method. For other
    callable handlers, we do keep a strong reference to the handler.

    When called with no arguments, this object returns either the actual
    handler, or Undefined if the handler no longer exists because the object
    it was bound to has been garbage collected.

    Parameters
    ----------
    handler : callable
        Object to be called when the relevant trait or traits change.
    """

    def __init__(self, handler):
        if isinstance(handler, MethodType):
            self.handler_ref = weakref.WeakMethod(handler)
        else:
            self.handler = handler

    def __call__(self):
        result = getattr(self, "handler", None)
        if result is not None:
            return result
        else:
            handler = self.handler_ref()
            return Undefined if handler is None else handler
