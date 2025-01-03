# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the HasTraits class, along with several useful subclasses and
    associated metaclasses.
"""

import abc
import copy as copy_module
import inspect
import os
import pickle
import re
import types
import warnings
import weakref

from types import FunctionType

from . import __version__ as TraitsVersion
from .constants import DefaultValue, TraitKind
from .ctrait import CTrait, __newobj__
from .ctraits import CHasTraits
from .observation import api as observe_api
from .traits import (
    ForwardProperty,
    Property,
    Trait,
    generic_trait,
)
from .trait_types import Any, Bool, Disallow, Event, Python, Str
from .trait_notifiers import (
    ExtendedTraitChangeNotifyWrapper,
    FastUITraitChangeNotifyWrapper,
    NewTraitChangeNotifyWrapper,
    StaticAnytraitChangeNotifyWrapper,
    StaticTraitChangeNotifyWrapper,
    TraitChangeNotifyWrapper,
    ui_dispatch,
)
from .trait_base import (
    SequenceTypes,
    TraitsCache,
    Undefined,
    is_none,
    not_event,
    not_false,
)
from .trait_errors import TraitError
from .trait_converters import check_trait, mapped_trait_for, trait_for


#  Set CHECK_INTERFACES to one of the following values:
#
#  - 0: Does not check to see if classes implement their declared interfaces.
#  - 1: Ensures that classes implement the interfaces they say they do, and
#       logs a warning if they don't.
#  - 2: Ensures that classes implement the interfaces they say they do, and
#       raises an InterfaceError if they don't.
#
#  This constant is used by the @provides decorator when deciding whether to
#  do interface checking. This behaviour is deprecated. In the future, the
#  provides decorator will no longer perform interface checking, regardless of
#  the value of this constant.

CHECK_INTERFACES = 0


#  This ABC is a placeholder for the TraitsUI ViewElement class, which should
#  inherit from or register as implementing the API.  This has to be done here
#  so that the metaclass machinery has something to check against when
#  filtering out TraitsUI elements that are declared as part of a HasTraits
#  class.

class AbstractViewElement(abc.ABC):
    pass


# Constants

WrapperTypes = (
    StaticAnytraitChangeNotifyWrapper,
    StaticTraitChangeNotifyWrapper,
)

# Class dictionary entries used to save trait, listener and view information
# and definitions:

BaseTraits = "__base_traits__"
ClassTraits = "__class_traits__"
PrefixTraits = "__prefix_traits__"
ListenerTraits = "__listener_traits__"
ObserverTraits = "__observer_traits__"
ViewTraits = "__view_traits__"
InstanceTraits = "__instance_traits__"

# The default Traits View name
DefaultTraitsView = "traits_view"

# Trait types which cannot have default values
CantHaveDefaultValue = ("event", "delegate", "constant")

# The trait types that should be copied last when doing a 'copy_traits':
DeferredCopy = ("delegate", "property")

# Quick test for normal vs extended trait name
extended_trait_pat = re.compile(r".*[ :\+\-,\.\*\?\[\]]")

# Generic 'Any' trait:
any_trait = Any().as_ctrait()

# Mapping from user-facing strings to the dispatcher callable in observe.
_ObserverDispatchers = {
    "same": observe_api.dispatch_same,
    "ui": ui_dispatch,
}


def _clone_trait(clone, metadata=None):
    """ Creates a clone of a specified trait.
    """
    trait = CTrait(TraitKind.trait)
    trait.clone(clone)

    if clone.__dict__ is not None:
        trait.__dict__ = clone.__dict__.copy()

    if metadata is not None:
        trait.__dict__.update(metadata)

    return trait


def _get_method(cls, method):
    """ Get the definition of a specified method (if any). """
    result = getattr(cls, method, None)
    if (result is not None) and is_unbound_method_type(result):
        return result
    return None


def _get_def(class_name, class_dict, bases, method):
    """ Gets the definition of a specified method (if any).
    """
    if method[0:2] == "__":
        # When name-mangling to handle the __ case (for _private traits),
        # leading underscores in the class name are stripped out.
        method = "_%s%s" % (class_name.lstrip('_'), method)

    result = class_dict.get(method)
    if (
        (result is not None)
        and is_unbound_method_type(result)
        and (getattr(result, "on_trait_change", None) is None)
        and (getattr(result, "_observe_inputs", None) is None)
    ):
        return result

    for base in bases:
        result = getattr(base, method, None)
        if (
            (result is not None)
            and is_unbound_method_type(result)
            and (getattr(result, "on_trait_change", None) is None)
            and (getattr(result, "_observe_inputs", None) is None)
        ):
            return result

    return None


def is_unbound_method_type(method):
    """ Check for something that looks like an unbound class method.

    This is used in practice to identify magic-named _name_changed
    and _name_fired methods.

    """
    # The ismethoddescriptor check catches methods written in C
    # extensions. It excludes things that pass an isfunction check, so we have
    # to explicitly re-include that check.
    return inspect.isfunction(method) or inspect.ismethoddescriptor(method)


def _is_serializable(value):
    """ Returns whether or not a specified value is serializable.
    """
    if isinstance(value, (list, tuple)):
        for item in value:
            if not _is_serializable(item):
                return False

        return True

    if isinstance(value, dict):
        for name, item in value.items():
            if (not _is_serializable(name)) or (not _is_serializable(item)):
                return False

        return True

    return (not isinstance(value, HasTraits)) or value.has_traits_interface(
        ISerializable
    )


def _get_instance_handlers(class_dict, bases):
    """ Returns a dictionary of potential 'Instance' or 'List(Instance)'
        handlers.
    """
    # Create the results dictionary:
    instance_traits = {}

    # Merge all of the base class information into the result:
    for base in bases:
        for name, base_arg_lists in base.__dict__.get(InstanceTraits).items():
            arg_lists = instance_traits.get(name)
            if arg_lists is None:
                instance_traits[name] = base_arg_lists[:]
            else:
                for arg_list in base_arg_lists:
                    if arg_list not in arg_lists:
                        arg_lists.append(arg_list)

    # Merge in the information from the class dictionary:
    for name, value in class_dict.items():
        if (name[:1] == "_") and is_unbound_method_type(value):
            n = 13
            col = name.find("_changed_for_")
            if col < 2:
                n = 11
                col = name.find("_fired_for_")
            if col >= 2:
                key = name[col + n:]
                if key != "":
                    arg_list = (name, name[1:col])
                    arg_lists = instance_traits.setdefault(key, [])
                    if arg_list not in arg_lists:
                        arg_lists.append(arg_list)

    # Return the dictionary of possible arg_lists:
    return instance_traits


def get_delegate_pattern(name, trait):
    """ Returns the correct 'delegate' listener pattern for a specified name
    and delegate trait.
    """
    prefix = trait._prefix
    if prefix == "":
        prefix = name
    elif (len(prefix) > 1) and (prefix[-1] == "*"):
        prefix = prefix[:-1] + name

    return " %s:%s" % (trait._delegate, prefix)


class _SimpleTest:
    def __init__(self, value):
        self.value = value

    def __call__(self, test):
        return test == self.value


def _add_notifiers(notifiers, handlers):
    """ Adds a list of handlers to a specified notifiers list.
    """
    for handler in handlers:
        if not isinstance(handler, WrapperTypes):
            handler = StaticTraitChangeNotifyWrapper(handler)
        notifiers.append(handler)


def _add_event_handlers(trait, cls, handlers):
    """ Adds any specified event handlers defined for a trait by a class.
    """
    events = trait.event
    if events is not None:
        if isinstance(events, str):
            events = [events]

        for event in events:
            handlers.append(_get_method(cls, "_%s_changed" % event))
            handlers.append(_get_method(cls, "_%s_fired" % event))


def _property_method(class_dict, name):
    """ Returns the method associated with a particular class property
    getter/setter.
    """
    return class_dict.get(name)


def _create_property_observe_state(observe, property_name, cached):
    """ Create the metadata for setting up an observer for Property.

    Parameters
    ----------
    observe : str or list or Expression
        As is accepted by HasTraits.observe expression argument
        This is the value provided in Property(observe=...)
    property_name : str
        The name of the property trait.
    cached : boolean
        Whether the property is cached or not.

    Returns
    -------
    state : dict
        State to be used by _init_traits_observers
    """

    def handler(instance, event):
        if cached:
            cache_name = TraitsCache + property_name
            old = instance.__dict__.pop(cache_name, Undefined)
        else:
            old = Undefined
        instance.trait_property_changed(property_name, old)

    def handler_getter(instance, name):
        return types.MethodType(handler, instance)

    graphs = _compile_expression(observe)

    return dict(
        graphs=graphs,
        dispatch="same",
        handler_getter=handler_getter,
        post_init=False,
    )


def _compile_expression(expression):
    """ Compile a user-supplied expression or list of expressions.

    Converts a list of strings or ObserverExpressions to a list of
    ObserverGraphs representing the observation patterns to be applied.

    Parameters
    ----------
    expression : str or list or ObserverExpression
        A description of what traits are being observed.
        If this is a list, each item must be a string or an ObserverExpression.

    Returns
    -------
    graphs : list of ObserverGraph
        List of graphs representing the observation patterns to be applied
        to the relevant objects and handlers.
    """
    # Handle the overloaded signature.
    # Support list to be consistent with on_trait_change.
    if isinstance(expression, list):
        expressions = expression
    else:
        expressions = [expression]

    graphs = []
    for expr in expressions:
        graphs.extend(
            observe_api.compile_str(expr) if isinstance(expr, str)
            else observe_api.compile_expr(expr)
        )
    return graphs


# This really should be 'HasTraits', but it's not defined yet:
_HasTraits = None


class MetaHasTraits(type):
    """ Controls the creation of HasTraits classes.

    The heavy work is done by the `update_traits_class_dict` function, which
    takes the ``class_dict`` dictionary of class members and extracts and
    processes the trait declarations in it. The trait declarations are then
    added back to the class dictionary and passed off to the __new__ method
    of the type superclass, to be added to the class.

    """

    def __new__(cls, class_name, bases, class_dict):
        # Convert entries in the class dictionary into traits, as appropriate.
        update_traits_class_dict(class_name, bases, class_dict)

        # Finish building the class using the updated class dictionary.
        return type.__new__(cls, class_name, bases, class_dict)


def update_traits_class_dict(class_name, bases, class_dict):
    """ Processes all of the traits related data in the class dictionary.

    This is called during the construction of a new HasTraits class. The first
    three parameters have the same interpretation as the corresponding
    parameters of ``type.__new__``. This function modifies ``class_dict``
    in-place.

    Parameters
    ----------
    class_name : str
        The name of the HasTraits class.
    bases : tuple
        The base classes for the HasTraits class.
    class_dict : dict
        A dictionary of class members.
    """

    # Create the various class dictionaries, lists and objects needed to
    # hold trait and view information and definitions:
    base_traits = {}
    class_traits = {}
    prefix_traits = {}
    listeners = {}
    prefix_list = []
    view_elements = {}

    # Mapping from method/trait names to list(dict)
    # where each nested dict provides the input arguments for calling
    # ``HasTraits.observe`` once. See ``_init_trait_observers``.`
    observers = {}

    # Create a list of just those base classes that derive from HasTraits:
    hastraits_bases = [
        base for base in bases if base.__dict__.get(ClassTraits) is not None
    ]

    # Create a list of all inherited trait dictionaries:
    inherited_class_traits = [
        base.__dict__.get(ClassTraits) for base in hastraits_bases
    ]

    # Move all trait definitions from the class dictionary to the
    # appropriate trait class dictionaries:
    for name, value in list(class_dict.items()):

        value = check_trait(value)
        rc = isinstance(value, CTrait)

        if (not rc) and isinstance(value, ForwardProperty):
            rc = True
            # Create Property trait from getter, setter, validator
            getter = _property_method(class_dict, "_get_" + name)
            setter = _property_method(class_dict, "_set_" + name)
            if (setter is None) and (getter is not None):
                if getattr(getter, "settable", False):
                    setter = HasTraits._set_traits_cache
                elif getattr(getter, "flushable", False):
                    setter = HasTraits._flush_traits_cache
            validate = _property_method(class_dict, "_validate_" + name)
            if validate is None:
                validate = value.validate

            value = Property(
                getter, setter, validate, True, value.handler, **value.metadata
            )
        if rc:
            del class_dict[name]
            if name[-1:] != "_":
                base_traits[name] = class_traits[name] = value
                value_type = value.type
                if value_type == "trait":
                    handler = value.handler
                    if handler is not None:
                        if handler.has_items:
                            items_trait = _clone_trait(
                                handler.items_event(), value.__dict__
                            )

                            if (
                                items_trait.instance_handler
                                == "_list_changed_handler"
                            ):
                                items_trait.instance_handler = (
                                    "_list_items_changed_handler"
                                )

                            class_traits[name + "_items"] = items_trait

                        if handler.is_mapped:
                            class_traits[name + "_"] = mapped_trait_for(
                                value, name
                            )

                elif value_type == "delegate":
                    # Only add a listener if the trait.listenable metadata
                    # is not False:
                    if value._listenable is not False:
                        listeners[name] = (
                            "delegate",
                            get_delegate_pattern(name, value),
                        )
                elif value_type == "event":
                    on_trait_change = value.on_trait_change
                    if isinstance(on_trait_change, str):
                        listeners[name] = ("event", on_trait_change)
            else:
                name = name[:-1]
                prefix_list.append(name)
                prefix_traits[name] = value

        elif is_unbound_method_type(value):
            pattern = getattr(value, "on_trait_change", None)
            if pattern is not None:
                listeners[name] = ("method", pattern)

            observer_states = getattr(value, "_observe_inputs", None)
            if observer_states is not None:
                observers[name] = observer_states

        elif isinstance(value, property):
            class_traits[name] = generic_trait

        # Handle any view elements found in the class:
        elif isinstance(value, AbstractViewElement):

            view_elements[name] = value

            # Remove the view element from the class definition:
            del class_dict[name]

        else:
            for ct in inherited_class_traits:
                if name in ct:
                    # The subclass is providing a default value for the
                    # trait defined in a superclass.
                    ictrait = ct[name]
                    if ictrait.type in CantHaveDefaultValue:
                        raise TraitError(
                            "Cannot specify a default value "
                            "for the %s trait '%s'. You must override the "
                            "the trait definition instead."
                            % (ictrait.type, name)
                        )

                    class_traits[name] = ictrait(value)
                    del class_dict[name]
                    break

    # Process all HasTraits base classes:
    migrated_properties = {}
    for base in hastraits_bases:
        base_dict = base.__dict__

        # Merge listener information:
        for name, value in base_dict.get(ListenerTraits).items():
            if (name not in class_traits) and (name not in class_dict):
                listeners[name] = value

        # Merge observer information:
        for name, states in base_dict[ObserverTraits].items():
            if (name not in class_traits) and (name not in class_dict):
                observers[name] = states

        # Merge base traits:
        for name, value in base_dict.get(BaseTraits).items():
            if name not in base_traits:
                property_info = value.property_fields
                if property_info is not None:
                    key = id(value)
                    migrated_properties[key] = value = migrate_property(
                        name, value, property_info, class_dict
                    )
                base_traits[name] = value

        # Merge class traits:
        for name, value in base_dict.get(ClassTraits).items():
            if name not in class_traits:
                property_info = value.property_fields
                if property_info is not None:
                    new_value = migrated_properties.get(id(value))
                    if new_value is not None:
                        value = new_value
                    else:
                        value = migrate_property(
                            name, value, property_info, class_dict
                        )
                class_traits[name] = value

        # Merge prefix traits:
        base_prefix_traits = base_dict.get(PrefixTraits)
        for name in base_prefix_traits["*"]:
            if name not in prefix_list:
                prefix_list.append(name)
                prefix_traits[name] = base_prefix_traits[name]

    # Make sure there is a definition for 'undefined' traits:
    if prefix_traits.get("") is None:
        prefix_list.append("")
        prefix_traits[""] = Python().as_ctrait()

    # Save a link to the prefix_list:
    prefix_traits["*"] = prefix_list

    # Make sure the trait prefixes are sorted longest to shortest
    # so that we can easily bind dynamic traits to the longest matching
    # prefix:
    prefix_list.sort(key=len, reverse=True)

    # Get the list of all possible 'Instance'/'List(Instance)' handlers:
    instance_traits = _get_instance_handlers(class_dict, hastraits_bases)

    # If there is an 'anytrait_changed' event handler, wrap it so that
    # it can be attached to all traits in the class:
    anytrait = _get_def(class_name, class_dict, bases, "_anytrait_changed")
    if anytrait is not None:
        anytrait = StaticAnytraitChangeNotifyWrapper(anytrait)

        # Save it in the prefix traits dictionary so that any dynamically
        # created traits (e.g. 'prefix traits') can re-use it:
        prefix_traits["@"] = anytrait

    # Make one final pass over the class traits dictionary, making sure
    # all static trait notification handlers are attached to a 'cloned'
    # copy of the original trait:
    cloned = set()
    for name in list(class_traits.keys()):
        trait = class_traits[name]
        handlers = [
            anytrait,
            _get_def(class_name, class_dict, bases, "_%s_changed" % name),
            _get_def(class_name, class_dict, bases, "_%s_fired" % name),
        ]

        # Check for an 'Instance' or 'List(Instance)' trait with defined
        # handlers:
        instance_handler = trait.instance_handler
        if (
            (instance_handler is not None)
            and (name in instance_traits)
            or (
                (instance_handler == "_list_items_changed_handler")
                and (name[-6:] == "_items")
                and (name[:-6] in instance_traits)
            )
        ):
            handlers.append(getattr(HasTraits, instance_handler))

        events = trait.event
        if events is not None:

            if isinstance(events, str):
                events = [events]

            for event in events:
                handlers.append(
                    _get_def(
                        class_name, class_dict, bases, "_%s_changed" % event
                    )
                )
                handlers.append(
                    _get_def(
                        class_name, class_dict, bases, "_%s_fired" % event
                    )
                )

        handlers = [h for h in handlers if h is not None]
        default = _get_def(class_name, class_dict, [], "_%s_default" % name)
        if (len(handlers) > 0) or (default is not None):

            if name not in cloned:
                cloned.add(name)
                class_traits[name] = trait = _clone_trait(trait)

            if len(handlers) > 0:
                _add_notifiers(trait._notifiers(True), handlers)

            if default is not None:
                trait.set_default_value(DefaultValue.callable, default)

        # Handle the case of properties whose value depends upon the value
        # of other traits:
        if (trait.type == "property") and (trait.depends_on is not None):

            cached = trait.cached
            if cached is True:
                cached = TraitsCache + name

            depends_on = trait.depends_on
            if isinstance(depends_on, SequenceTypes):
                depends_on = ",".join(depends_on)
            else:
                # Note: We add the leading blank to force it to be treated
                # as using the extended trait notation so that it will
                # automatically add '_items' listeners to lists/dicts:
                depends_on = " " + depends_on

            listeners[name] = ("property", cached, depends_on)

        if trait.type == "property" and trait.observe is not None:
            observer_state = _create_property_observe_state(
                observe=trait.observe,
                property_name=name,
                cached=trait.cached,
            )
            observers[name] = [observer_state]

    # Add processed traits back into class_dict.
    class_dict[BaseTraits] = base_traits
    class_dict[ClassTraits] = class_traits
    class_dict[InstanceTraits] = instance_traits
    class_dict[PrefixTraits] = prefix_traits
    class_dict[ListenerTraits] = listeners
    class_dict[ObserverTraits] = observers
    class_dict[ViewTraits] = view_elements


def migrate_property(name, property, property_info, class_dict):
    """ Migrates an existing property to the class being defined
    (allowing for method overrides).
    """
    get = _property_method(class_dict, "_get_" + name)
    set = _property_method(class_dict, "_set_" + name)
    val = _property_method(class_dict, "_validate_" + name)
    if (get is not None) or (set is not None) or (val is not None):
        old_get, old_set, old_val = property_info
        return Property(
            get or old_get,
            set or old_set,
            val or old_val,
            True,
            **property.__dict__
        )

    return property


# 'HasTraits' decorators

def observe(expression, *, post_init=False, dispatch="same"):
    """ Marks the wrapped method as being a handler to be called when the
    specified traits change.

    This decorator can be stacked, e.g.::

        @observe("attr1")
        @observe("attr2", post_init=True)
        def updated(self, event):
            ...

    The decorated function must accept one argument which is the event object
    representing the change. See :mod:`traits.observation.events` for details.

    Parameters
    ----------
    expression : str or list or ObserverExpression
        A description of what traits are being observed.
        If this is a list, each item must be a string or Expression.
        See :py:func:`HasTraits.observe` for details on the
        semantics when passing a string.
    post_init : boolean, optional
        Whether the change handler should be attached after
        the state is set when instantiating an object. Default is false, and
        values provided to the instance constructor will trigger the
        change handler to fire if the value is different from the
        default. Set to true to avoid this change event.
    dispatch : str, optional
        A string indicating how the handler should be run. Default is to run
        it on the same thread where the change occurs.
        Possible values are:

        =========== =======================================================
        value       dispatch
        =========== =======================================================
        ``same``    Run notifications on the same thread where the change
                    occurs. The notifications are executed immediately.
        ``ui``      Run notifications on the UI thread. If the current
                    thread is the UI thread, the notifications are executed
                    immediately; otherwise, they are placed on the UI
                    event queue.
        =========== =======================================================

    See Also
    --------
    HasTraits.observe
    """

    graphs = _compile_expression(expression)

    def observe_decorator(handler):
        """ Create input arguments for HasTraits.observe and attach the input
        to the callable.

        The metaclass will then collect this information for calling
        HasTraits.observe with the decorated function.

        Parameters
        ----------
        handler : callable
            Method of a subclass of HasTraits, with signature of the form
            ``my_method(self, event)``.
        """
        # Warn on a dubious handler signature. The handler should accept a call
        # that passes a single positional argument (conventionally named
        # "event") in addition to the usual "self".
        handler_signature = inspect.signature(handler)
        try:
            handler_signature.bind("self", "event")
        except TypeError:
            warnings.warn(
                (
                    "Dubious signature for observe-decorated method. "
                    "The decorated method should be callable with a "
                    "single positional argument in addition to 'self'. "
                    "Did you forget to add an 'event' parameter?"
                ),
                UserWarning,
                stacklevel=2,
            )

        try:
            observe_inputs = handler._observe_inputs
        except AttributeError:
            observe_inputs = []
            handler._observe_inputs = observe_inputs

        observe_input = dict(
            graphs=graphs,
            dispatch=dispatch,
            post_init=post_init,
            handler_getter=getattr,
        )
        observe_inputs.append(observe_input)

        return handler
    return observe_decorator


def on_trait_change(name, post_init=False, dispatch="same"):
    """ Marks the following method definition as being a handler for the
        extended trait change specified by *name(s)*.

        Refer to the documentation for the on_trait_change() method of
        the **HasTraits** class for information on the correct syntax for
        the *name* argument and the semantics of the *dispatch* keyword
        argument.

        A handler defined using this decorator is normally effective
        immediately. However, if *post_init* is **True**, then the handler only
        becomes effective after all object constructor arguments have been
        processed. That is, trait values assigned as part of object
        construction will not cause the handler to be invoked.

        See Also
        --------
        observe : A newer API for defining traits notifications.
    """

    def decorator(function):

        function.on_trait_change = {
            "pattern": name,
            "post_init": post_init,
            "dispatch": dispatch,
        }

        return function

    return decorator


def cached_property(function):
    """ Marks the following method definition as being a "cached property".
        That is, it is a property getter which, for performance reasons, caches
        its most recently computed result in an attribute whose name is of the
        form: *_traits_cache_name*, where *name* is the name of the property. A
        method marked as being a cached property needs only to compute and
        return its result. The @cached_property decorator automatically wraps
        the decorated method in cache management code, eliminating the need to
        write boilerplate cache management code explicitly. For example::

            file_name = File
            file_contents = Property(observe='file_name')

            @cached_property
            def _get_file_contents(self):
                with open(self.file_name, 'rb') as fh:
                    return fh.read()

        In this example, accessing the *file_contents* trait calls the
        _get_file_contents() method only once each time after the **file_name**
        trait is modified. In all other cases, the cached value
        **_file_contents**, which maintained by the @cached_property wrapper
        code, is returned.

        Note the use, in the example, of the **observe** metadata attribute
        to specify that the value of **file_contents** depends on
        **file_name**, so that _get_file_contents() is called only when
        **file_name** changes. For details, see the traits.traits.Property()
        function.
    """
    name = TraitsCache + function.__name__[5:]

    def decorator(self):
        result = self.__dict__.get(name, Undefined)
        if result is Undefined:
            self.__dict__[name] = result = function(self)

        return result

    decorator.cached_property = True

    return decorator


def property_depends_on(dependency, settable=False, flushable=False):
    """ Marks the following method definition as being a "cached property"
        that depends on the specified extended trait names. That is, it is a
        property getter which, for performance reasons, caches its most
        recently computed result in an attribute whose name is of the form:
        *_traits_cache_name*, where *name* is the name of the property. A
        method marked as being a cached property needs only to compute and
        return its result. The @property_depends_on decorator automatically
        wraps the decorated method in cache management code that will cache the
        most recently computed value and flush the cache when any of the
        specified dependencies are modified, thus eliminating the need to write
        boilerplate cache management code explicitly. For example::

            file_name = File
            file_contents = Property

            @property_depends_on('file_name')
            def _get_file_contents(self):
                with open(self.file_name, 'rb') as fh:
                    return fh.read()

        In this example, accessing the *file_contents* trait calls the
        _get_file_contents() method only once each time after the **file_name**
        trait is modified. In all other cases, the cached value
        **_file_contents**, which is maintained by the @cached_property wrapper
        code, is returned.
    """

    def decorator(function):
        name = TraitsCache + function.__name__[5:]

        def wrapper(self):
            result = self.__dict__.get(name, Undefined)
            if result is Undefined:
                self.__dict__[name] = result = function(self)

            return result

        wrapper.cached_property = True
        wrapper.depends_on = dependency
        wrapper.settable = settable
        wrapper.flushable = flushable

        return wrapper

    return decorator


def weak_arg(arg):
    """ Create a weak reference to arg and wrap the function so that the
    dereferenced weakref is passed as the first argument. If arg has been
    deleted then the function is not called.
    """
    # Create the weak reference
    weak_arg = weakref.ref(arg)

    def decorator(function):
        # We need multiple wrappers to traits can find the number of arguments.
        # The all just dereference the weak reference and the call the
        # function if it is not None.
        def wrapper0():
            arg = weak_arg()
            if arg is not None:
                return function(arg)

        def wrapper1(arg1):
            arg = weak_arg()
            if arg is not None:
                return function(arg, arg1)

        def wrapper2(arg1, arg2):
            arg = weak_arg()
            if arg is not None:
                return function(arg, arg1, arg2)

        def wrapper3(arg1, arg2, arg3):
            arg = weak_arg()
            if arg is not None:
                return function(arg, arg1, arg2, arg3)

        def wrapper4(arg1, arg2, arg3, arg4):
            arg = weak_arg()
            if arg is not None:
                return function(arg, arg1, arg2, arg3, arg4)

        def wrappern(*args):
            arg = weak_arg()
            if arg is not None:
                function(arg, *args)

        # Return the correct wrapper depending on the arg count
        args = function.__code__.co_argcount - 1
        if args == 0:
            return wrapper0
        elif args == 1:
            return wrapper1
        elif args == 2:
            return wrapper2
        elif args == 3:
            return wrapper3
        elif args == 4:
            return wrapper4
        else:
            return wrappern

    return decorator


class HasTraits(CHasTraits, metaclass=MetaHasTraits):
    """ Enables any Python class derived from it to have trait attributes.

    Most of the methods of HasTraits operated by default only on the trait
    attributes explicitly defined in the class definition. They do not operate
    on trait attributes defined by way of wildcards or by calling
    **add_trait()**.
    For example::

        >>> class Person(HasTraits):
        ...     name = Str
        ...     age  = Int
        ...     temp_ = Any
        >>> bob = Person()
        >>> bob.temp_lunch = 'sandwich'
        >>> bob.add_trait('favorite_sport', Str('football'))
        >>> print(bob.trait_names())
        ['trait_added', 'age', 'name']

    In this example, the trait_names() method returns only the *age* and
    *name* attributes defined on the Person class. (The **trait_added**
    attribute is an explicit trait event defined on the HasTraits class.)
    The wildcard attribute *temp_lunch* and the dynamically-added trait
    attribute *favorite_sport* are not listed.

    Subclass should avoid defining new traits and/or methods with names
    starting with "trait" or "_trait" to avoid overshadowing existing methods,
    unless it has been documented as being safe to do so.
    """

    # -- Trait Prefix Rules ---------------------------------------------------

    #: Make traits 'property cache' values private with no type checking:
    _traits_cache__ = Any(private=True, transient=True)

    # -- Class Variables ------------------------------------------------------

    #: Mapping from dispatch type to notification wrapper class type
    wrappers = {
        "same": TraitChangeNotifyWrapper,
        "extended": ExtendedTraitChangeNotifyWrapper,
        "new": NewTraitChangeNotifyWrapper,
        "fast_ui": FastUITraitChangeNotifyWrapper,
        "ui": FastUITraitChangeNotifyWrapper,
    }

    # -- Trait Definitions ----------------------------------------------------

    #: An event fired when a new trait is dynamically added to the object. The
    #: value is the name of the trait that was added.
    trait_added = Event(Str())

    #: An event that can be fired to indicate that the state of the object has
    #: been modified.
    trait_modified = Event()

    def _trait_added_changed(self, name):
        """ Handles a 'trait_added' event being fired.
        """
        # fixme: This test should be made more comprehensive by also verifying
        # that if the trait name does end in '_items', its base trait is also
        # a list or dictionary (in order to eliminate a false positive on an
        # unfortunately named trait:
        trait = self.trait(name)
        if (trait.type == "delegate") and (name[-6:] != "_items"):
            self._init_trait_delegate_listener(
                name, "delegate", get_delegate_pattern(name, trait)
            )

    @classmethod
    def add_class_trait(cls, name, *trait):
        """ Adds a named trait attribute to this class.

        Also adds the same attribute to all subclasses.

        Parameters
        ----------
        name : str
            Name of the attribute to add.
        *trait :
            A trait or a value that can be converted to a trait using Trait()
            Trait definition of the attribute. It can be a single value or
            a list equivalent to an argument list for the Trait() function.

        """

        # Make sure a trait argument was specified:
        if len(trait) == 0:
            raise ValueError("No trait definition was specified.")

        # Make sure only valid traits get added:
        if len(trait) > 1:
            trait = Trait(*trait)
        else:
            trait = trait_for(trait[0])

        # Add the trait to the class:
        cls._add_class_trait(name, trait, is_subclass=False)

        # Also add the trait to all subclasses of this class:
        for subclass in cls.trait_subclasses(True):
            subclass._add_class_trait(name, trait, is_subclass=True)

    @classmethod
    def _add_class_trait(cls, name, trait, is_subclass):
        """
        Add a named trait attribute to this class.

        Does not affect subclasses.

        Parameters
        ----------
        name : str
            Name of the attribute to add.
        trait : CTrait
            The trait to be added.
        is_subclass : bool
            True if we're adding the trait to a strict subclass of the
            original class that add_class_trait was called for. This is used
            to decide how to behave if ``cls`` already has a trait named
            ``name``: in that circumstance, if ``is_subclass`` is False, an
            error will be raised, while if ``is_subclass`` is True, no trait
            will be added.

        Raises
        ------
        TraitError
            If a trait with the given name already exists, and is_subclass
            is ``False``.
        """
        # Get a reference to the class's dictionary and 'prefix' traits:
        class_dict = cls.__dict__
        prefix_traits = class_dict[PrefixTraits]

        # See if the trait is a 'prefix' trait:
        if name[-1:] == "_":
            name = name[:-1]
            if name in prefix_traits:
                if is_subclass:
                    return
                raise TraitError("The '%s_' trait is already defined." % name)
            prefix_traits[name] = trait

            # Otherwise, add it to the list of known prefixes:
            prefix_list = prefix_traits["*"]
            prefix_list.append(name)

            # Resort the list from longest to shortest:
            prefix_list.sort(key=len, reverse=True)

            return

        # Check to see if the trait is already defined:
        class_traits = class_dict[ClassTraits]
        if class_traits.get(name) is not None:
            if is_subclass:
                return
            raise TraitError("The '%s' trait is already defined." % name)

        # Check to see if the trait has additional sub-traits that need to be
        # defined also:
        handler = trait.handler
        if handler is not None:
            if handler.has_items:
                cls._add_class_trait(
                    name + "_items",
                    handler.items_event(),
                    is_subclass=is_subclass,
                )
            if handler.is_mapped:
                cls._add_class_trait(
                    name + "_",
                    mapped_trait_for(trait, name),
                    is_subclass=is_subclass,
                )

        # Make the new trait inheritable (if allowed):
        if trait.is_base is not False:
            class_dict[BaseTraits][name] = trait

        # See if there are any static notifiers defined:
        handlers = [
            _get_method(cls, "_%s_changed" % name),
            _get_method(cls, "_%s_fired" % name),
        ]

        # Add any special trait defined event handlers:
        _add_event_handlers(trait, cls, handlers)

        # Add the 'anytrait' handler (if any):
        handlers.append(prefix_traits.get("@"))

        # Filter out any 'None' values:
        handlers = [h for h in handlers if h is not None]

        # If there are and handlers, add them to the trait's notifier's list:
        if len(handlers) > 0:
            trait = _clone_trait(trait)
            _add_notifiers(trait._notifiers(True), handlers)

        # Finally, add the new trait to the class trait dictionary:
        class_traits[name] = trait

    @classmethod
    def set_trait_dispatch_handler(cls, name, klass, override=False):
        """ Sets a trait notification dispatch handler.
        """
        try:
            if issubclass(klass, TraitChangeNotifyWrapper):
                if (not override) and (name in cls.wrappers):
                    raise TraitError(
                        "A dispatch handler called '%s' has "
                        "already been defined." % name
                    )
                cls.wrappers[name] = klass
                return
        except TypeError:
            pass
        raise TraitError(
            "%s is not a subclass of TraitChangeNotifyWrapper." % klass
        )

    @classmethod
    def trait_subclasses(cls, all=False):
        """ Returns a list of the immediate (or all) subclasses of this class.

        Parameters
        ----------
        all : bool
            Indicates whether to return all subclasses of this class. If
            False, only immediate subclasses are returned.

        """
        if not all:
            return cls.__subclasses__()
        return cls._trait_subclasses([])

    @classmethod
    def _trait_subclasses(cls, subclasses):
        for subclass in cls.__subclasses__():
            if subclass not in subclasses:
                subclasses.append(subclass)
                subclass._trait_subclasses(subclasses)
        return subclasses

    def has_traits_interface(self, *interfaces):
        """Returns whether the object implements a specified traits interface.

        Tests whether the object implements one or more of the interfaces
        specified by *interfaces*. Return **True** if it does, and **False**
        otherwise.

        Parameters
        ----------
        *interfaces :
            One or more traits Interface (sub)classes.
        """
        return isinstance(self, interfaces)

    def __getstate__(self):
        """ Returns a dictionary of traits to pickle.

        In general, avoid overriding __getstate__ in subclasses. Instead, mark
        traits that should not be pickled with 'transient = True' metadata.

        In cases where this strategy is not sufficient, override __getstate__
        in subclasses using the following pattern to remove items that should
        not be persisted::

            def __getstate__(self):
                state = super().__getstate__()
                for key in ['foo', 'bar']:
                    if key in state:
                        del state[key]
                return state
        """
        # Save all traits which do not have any 'transient' metadata:
        result = self.trait_get(transient=is_none)

        # Add all delegate traits that explicitly have 'transient = False'
        # metadata:
        dic = self.__dict__
        result.update(
            dict(
                [
                    (name, dic[name])
                    for name in self.trait_names(
                        type="delegate", transient=False
                    )
                    if name in dic
                ]
            )
        )

        # If this object implements ISerializable, make sure that all
        # contained HasTraits objects in its persisted state also implement
        # ISerializable:
        if self.has_traits_interface(ISerializable):
            for name, value in result.items():
                if not _is_serializable(value):
                    raise TraitError(
                        "The '%s' trait of a '%s' instance "
                        "contains the unserializable value: %s"
                        % (name, self.__class__.__name__, value)
                    )

        # Store the traits version in the state dictionary (if possible):
        result.setdefault("__traits_version__", TraitsVersion)

        # Return the final state dictionary:
        return result

    def __reduce_ex__(self, protocol):
        return (__newobj__, (self.__class__,), self.__getstate__())

    def __setstate__(self, state, trait_change_notify=True):
        """ Restores the previously pickled state of an object.
        """
        pop = state.pop
        if pop("__traits_version__", None) is None:
            # If the state was saved by a version of Traits prior to 3.0, then
            # use Traits 2.0 compatible code to restore it:
            values = [
                (name, pop(name)) for name in pop("__HasTraits_restore__", [])
            ]
            self.__dict__.update(state)
            self.trait_set(
                trait_change_notify=trait_change_notify, **dict(values)
            )
        else:
            # Otherwise, apply the Traits 3.0 restore logic:
            self._init_trait_listeners()
            self._init_trait_observers()
            self.trait_set(trait_change_notify=trait_change_notify, **state)
            self._post_init_trait_listeners()
            self._post_init_trait_observers()
            self.traits_init()

        self._trait_set_inited()

    def trait_get(self, *names, **metadata):
        """ Retrieve trait values for one or more traits.

        This function can be called in one of three ways. In the first form,
        the user passes the names of one or more traits to be retrieved::

            my_object.trait_get("trait_name1", "trait_name2")

        In the second form, the user passes a list of zero or more names of
        traits::

            my_object.trait_get(["trait_name1", "trait_name2"])

        In the final form, no trait names are passed, and all trait names
        and trait values are returned, subject to the given metadata filters::

            my_object.trait_get(transient=True, frombicated=False)

        In all cases, a dictionary mapping trait names to trait values is
        returned.

        For the first two forms, if any name does not correspond to a defined
        trait, it is not included in the result.

        Parameters
        ----------
        *names
            Names of the traits to look up, or a single positional argument
            providing a sequence of trait names.
        **metadata
            Metadata information used to filter the traits to return. This
            information is used only when no names are provided.

        Returns
        -------
        result : dict
            A dictionary mapping the selected trait names to their
            corresponding values.
        """

        result = {}
        n = len(names)
        if (n == 1) and (type(names[0]) in SequenceTypes):
            names = names[0]
        elif n == 0:
            names = self.trait_names(**metadata)

        # Sentinel for missing attributes.
        missing = object()
        for name in names:
            value = getattr(self, name, missing)
            if value is not missing:
                result[name] = value

        return result

    def trait_set(self, trait_change_notify=True, **traits):
        """ Shortcut for setting object trait attributes.

        Treats each keyword argument to the method as the name of a trait
        attribute and sets the corresponding trait attribute to the value
        specified. This is a useful shorthand when a number of trait attributes
        need to be set on an object, or a trait attribute value needs to be set
        in a lambda function. For example, you can write::

            person.trait_set(name='Bill', age=27)

        instead of::

            person.name = 'Bill'
            person.age = 27

        Parameters
        ----------
        trait_change_notify : bool
            If **True** (the default), then each value assigned may generate a
            trait change notification. If **False**, then no trait change
            notifications will be generated. (see also: trait_setq)
        **traits :
            Key/value pairs, the trait attributes and their values to be
            set

        Returns
        -------
        self :
            The method returns this object, after setting attributes.
        """
        if not trait_change_notify:
            self._trait_change_notify(False)
            try:
                for name, value in traits.items():
                    setattr(self, name, value)
            finally:
                self._trait_change_notify(True)
        else:
            for name, value in traits.items():
                setattr(self, name, value)

        return self

    def trait_setq(self, **traits):
        """ Shortcut for setting object trait attributes.

        Treats each keyword argument to the method as the name of a trait
        attribute and sets the corresponding trait attribute to the value
        specified. This is a useful shorthand when a number of trait attributes
        need to be set on an object, or a trait attribute value needs to be set
        in a lambda function. For example, you can write::

            person.trait_setq(name='Bill', age=27)

        instead of::

            person.name = 'Bill'
            person.age = 27

        Parameters
        ----------
        **traits :
            Key/value pairs, the trait attributes and their values to be set.
            No trait change notifications will be generated for any values
            assigned (see also: trait_set).

        Returns
        -------
        self :
            The method returns this object, after setting attributes.
        """
        return self.trait_set(trait_change_notify=False, **traits)

    def reset_traits(self, traits=None, **metadata):
        """ Resets some or all of an object's trait attributes to their default
        values.

        Resets each of the traits whose names are specified in the *traits*
        list to their default values. If *traits* is None or omitted, the
        method resets all explicitly-defined object trait attributes to their
        default values. Note that this does not affect wildcard trait
        attributes or trait attributes added via add_trait(), unless they are
        explicitly named in *traits*.

        Parameters
        ----------
        traits : list of strings
            Names of trait attributes to reset.

        Returns
        -------
        unresetable : list of strings
            A list of attributes that the method was unable to reset, which is
            empty if all the attributes were successfully reset.
        """
        unresetable = []

        if traits is None:
            traits = self.trait_names(**metadata)

        for name in traits:
            try:
                delattr(self, name)
            except (AttributeError, TraitError):
                unresetable.append(name)

        return unresetable

    def copyable_trait_names(self, **metadata):
        """ Returns the list of trait names to copy or clone by default.
        """

        metadata.setdefault("transient", lambda t: t is not True)
        return self.trait_names(**metadata)

    def all_trait_names(self):
        """ Returns the list of all trait names, including implicitly defined
            traits.
        """
        return list(self.__class_traits__.keys())

    def __dir__(self):
        """ Returns the list of trait names when calling the dir() builtin on
            the object. This enables tab-completion in IPython.
        """
        return super().__dir__() + self.trait_names()

    def copy_traits(
        self, other, traits=None, memo=None, copy=None, **metadata
    ):
        """ Copies another object's trait attributes into this one.

        Parameters
        ----------
        other : object
            The object whose trait attribute values should be copied.
        traits : list of strings
            A list of names of trait attributes to copy. If None or
            unspecified, the set of names returned by trait_names() is used.
            If 'all' or an empty list, the set of names returned by
            all_trait_names() is used.
        memo : dict
            A dictionary of objects that have already been copied.
        copy : None | 'deep' | 'shallow'
            The type of copy to perform on any trait that does not have
            explicit 'copy' metadata. A value of None means 'copy reference'.

        Returns
        -------
        unassignable : list of strings
            A list of attributes that the method was unable to copy, which is
            empty if all the attributes were successfully copied.

        """

        if traits is None:
            traits = self.copyable_trait_names(**metadata)
        elif (traits == "all") or (len(traits) == 0):
            traits = self.all_trait_names()
            if memo is not None:
                memo["traits_to_copy"] = "all"

        unassignable = []
        deferred = []
        deep_copy = copy == "deep"
        shallow_copy = copy == "shallow"

        for name in traits:
            try:
                trait = self.trait(name)
                if trait.type in DeferredCopy:
                    deferred.append(name)
                    continue

                base_trait = other.base_trait(name)
                if base_trait.type == "event":
                    continue

                value = getattr(other, name)
                copy_type = base_trait.copy
                if copy_type == "shallow":
                    value = copy_module.copy(value)
                elif copy_type == "ref":
                    pass
                elif (copy_type == "deep") or deep_copy:
                    if memo is None:
                        value = copy_module.deepcopy(value)
                    else:
                        value = copy_module.deepcopy(value, memo)
                elif shallow_copy:
                    value = copy_module.copy(value)

                setattr(self, name, value)
            except:
                unassignable.append(name)

        for name in deferred:
            try:
                value = getattr(other, name)
                copy_type = other.base_trait(name).copy
                if copy_type == "shallow":
                    value = copy_module.copy(value)
                elif copy_type == "ref":
                    pass
                elif (copy_type == "deep") or deep_copy:
                    if memo is None:
                        value = copy_module.deepcopy(value)
                    else:
                        value = copy_module.deepcopy(value, memo)
                elif shallow_copy:
                    value = copy_module.copy(value)

                setattr(self, name, value)
            except:
                unassignable.append(name)

        return unassignable

    def clone_traits(self, traits=None, memo=None, copy=None, **metadata):
        """ Clones a new object from this one, optionally copying only a
        specified set of traits.

        Creates a new object that is a clone of the current object. If *traits*
        is None (the default), then all explicit trait attributes defined
        for this object are cloned. If *traits* is 'all' or an empty list, the
        list of traits returned by all_trait_names() is used; otherwise,
        *traits* must be a list of the names of the trait attributes to be
        cloned.

        Parameters
        ----------
        traits : list of strings
            The list of names of the trait attributes to copy.
        memo : dict
            A dictionary of objects that have already been copied.
        copy : str
            The type of copy ``deep`` or ``shallow`` to perform on any trait
            that does not have explicit 'copy' metadata. A value of None means
            'copy reference'.

        Returns
        -------
        new :
            The newly cloned object.
        """
        if memo is None:
            memo = {}

        if traits is None:
            traits = self.copyable_trait_names(**metadata)
        elif (traits == "all") or (len(traits) == 0):
            traits = self.all_trait_names()
            memo["traits_to_copy"] = "all"

        memo["traits_copy_mode"] = copy
        new = self.__new__(self.__class__)
        memo[id(self)] = new
        new._init_trait_listeners()
        new._init_trait_observers()
        new.copy_traits(self, traits, memo, copy, **metadata)
        new._post_init_trait_listeners()
        new._post_init_trait_observers()
        new.traits_init()
        new._trait_set_inited()

        return new

    def __deepcopy__(self, memo):
        """ Creates a deep copy of the object.
        """
        return self.clone_traits(
            memo=memo,
            traits=memo.get("traits_to_copy"),
            copy=memo.get("traits_copy_mode"),
        )

    def edit_traits(
        self,
        view=None,
        parent=None,
        kind=None,
        context=None,
        handler=None,
        id="",
        scrollable=None,
        **args
    ):
        """ Displays a user interface window for editing trait attribute
        values.

        Parameters
        ----------
        view : View or string
            A View object (or its name) that defines a user interface for
            editing trait attribute values of the current object. If the view
            is defined as an attribute on this class, use the name of the
            attribute. Otherwise, use a reference to the view object. If this
            attribute is not specified, the View object returned by
            trait_view() is used.
        parent : toolkit control
            The reference to a user interface component to use as the parent
            window for the object's UI window.
        kind : str
            The type of user interface window to create. See the
            **traitsui.view.kind_trait** trait for values and
            their meanings. If *kind* is unspecified or None, the **kind**
            attribute of the View object is used.
        context : object or dictionary
            A single object or a dictionary of string/object pairs, whose trait
            attributes are to be edited. If not specified, the current object
            is used.
        handler : Handler
            A handler object used for event handling in the dialog box. If
            None, the default handler for Traits UI is used.
        id : str
            A unique ID for persisting preferences about this user interface,
            such as size and position. If not specified, no user preferences
            are saved.
        scrollable : bool
            Indicates whether the dialog box should be scrollable. When set to
            True, scroll bars appear on the dialog box if it is not large
            enough to display all of the items in the view at one time.

        Returns
        -------
        A UI object.
        """
        if context is None:
            context = self

        view = self.trait_view(view)

        return view.ui(
            context,
            parent,
            kind,
            self.trait_view_elements(),
            handler,
            id,
            scrollable,
            args,
        )

    def trait_context(self):
        """ Returns the default context to use for editing or configuring
            traits.
        """
        return {"object": self}

    def trait_view(self, name=None, view_element=None):
        """ Gets or sets a ViewElement associated with an object's class.

        If both *name* and *view_element* are specified, the view element is
        associated with *name* for the current object's class. (That is,
        *view_element* is added to the ViewElements object associated with
        the current object's class, indexed by *name*.)

        If only *name* is specified, the function returns the view element
        object associated with *name*, or None if *name* has no associated
        view element. View elements retrieved by this function are those that
        are bound to a class attribute in the class definition, or that are
        associated with a name by a previous call to this method.

        If neither *name* nor *view_element* is specified, the method returns a
        View object, based on the following order of preference:

        1. If there is a View object named ``traits_view`` associated with the
           current object, it is returned.
        2. If there is exactly one View object associated the current
           object, it is returned.
        3. Otherwise, it returns a View object containing items for all the
           non-event trait attributes on the current object.

        Parameters
        ----------
        name : str
            Name of a view element
        view_element : ViewElement
            View element to associate

        Returns
        -------
        A view element.
        """
        return self.__class__._trait_view(
            name,
            view_element,
            self.default_traits_view,
            self.trait_view_elements,
            self.visible_traits,
            self,
        )

    @classmethod
    def class_trait_view(cls, name=None, view_element=None):
        return cls._trait_view(
            name,
            view_element,
            cls.class_default_traits_view,
            cls.class_trait_view_elements,
            cls.class_visible_traits,
            None,
        )

    @classmethod
    def _trait_view(
        cls,
        name,
        view_element,
        default_name,
        view_elements,
        trait_selector_f,
        handler,
    ):
        """ Gets or sets a ViewElement associated with an object's class.
        """
        # If a view element was passed instead of a name or None, return it:
        if isinstance(name, AbstractViewElement):
            return name

        # Get the ViewElements object associated with the class:
        view_elements = view_elements()

        # The following test should only succeed for objects created before
        # traits has been fully initialized (such as the default Handler):
        if view_elements is None:
            return None

        if name:
            if view_element is None:
                # If only a name was specified, return the ViewElement it
                # matches, if any:
                result = view_elements.find(name)
                if (result is None) and (handler is not None):
                    method = getattr(handler, name, None)
                    if callable(method):
                        result = method()

                return result

            # Otherwise, save the specified ViewElement under the name
            # specified:
            view_elements.content[name] = view_element

            return None

        # Get the default view/view name:
        name = default_name()

        # If the default is a View, return it:
        if isinstance(name, AbstractViewElement):
            return name

        # Otherwise, get all View objects associated with the object's class:
        names = view_elements.filter_by()

        # If the specified default name is in the list, return its View:
        if name in names:
            return view_elements.find(name)

        if handler is not None:
            method = getattr(handler, name, None)
            if callable(method):
                result = method()
                if isinstance(result, AbstractViewElement):
                    return result

        # If there is only one View, return it:
        if len(names) == 1:
            return view_elements.find(names[0])

        # Otherwise, create and return a View based on the set of editable
        # traits defined for the object:
        from traitsui.api import View

        return View(trait_selector_f(), buttons=["OK", "Cancel"])

    def default_traits_view(self):
        """ Returns the name of the default traits view for the object's class.
        """
        return self.__class__.class_default_traits_view()

    @classmethod
    def class_default_traits_view(cls):
        """ Returns the name of the default traits view for the class.
        """
        return DefaultTraitsView

    def trait_views(self, klass=None):
        """ Returns a list of the names of all view elements associated with
        the current object's class.

        If *klass* is specified, the list of names is filtered such that only
        objects that are instances of the specified class are returned.

        Parameters
        ----------
        klass : class
            A class, such that all returned names must correspond to instances
            of this class. Possible values include:

            * Group
            * Item
            * View
            * ViewElement
            * ViewSubElement
        """
        view_elements = self.__class__.__dict__[ViewTraits]
        if isinstance(view_elements, dict):
            view_elements = self._init_trait_view_elements()
        return view_elements.filter_by(klass)

    def trait_view_elements(self):
        """ Returns the ViewElements object associated with the object's
        class.

        The returned object can be used to access all the view elements
        associated with the class.
        """
        return self.__class__.class_trait_view_elements()

    @classmethod
    def class_trait_view_elements(cls):
        """ Returns the ViewElements object associated with the class.

        The returned object can be used to access all the view elements
        associated with the class.
        """
        view_elements = cls.__dict__[ViewTraits]
        if isinstance(view_elements, dict):
            view_elements = cls._init_trait_view_elements()
        return view_elements

    @classmethod
    def _init_trait_view_elements(cls):
        """ Lazily Initialize the ViewElements object from a dictionary. """
        from traitsui.view_elements import ViewElements

        hastraits_bases = [
            base for base in cls.__bases__
            if ClassTraits in base.__dict__
        ]
        view_elements = ViewElements()
        elements_dict = cls.__dict__[ViewTraits]

        for name, element in elements_dict.items():
            # Add the view element to the class's 'ViewElements' if it is
            # not already defined (duplicate definitions are errors):
            if name in view_elements.content:
                raise TraitError(
                    "Duplicate definition for view element '%s'" % name
                )

            view_elements.content[name] = element

            # Replace all substitutable view sub elements with 'Include'
            # objects, and add the substituted items to the
            # 'ViewElements':
            element.replace_include(view_elements)

        for base in hastraits_bases:
            # If the base class has a 'ViewElements' object defined, add it to
            # the 'parents' list of this class's 'ViewElements':
            parent_view_elements = base.class_trait_view_elements()
            if parent_view_elements is not None:
                view_elements.parents.append(parent_view_elements)

        setattr(cls, ViewTraits, view_elements)
        return view_elements

    def configure_traits(
        self,
        filename=None,
        view=None,
        kind=None,
        edit=None,
        context=None,
        handler=None,
        id="",
        scrollable=None,
        **args
    ):
        ### JMS: Is it correct to assume that non-modal options for 'kind'
        ###      behave modally when called from this method?
        """Creates and displays a dialog box for editing values of trait
        attributes, as if it were a complete, self-contained GUI application.

        This method is intended for use in applications that do not normally
        have a GUI. Control does not resume in the calling application until
        the user closes the dialog box.

        The method attempts to open and unpickle the contents of *filename*
        before displaying the dialog box. When editing is complete, the method
        attempts to pickle the updated contents of the object back to
        *filename*. If the file referenced by *filename* does not exist, the
        object is not modified before displaying the dialog box. If *filename*
        is unspecified or None, no pickling or unpickling occurs.

        If *edit* is True (the default), a dialog box for editing the
        current object is displayed. If *edit* is False or None, no
        dialog box is displayed. You can use ``edit=False`` if you want the
        object to be restored from the contents of *filename*, without being
        modified by the user.

        Parameters
        ----------
        filename : str
            The name (including path) of a file that contains a pickled
            representation of the current object. When this parameter is
            specified, the method reads the corresponding file (if it exists)
            to restore the saved values of the object's traits before
            displaying them. If the user confirms the dialog box (by clicking
            **OK**), the new values are written to the file. If this parameter
            is not specified, the values are loaded from the in-memory object,
            and are not persisted when the dialog box is closed.

            .. deprecated:: 6.0.0

        view : View or str
            A View object (or its name) that defines a user interface for
            editing trait attribute values of the current object. If the view
            is defined as an attribute on this class, use the name of the
            attribute. Otherwise, use a reference to the view object. If this
            attribute is not specified, the View object returned by
            trait_view() is used.
        kind : str
            The type of user interface window to create. See the
            **traitsui.view.kind_trait** trait for values and
            their meanings. If *kind* is unspecified or None, the **kind**
            attribute of the View object is used.
        edit : bool
            Indicates whether to display a user interface. If *filename*
            specifies an existing file, setting *edit* to False loads the
            saved values from that file into the object without requiring
            user interaction.

            .. deprecated:: 6.2.0

        context : object or dictionary
            A single object or a dictionary of string/object pairs, whose trait
            attributes are to be edited. If not specified, the current object
            is used
        handler : Handler
            A handler object used for event handling in the dialog box. If
            None, the default handler for Traits UI is used.
        id : str
            A unique ID for persisting preferences about this user interface,
            such as size and position. If not specified, no user preferences
            are saved.
        scrollable : bool
            Indicates whether the dialog box should be scrollable. When set to
            True, scroll bars appear on the dialog box if it is not large
            enough to display all of the items in the view at one time.

        Returns
        -------
        True on success.
        """
        if filename is not None:
            message = ('Restoring from pickle will not be supported starting '
                       'with traits 7.0.0')
            warnings.warn(message, DeprecationWarning)
            if os.path.exists(filename):
                with open(filename, "rb") as fd:
                    self.copy_traits(pickle.Unpickler(fd).load())

        if edit is None:
            edit = True
        else:
            message = (
                'The edit argument to configure_traits is '
                'deprecated, and will be removed in Traits 7.0.0'
            )
            warnings.warn(message, DeprecationWarning)

        if edit:
            from traitsui.api import toolkit

            if context is None:
                context = self
            rc = toolkit().view_application(
                context,
                self.trait_view(view),
                kind,
                handler,
                id,
                scrollable,
                args,
            )
            if rc and (filename is not None):
                with open(filename, "wb") as fd:
                    pickle.Pickler(fd, protocol=3).dump(self)
            return rc

        return True

    def editable_traits(self):
        """Returns an alphabetically sorted list of the names of non-event
        trait attributes associated with the current object.
        """
        names = self.trait_names(type=not_event, editable=not_false)
        names.sort()
        return names

    @classmethod
    def class_editable_traits(cls):
        """Returns an alphabetically sorted list of the names of non-event
        trait attributes associated with the current class.
        """
        names = cls.class_trait_names(type=not_event, editable=not_false)
        names.sort()
        return names

    def visible_traits(self):
        """Returns an alphabetically sorted list of the names of non-event
        trait attributes associated with the current object, that should be GUI
        visible
        """
        return self.trait_names(type=not_event, visible=not_false)

    @classmethod
    def class_visible_traits(cls):
        """Returns an alphabetically sorted list of the names of non-event
        trait attributes associated with the current class, that should be GUI
        visible
        """
        return cls.class_trait_names(type=not_event, visible=not_false)

    def print_traits(self, show_help=False, **metadata):
        """Prints the values of all explicitly-defined, non-event trait
        attributes on the current object, in an easily readable format.

        Parameters
        ----------
        show_help : bool
            Indicates whether to display additional descriptive information.
        """

        if len(metadata) > 0:
            names = self.trait_names(**metadata)
        else:
            names = self.trait_names(type=not_event)

        if len(names) == 0:
            print("")
            return

        result = []
        pad = max([len(x) for x in names]) + 1
        maxval = 78 - pad
        names.sort()

        for name in names:
            try:
                value = repr(getattr(self, name)).replace("\n", "\\n")
                if len(value) > maxval:
                    value = "%s...%s" % (
                        value[:(maxval - 2) // 2],
                        value[-((maxval - 3) // 2):],
                    )
            except:
                value = "<undefined>"
            lname = (name + ":").ljust(pad)
            if show_help:
                result.append(
                    "%s %s\n   The value must be %s."
                    % (lname, value, self.base_trait(name).setter.info())
                )
            else:
                result.append("%s %s" % (lname, value))

        print("\n".join(result))

    def _on_trait_change(
        self,
        handler,
        name=None,
        remove=False,
        dispatch="same",
        priority=False,
        target=None,
    ):
        """Causes the object to invoke a handler whenever a trait attribute
        is modified, or removes the association.

        Multiple handlers can be defined for the same object, or even for the
        same trait attribute on the same object. If *name* is not specified or
        is None, *handler* is invoked when any trait attribute on the
        object is changed.

        Parameters
        ----------
        handler : function
            A trait notification function for the attribute specified by
            *name*.
        name : str
            Specifies the trait attribute whose value changes trigger the
            notification.
        remove : bool
            If True, removes the previously-set association between
            *handler* and *name*; if False (the default), creates the
            association.
        """

        if type(name) is list:
            for name_i in name:
                self._on_trait_change(
                    handler, name_i, remove, dispatch, priority, target
                )

            return

        name = name or "anytrait"

        if remove:
            if name == "anytrait":
                notifiers = self._notifiers(False)
            else:
                trait = self._trait(name, 1)
                if trait is None:
                    return
                notifiers = trait._notifiers(False)

            if notifiers is not None:
                for i, notifier in enumerate(notifiers):
                    if notifier.equals(handler):
                        del notifiers[i]
                        notifier.dispose()
                        break

            return

        if name == "anytrait":
            notifiers = self._notifiers(True)
        else:
            notifiers = self._trait(name, 2)._notifiers(True)

        for notifier in notifiers:
            if notifier.equals(handler):
                break
        else:
            wrapper = self.wrappers[dispatch](handler, notifiers, target)

            if priority:
                notifiers.insert(0, wrapper)
            else:
                notifiers.append(wrapper)

    def observe(self, handler, expression, *, remove=False, dispatch="same"):
        """ Causes the object to invoke a handler whenever a trait attribute
        matching a specified pattern is modified, or removes the association.

        The *expression* parameter can be a single string or an Expression
        object. A list of expressions is also accepted.

        When *expression* is a string, its content should follow Traits Mini
        Language semantics:

        ============================== ======================================
        Expression                       Meaning
        ============================== ======================================
        ``item1.item2``                Observes trait *item2* on the object
                                       under trait *item1*.
                                       Changes to either *item1* or *item2*
                                       cause a notification to be fired.
        ``item1:item2``                Similar to the above, except changes
                                       to *item1* will not fire events
                                       (the ':' indicates no notifications).
        ``[item1, item2, ..., itemN]`` A list which matches any of the
                                       specified items. Each item can itself
                                       be an expression.
        ``items``                      Special keyword for observing a trait
                                       named *items* or items inside a list /
                                       dict / set.
        ``+metadata_name``             Matches any trait on the object having
                                       *metadata_name* metadata.
        ============================== ======================================

        All spaces will be ignored.

        The :py:class:`ObserverExpression` object supports
        the above features and more.

        Parameters
        ----------
        handler : callable(event)
            A callable that will be invoked when the observed trait changes.
            It must accept one argument, which is an event object providing
            information about the change.
            See :py:mod:`traits.observation.events` for details.
        expression : str or list or ObserverExpression
            A description of what traits are being observed.
            If this is a list, each item must be a string or an Expression.
        remove : boolean, optional
            Whether to remove the event handler. Default is to add the event
            handler.
        dispatch : str, optional
            A string indicating how the handler should be run.
            Default is to run on the same thread where the change occurs.

            Possible values are:

            =========== =======================================================
            value       dispatch
            =========== =======================================================
            ``same``    Run notifications on the same thread where the change
                        occurs. The notifications are executed immediately.
            ``ui``      Run notifications on the UI thread. If the current
                        thread is the UI thread, the notifications are executed
                        immediately; otherwise, they are placed on the UI
                        event queue.
            =========== =======================================================

        Raises
        ------
        NotifierNotFound
            When attempting to remove a handler that doesn't exist.
        """
        graphs = _compile_expression(expression)

        observe_api.apply_observers(
            object=self,
            graphs=graphs,
            handler=handler,
            dispatcher=_ObserverDispatchers[dispatch],
            remove=remove,
        )

    def on_trait_change(
        self,
        handler,
        name=None,
        remove=False,
        dispatch="same",
        priority=False,
        deferred=False,
        target=None,
    ):
        """Causes the object to invoke a handler whenever a trait attribute
        matching a specified pattern is modified, or removes the association.

        Multiple handlers can be defined for the same object, or even for the
        same trait attribute on the same object. If *name* is not specified or
        is None, *handler* is invoked when any trait attribute on the
        object is changed.

        The *name* parameter is a single *xname* or a list of *xname* names,
        where an *xname* is an extended name of the form::

            xname2[('.'|':') xname2]*

        An *xname2* is of the form::

            (xname3 | '['xname3[','xname3]*']') ['*']

        An *xname3* is of the form::

            xname | ['+'|'-'][name] | name['?' | ('+'|'-')[name]]

        A *name* is any valid Python attribute name. The semantic meaning of
        this notation is as follows:

        ================================ ======================================
        expression                       meaning
        ================================ ======================================
        ``item1.item2``                  means *item1* is a trait containing an
                                         object (or objects if *item1* is a
                                         list or dict) with a trait called
                                         *item2*. Changes to either *item1* or
                                         *item2* cause a notification to be
                                         generated.
        ``item1:item2``                  means *item1* is a trait containing an
                                         object (or objects if *item1* is a
                                         list or dict) with a trait called
                                         *item2*. Changes to *item2* cause a
                                         notification to be generated, while
                                         changes to *item1* do not (i.e., the
                                         ':' indicates that changes to the
                                         *link* object should not be reported).
        ``[item1, item2, ..., itemN]``   A list which matches any of the
                                         specified items. Note that at the
                                         topmost level, the surrounding square
                                         brackets are optional.
        ``name?``                        If the current object does not have an
                                         attribute called *name*, the reference
                                         can be ignored. If the '?' character
                                         is omitted, the current object must
                                         have a trait called *name*, otherwise
                                         an exception will be raised.
        ``prefix+``                      Matches any trait on the object whose
                                         name begins with *prefix*.
        ``+metadata_name``               Matches any trait on the object having
                                         *metadata_name* metadata.
        ``-metadata_name``               Matches any trait on the object which
                                         does not have *metadata_name*
                                         metadata.
        ``prefix+metadata_name``         Matches any trait on the object whose
                                         name begins with *prefix* and which
                                         has *metadata_name* metadata.
        ``prefix-metadata_name``         Matches any trait on the object
                                         whose name begins with *prefix* and
                                         which does not have *metadata_name*
                                         metadata.
        ``+``                            Matches all traits on the object.
        ``pattern*``                     Matches object graphs where *pattern*
                                         occurs one or more times (useful for
                                         setting up listeners on recursive data
                                         structures like trees or linked
                                         lists).
        ================================ ======================================

        Some examples of valid names and their meaning are as follows:

        ======================= ===============================================
        example                 meaning
        ======================= ===============================================
        ``foo,bar,baz``         Listen for trait changes to *object.foo*,
                                *object.bar*, and *object.baz*.
        ``['foo','bar','baz']`` Equivalent to 'foo,bar,baz', but may be more
                                useful in cases where the individual items are
                                computed.
        ``foo.bar.baz``         Listen for trait changes to
                                *object.foo.bar.baz* and report changes to
                                *object.foo*, *object.foo.bar* or
                                *object.foo.bar.baz*.
        ``foo:bar:baz``         Listen for changes to *object.foo.bar.baz*, and
                                only report changes to *object.foo.bar.baz*.
        ``foo.[bar,baz]``       Listen for trait changes to *object.foo.bar*
                                and *object.foo.baz*.
        ``[left,right]*.name``  Listen for trait changes to the *name* trait of
                                each node of a tree having *left* and *right*
                                links to other tree nodes, and where *object*
                                the method is applied to the root node of the
                                tree.
        ``+dirty``              Listen for trait changes on any trait in the
                                *object* which has the 'dirty' metadata set.
        ``foo.+dirty``          Listen for trait changes on any trait in
                                *object.foo* which has the 'dirty' metadata
                                set.
        ``foo.[bar,-dirty]``    Listen for trait changes on *object.foo.bar* or
                                any trait on *object.foo* which does not have
                                'dirty' metadata set.
        ======================= ===============================================


        Note that any of the intermediate (i.e., non-final) links in a
        pattern can be traits of type Instance, List or Dict. In the case
        of List and Dict traits, the subsequent portion of the pattern is
        applied to each item in the list, or value in the dictionary.

        For example, if the self.children is a list, 'children.name'
        listens for trait changes to the *name* trait for each item in the
        self.children list.

        Note that items added to or removed from a list or dictionary in
        the pattern will cause the *handler* routine to be invoked as well,
        since this is treated as an *implied* change to the item's trait
        being monitored.

        The signature of the *handler* supplied also has an effect on
        how changes to intermediate traits are processed. The five valid
        handler signatures are:

        1. handler()
        2. handler(new)
        3. handler(name,new)
        4. handler(object,name,new)
        5. handler(object,name,old,new)

        For signatures 1, 4 and 5, any change to any element of a path
        being listened to invokes the handler with information about the
        particular element that was modified (e.g., if the item being
        monitored is 'foo.bar.baz', a change to 'bar' will call *handler*
        with the following information:

        - object: object.foo
        - name:   bar
        - old:    old value for object.foo.bar
        - new:    new value for object.foo.bar

        If one of the intermediate links is a List or Dict, the call to
        *handler* may report an *_items* changed event. If in the previous
        example, *bar* is a List, and a new item is added to *bar*, then
        the information passed to *handler* would be:

        - object: object.foo
        - name:   bar_items
        - old:    Undefined
        - new:    TraitListEvent whose *added* trait contains the new item
                  added to *bar*.

        For signatures 2 and 3, the *handler* does not receive enough
        information to discern between a change to the final trait being
        listened to and a change to an intermediate link. In this case,
        the event dispatcher will attempt to map a change to an
        intermediate link to its effective change on the final trait. This
        only works if all of the intermediate links are single values (such
        as an Instance or Any trait) and not Lists or Dicts. If the modified
        intermediate trait or any subsequent intermediate trait preceding
        the final trait is a List or Dict, then a TraitError is raised,
        since the effective value for the final trait cannot in general be
        resolved unambiguously. To prevent TraitErrors in this case, use the
        ':' separator to suppress notifications for changes to any of the
        intermediate links.

        Handler signature 1 also has the special characteristic that if a
        final trait is a List or Dict, it will automatically handle '_items'
        changed events for the final trait as well. This can be useful in
        cases where the *handler* only needs to know that some aspect of the
        final trait has been changed. For all other *handler* signatures,
        you must explicitly specify the 'xxx_items' trait if you want to
        be notified of changes to any of the items of the 'xxx' trait.

        Parameters
        ----------
        handler : function
            A trait notification function for the *name* trait attribute, with
            one of the signatures described below.
        name : str
            The name of the trait attribute whose value changes trigger the
            notification. The *name* can specify complex patterns of trait
            changes using an extended *name* syntax, which is described below.
        remove : bool
            If True, removes the previously-set association between
            *handler* and *name*; if False (the default), creates the
            association.
        dispatch : str
            A string indicating the thread on which notifications must be run.
            Possible values are:

            =========== =======================================================
            value       dispatch
            =========== =======================================================
            ``same``    Run notifications on the same thread as this one.
            ``ui``      Run notifications on the UI thread. If the current
                        thread is the UI thread, the notifications are executed
                        immediately; otherwise, they are placed on the UI
                        event queue.
            ``fast_ui`` Alias for ``ui``.
            ``new``     Run notifications in a new thread.
            =========== =======================================================

        See Also
        --------
        HasTraits.observe : A newer API for defining traits notifications.
        """
        # Check to see if we can do a quick exit to the basic trait change
        # handler:
        if (
            isinstance(name, str)
            and (extended_trait_pat.match(name) is None)
        ) or (name is None):
            self._on_trait_change(
                handler, name, remove, dispatch, priority, target
            )

            return

        from .traits_listener import (
            TraitsListener,
            ListenerParser,
            ListenerHandler,
            ListenerNotifyWrapper,
        )

        if isinstance(name, list):
            for name_i in name:
                self.on_trait_change(
                    handler,
                    name=name_i,
                    remove=remove,
                    dispatch=dispatch,
                    priority=priority,
                    deferred=deferred,
                    target=target,
                )

            return

        # Make sure we have a name string:
        name = (name or "anytrait").strip()

        if remove:
            dict = self.__dict__.get(TraitsListener)
            if dict is not None:
                listeners = dict.get(name)
                if listeners is not None:
                    for i, wrapper in enumerate(listeners):
                        if wrapper.equals(handler):
                            del listeners[i]
                            if len(listeners) == 0:
                                del dict[name]
                                if len(dict) == 0:
                                    del self.__dict__[TraitsListener]
                            wrapper.listener.unregister(self)
                            wrapper.dispose()
                            break
        else:
            dict = self.__dict__.setdefault(TraitsListener, {})
            listeners = dict.setdefault(name, [])
            for wrapper in listeners:
                if wrapper.equals(handler):
                    break
            else:
                # The listener notify wrapper needs a reference to the
                # listener, and the listener needs a (weak) reference to the
                # wrapper. We first construct the wrapper with a listener of
                # `None`, then construct the listener with its reference to the
                # wrapper, then we replace the `None` listener with the correct
                # one.
                lnw = ListenerNotifyWrapper(handler, self, name, None, target)
                listener = ListenerParser(
                    name,
                    handler=ListenerHandler(handler),
                    wrapped_handler_ref=weakref.ref(lnw),
                    dispatch=dispatch,
                    priority=priority,
                    deferred=deferred,
                    handler_type=lnw.type,
                ).listener
                lnw.listener = listener
                listener.register(self)
                listeners.append(lnw)

    # A synonym for 'on_trait_change'
    on_trait_event = on_trait_change

    def sync_trait(
        self, trait_name, object, alias=None, mutual=True, remove=False
    ):
        """Synchronizes the value of a trait attribute on this object with a
        trait attribute on another object.

        In mutual synchronization, any change to the value of the specified
        trait attribute of either object results in the same value being
        assigned to the corresponding trait attribute of the other object.
        In one-way synchronization, any change to the value of the attribute
        on this object causes the corresponding trait attribute of *object* to
        be updated, but not vice versa.

        For ``List`` traits, the list's items are also synchronized, so that
        mutations to this trait's list will be reflected in the synchronized
        list (and vice versa in the case of mutual synchronization). For
        ``Dict`` and ``Set`` traits, items are not synchronized.

        Parameters
        ----------
        name : str
            Name of the trait attribute on this object.
        object : object
            The object with which to synchronize.
        alias : str
            Name of the trait attribute on *other*; if None or omitted, same
            as *name*.
        mutual : bool or int
            Indicates whether synchronization is mutual (True or non-zero)
            or one-way (False or zero)
        remove : bool or int
            Indicates whether synchronization is being added (False or zero)
            or removed (True or non-zero)
        """
        if alias is None:
            alias = trait_name

        is_list = self._is_list_trait(trait_name) and object._is_list_trait(
            alias
        )

        if remove:
            info = self._get_sync_trait_info()
            dic = info.get(trait_name)
            if dic is not None:
                key = (id(object), alias)
                if key in dic:
                    del dic[key]

                    if len(dic) == 0:
                        del info[trait_name]
                        self._on_trait_change(
                            self._sync_trait_modified, trait_name, remove=True
                        )

                        if is_list:
                            self._on_trait_change(
                                self._sync_trait_items_modified,
                                trait_name + "_items",
                                remove=True,
                            )

            if mutual:
                object.sync_trait(alias, self, trait_name, False, True)

            return

        # Callback to use when the synced object goes out of scope. In order
        # to avoid reference cycles, this must not be a member function. See
        # Github issue #69 for more detail.
        def _sync_trait_listener_deleted(ref, info):
            for key, dic in list(info.items()):
                if key != "":
                    for name, value in list(dic.items()):
                        if ref is value[0]:
                            del dic[name]
                    if len(dic) == 0:
                        del info[key]

        info = self._get_sync_trait_info()
        dic = info.setdefault(trait_name, {})
        key = (id(object), alias)

        callback = lambda ref: _sync_trait_listener_deleted(ref, info)
        value = (weakref.ref(object, callback), alias)

        if key not in dic:
            if len(dic) == 0:
                self._on_trait_change(self._sync_trait_modified, trait_name)
                if is_list:
                    self._on_trait_change(
                        self._sync_trait_items_modified, trait_name + "_items"
                    )
            dic[key] = value
            setattr(object, alias, getattr(self, trait_name))

        if mutual:
            object.sync_trait(alias, self, trait_name, False)

    def _get_sync_trait_info(self):
        info = getattr(self, "__sync_trait__", None)
        if info is None:
            self.__dict__["__sync_trait__"] = info = {}
            info[""] = {}

        return info

    def _sync_trait_modified(self, object, name, old, new):
        info = self.__sync_trait__
        if name not in info:
            return
        locked = info[""]
        locked[name] = None
        for object, object_name in info[name].values():
            object = object()
            if object_name not in object._get_sync_trait_info()[""]:
                try:
                    setattr(object, object_name, new)
                except:
                    pass

        del locked[name]

    def _sync_trait_items_modified(self, object, name, old, event):
        n0 = event.index
        n1 = n0 + len(event.removed)
        name = name[:-6]
        info = self.__sync_trait__
        locked = info[""]
        locked[name] = None
        for object, object_name in info[name].values():
            object = object()
            if object_name not in object._get_sync_trait_info()[""]:
                try:
                    getattr(object, object_name)[n0:n1] = event.added
                except:
                    pass

        del locked[name]

    def _is_list_trait(self, trait_name):
        handler = self.base_trait(trait_name).handler

        return (handler is not None) and (
            handler.default_value_type == DefaultValue.trait_list_object
        )

    def add_trait(self, name, *trait):
        """Adds a trait attribute to this object.

        Parameters
        ----------
        name : str
            Name of the attribute to add.
        *trait :
            Trait or a value that can be converted to a trait by Trait().
            Trait definition for *name*. If more than one value is specified,
            it is equivalent to passing the entire list of values to Trait().

        """

        # Make sure a trait argument was specified:
        if len(trait) == 0:
            raise ValueError("No trait definition was specified.")

        # Make sure only valid traits get added:
        if len(trait) > 1:
            trait = Trait(*trait)
        else:
            trait = trait_for(trait[0])

        # Check to see if the trait has additional sub-traits that need to be
        # defined also:
        handler = trait.handler
        if handler is not None:
            if handler.has_items:
                self.add_trait(name + "_items", handler.items_event())
            if handler.is_mapped:
                self.add_trait(name + "_", mapped_trait_for(trait, name))

        # See if there already is a class or instance trait with the same name:
        old_trait = self._trait(name, 0)

        # Get the object's instance trait dictionary and add a clone of the new
        # trait to it:
        itrait_dict = self._instance_traits()
        itrait_dict[name] = trait = _clone_trait(trait)

        # If there already was a trait with the same name:
        if old_trait is not None:
            # Copy the old traits notifiers into the new trait:
            old_notifiers = old_trait._notifiers(False)
            if old_notifiers is not None:
                trait._notifiers(True).extend(old_notifiers)
        else:
            # Otherwise, see if there are any static notifiers that should be
            # applied to the trait:
            cls = self.__class__
            handlers = [
                _get_method(cls, "_%s_changed" % name),
                _get_method(cls, "_%s_fired" % name),
            ]

            # Add any special trait defined event handlers:
            _add_event_handlers(trait, cls, handlers)

            # Add the 'anytrait' handler (if any):
            handlers.append(self.__prefix_traits__.get("@"))

            # Filter out any 'None' values:
            handlers = [h for h in handlers if h is not None]

            # If there are any static notifiers, attach them to the trait:
            if len(handlers) > 0:
                _add_notifiers(trait._notifiers(True), handlers)

        # If this was a new trait, fire the 'trait_added' event:
        if old_trait is None:
            self.trait_added = name

    def remove_trait(self, name):
        """Removes a trait attribute from this object.

        Parameters
        ----------
        name : str
            Name of the attribute to remove.

        Returns
        -------
        result : bool
            True if the trait was successfully removed.
        """
        # Get the trait definition:
        trait = self._trait(name, 0)
        if trait is not None:

            # Check to see if the trait has additional sub-traits that need to
            # be removed also:
            handler = trait.handler
            if handler is not None:
                if handler.has_items:
                    self.remove_trait(name + "_items")
                if handler.is_mapped:
                    self.remove_trait(name + "_")

            # Remove the trait value from the object dictionary as well:
            if name in self.__dict__:
                del self.__dict__[name]

            # Get the object's instance trait dictionary and remove the trait
            # from it:
            itrait_dict = self._instance_traits()
            if name in itrait_dict:
                del itrait_dict[name]
                return True

        return False

    def trait(self, name, force=False, copy=False):
        """Returns the trait definition for the *name* trait attribute.

        If *force* is False (the default) and *name* is the name of an
        implicitly defined trait attribute that has never been referenced
        explicitly (i.e., has not yet been defined), the result is None. In
        all other cases, the result is the trait definition object associated
        with *name*.

        If *copy* is True, and a valid trait definition is found for *name*,
        a copy of the trait found is returned. In all other cases, the trait
        definition found is returned unmodified (the default).

        Parameters
        ----------
        name : str
            Name of the attribute whose trait definition is to be returned.
        force : bool
            Indicates whether to return a trait definition if *name* is
            not explicitly defined.
        copy : bool
            Indicates whether to return the original trait definition or a
            copy.
        """
        mode = 0
        if force:
            mode = -1
        result = self._trait(name, mode)
        if (not copy) or (result is None):
            return result

        return _clone_trait(result)

    def base_trait(self, name):
        """Returns the base trait definition for a trait attribute.

        This method is similar to the trait() method, and returns a
        different result only in the case where the trait attribute defined by
        *name* is a delegate. In this case, the base_trait() method follows the
        delegation chain until a non-delegated trait attribute is reached, and
        returns the definition of that attribute's trait as the result.

        Parameters
        ----------
        name : str
            Name of the attribute whose trait definition is returned.
        """
        return self._trait(name, -2)

    def validate_trait(self, name, value):
        """ Validates whether a value is legal for a trait.

        Returns the validated value if it is valid.
        """
        return self.base_trait(name).validate(self, name, value)

    def traits(self, **metadata):
        """Returns a dictionary containing the definitions of all of the trait
        attributes of this object that match the set of *metadata* criteria.
        Note that any traits with a name containing the suffix "_items" are
        always excluded.

        The keys of the returned dictionary are the trait attribute names, and
        the values are their corresponding trait definition objects.

        If no *metadata* information is specified, then all explicitly defined
        trait attributes defined for the object are returned.

        Otherwise, the *metadata* keyword dictionary is assumed to define a set
        of search criteria for selecting trait attributes of interest. The
        *metadata* dictionary keys correspond to the names of trait metadata
        attributes to examine, and the values correspond to the values the
        metadata attribute must have in order to be included in the search
        results.

        The *metadata* values either may be simple Python values like strings
        or integers, or may be lambda expressions or functions that return True
        if the trait attribute is to be included in the result. A lambda
        expression or function must receive a single argument, which is the
        value of the trait metadata attribute being tested. If more than one
        metadata keyword is specified, a trait attribute must match the
        metadata values of all keywords to be included in the result.

        Parameters
        ----------
        **metadata :
            Criteria for selecting trait attributes.
        """
        traits = self.__base_traits__.copy()

        # Update with instance-defined traits.
        for name, trt in self._instance_traits().items():
            if name[-6:] != "_items":
                traits[name] = trt

        for name in self.__dict__.keys():
            if name not in traits:
                trait = self.trait(name)
                if trait is not None:
                    traits[name] = trait

        if len(metadata) == 0:
            return traits

        for meta_name, meta_eval in list(metadata.items()):
            if type(meta_eval) is not FunctionType:
                metadata[meta_name] = _SimpleTest(meta_eval)

        result = {}
        for name, trait in traits.items():
            for meta_name, meta_eval in metadata.items():
                if not meta_eval(getattr(trait, meta_name, None)):
                    break
            else:
                result[name] = trait

        return result

    @classmethod
    def class_traits(cls, **metadata):
        """Returns a dictionary containing the definitions of all of the trait
        attributes of the class that match the set of *metadata* criteria.

        The keys of the returned dictionary are the trait attribute names, and
        the values are their corresponding trait definition objects.

        If no *metadata* information is specified, then all explicitly defined
        trait attributes defined for the class are returned.

        Otherwise, the *metadata* keyword dictionary is assumed to define a set
        of search criteria for selecting trait attributes of interest. The
        *metadata* dictionary keys correspond to the names of trait metadata
        attributes to examine, and the values correspond to the values the
        metadata attribute must have in order to be included in the search
        results.

        The *metadata* values either may be simple Python values like strings
        or integers, or may be lambda expressions or functions that return
        **True** if the trait attribute is to be included in the result. A
        lambda expression or function must receive a single argument, which is
        the value of the trait metadata attribute being tested. If more than
        one metadata keyword is specified, a trait attribute must match the
        metadata values of all keywords to be included in the result.

        Parameters
        ----------
        **metadata :
            Criteria for selecting trait attributes.
        """
        if len(metadata) == 0:
            return cls.__base_traits__.copy()

        result = {}

        for meta_name, meta_eval in list(metadata.items()):
            if type(meta_eval) is not FunctionType:
                metadata[meta_name] = _SimpleTest(meta_eval)

        for name, trait in cls.__base_traits__.items():
            for meta_name, meta_eval in metadata.items():
                if not meta_eval(getattr(trait, meta_name, None)):
                    break
            else:
                result[name] = trait

        return result

    def trait_names(self, **metadata):
        """Returns a list of the names of all trait attributes whose
        definitions match the set of *metadata* criteria specified.

        This method is similar to the traits() method, but returns only the
        names of the matching trait attributes, not the trait definitions.

        Parameters
        ----------
        **metadata :
            Criteria for selecting trait attributes.
        """
        return list(self.traits(**metadata).keys())

    @classmethod
    def class_trait_names(cls, **metadata):
        """Returns a list of the names of all trait attributes whose
        definitions match the set of *metadata* criteria specified.

        This method is similar to the traits() method, but returns only the
        names of the matching trait attributes, not the trait definitions.

        Parameters
        ----------
        **metadata :
            Criteria for selecting trait attributes.
        """
        return list(cls.class_traits(**metadata).keys())

    def _set_traits_cache(self, name, value):
        """ Explicitly sets the value of a cached property.
        """
        cached = TraitsCache + name
        old_value = self.__dict__.get(cached, Undefined)
        self.__dict__[cached] = value
        if old_value != value:
            self.trait_property_changed(name, old_value, value)

    def _flush_traits_cache(self, name, value):
        """ Explicitly flushes the value of a cached property.
        """
        self.trait_property_changed(
            name, self.__dict__.pop(TraitsCache + name, Undefined)
        )

    def __prefix_trait__(self, name, is_set):
        """ Return the trait definition for a specified name when there is
        no explicit definition in the class.
        """
        # Check to see if the name is of the form '__xxx__':
        if (name[:2] == "__") and (name[-2:] == "__"):
            if name == "__class__":
                return generic_trait

            # If this is for purposes of performing a 'setattr', always map the
            # name to an 'Any' trait:
            if is_set:
                return any_trait

            # Otherwise, it is a 'getattr' request, so indicate that no such
            # attribute exists:
            raise AttributeError(
                "'%s' object has no attribute '%s'"
                % (self.__class__.__name__, name)
            )

        # Handle the special case of 'delegated' traits:
        if name[-1:] == "_":
            trait = self._trait(name[:-1], 0)
            if (trait is not None) and (trait.type == "delegate"):
                return _clone_trait(trait)

        prefix_traits = self.__prefix_traits__
        for prefix in prefix_traits["*"]:
            if prefix == name[: len(prefix)]:
                # If we found a match, use its trait as a template for a new
                # trait:
                trait = prefix_traits[prefix]

                # Get any change notifiers that apply to the trait:
                cls = self.__class__
                handlers = [
                    _get_method(cls, "_%s_changed" % name),
                    _get_method(cls, "_%s_fired" % name),
                ]

                # Add any special trait defined event handlers:
                _add_event_handlers(trait, cls, handlers)

                # Add the 'anytrait' handler (if any):
                handlers.append(prefix_traits.get("@"))

                # Filter out any 'None' values:
                handlers = [h for h in handlers if h is not None]

                # If there are any handlers, add them to the trait's notifier's
                # list:
                if len(handlers) > 0:
                    trait = _clone_trait(trait)
                    _add_notifiers(trait._notifiers(True), handlers)

                return trait

        # There should ALWAYS be a prefix match in the trait classes, since ''
        # is at the end of the list, so we should never get here:
        raise SystemError(
            "Trait class look-up failed for attribute '%s' "
            "for an object of type '%s'" % (name, self.__class__.__name__)
        )

    def add_trait_listener(self, object, prefix=""):
        """ Add (Java-style) event listener to an object. """
        self._trait_listener(object, prefix, False)

    def remove_trait_listener(self, object, prefix=""):
        """ Remove (Java-style) event listener to an object. """
        self._trait_listener(object, prefix, True)

    def _trait_listener(self, object, prefix, remove):
        if prefix[-1:] != "_":
            prefix += "_"
        n = len(prefix)
        traits = self.__base_traits__
        for name in self._each_trait_method(object):
            if name[:n] == prefix:
                if name[-8:] == "_changed":
                    short_name = name[n:-8]
                    if short_name in traits:
                        self._on_trait_change(
                            getattr(object, name), short_name, remove=remove
                        )
                    elif short_name == "anytrait":
                        self._on_trait_change(
                            getattr(object, name), remove=remove
                        )
                elif name[:-6] == "_fired":
                    short_name = name[n:-6]
                    if short_name in traits:
                        self._on_trait_change(
                            getattr(object, name), short_name, remove=remove
                        )
                    elif short_name == "anytrait":
                        self._on_trait_change(
                            getattr(object, name), remove=remove
                        )

    def _each_trait_method(self, object):
        """ Generates each (name, method) pair for a specified object.
        """
        dic = {}
        for klass in object.__class__.__mro__:
            for name, method in klass.__dict__.items():
                if (is_unbound_method_type(method) and name not in dic):
                    dic[name] = True
                    yield name

    def _instance_changed_handler(self, name, old, new):
        """ Handles adding/removing listeners for a generic 'Instance' trait.
        """
        arg_lists = self._get_instance_handlers(name)

        if old is not None:
            for args in arg_lists:
                old.on_trait_change(remove=True, *args)

        if new is not None:
            for args in arg_lists:
                new.on_trait_change(*args)

    def _list_changed_handler(self, name, old, new):
        """ Handles adding/removing listeners for a generic 'List(Instance)'
            trait.
        """
        arg_lists = self._get_instance_handlers(name)

        for item in old:
            for args in arg_lists:
                item.on_trait_change(remove=True, *args)

        for item in new:
            for args in arg_lists:
                item.on_trait_change(*args)

    def _list_items_changed_handler(self, name, not_used, event):
        """ Handles adding/removing listeners for a generic 'List(Instance)'
            trait.
        """
        arg_lists = self._get_instance_handlers(name[:-6])

        for item in event.removed:
            for args in arg_lists:
                item.on_trait_change(remove=True, *args)

        for item in event.added:
            for args in arg_lists:
                item.on_trait_change(*args)

    def _get_instance_handlers(self, name):
        """ Returns a list of (name, method) pairs for a specified 'Instance'
            or 'List(Instance)' trait name:
        """
        return [
            (getattr(self, method_name), item_name)
            for method_name, item_name in self.__class__.__instance_traits__[
                name
            ]
        ]

    def _post_init_trait_listeners(self):
        """ Initializes the object's statically parsed, but dynamically
            registered, traits listeners (called at object creation and
            unpickling times).
        """
        for name, data in self.__class__.__listener_traits__.items():
            if data[0] == "method":
                config = data[1]
                if config["post_init"]:
                    self.on_trait_change(
                        getattr(self, name),
                        config["pattern"],
                        deferred=True,
                        dispatch=config["dispatch"],
                    )

    def _init_trait_listeners(self):
        """ Initializes the object's statically parsed, but dynamically
            registered, traits listeners (called at object creation and
            unpickling times).
        """
        for name, data in self.__class__.__listener_traits__.items():
            getattr(self, "_init_trait_%s_listener" % data[0])(name, *data)

    def _init_trait_method_listener(self, name, kind, config):
        """ Sets up the listener for a method with the @on_trait_change
            decorator.
        """
        if not config["post_init"]:
            self.on_trait_change(
                getattr(self, name),
                config["pattern"],
                deferred=True,
                dispatch=config["dispatch"],
            )

    def _init_trait_event_listener(self, name, kind, pattern):
        """ Sets up the listener for an event with on_trait_change metadata.
        """

        @weak_arg(self)
        def notify(self):
            setattr(self, name, True)

        self.on_trait_change(notify, pattern, target=self)

    def _init_trait_property_listener(self, name, kind, cached, pattern):
        """ Sets up the listener for a property with 'depends_on' metadata.
        """
        if cached is None:

            @weak_arg(self)
            def notify(self):
                self.trait_property_changed(name, None)

        else:
            cached_old = cached + ":old"

            @weak_arg(self)
            def pre_notify(self):
                dict = self.__dict__
                old = dict.get(cached_old, Undefined)
                if old is Undefined:
                    dict[cached_old] = dict.pop(cached, None)

            self.on_trait_change(
                pre_notify, pattern, priority=True, target=self
            )

            @weak_arg(self)
            def notify(self):
                old = self.__dict__.pop(cached_old, Undefined)
                if old is not Undefined:
                    self.trait_property_changed(name, old)

        self.on_trait_change(notify, pattern, target=self)

    def _init_trait_delegate_listener(self, name, kind, pattern):
        """ Sets up the listener for a delegate trait.
        """
        name_pattern = self._trait_delegate_name(name, pattern)
        target_name_len = len(name_pattern.split(":")[-1])

        @weak_arg(self)
        def notify(self, object, notify_name, old, new):
            self.trait_property_changed(
                name + notify_name[target_name_len:], old, new
            )

        self.on_trait_change(notify, name_pattern, target=self)
        self.__dict__.setdefault(ListenerTraits, {})[name] = notify

    def _remove_trait_delegate_listener(self, name, remove):
        """ Removes a delegate listener when the local delegate value is set.
        """
        dict = self.__dict__.setdefault(ListenerTraits, {})

        if remove:
            # Although the name should be in the dict, it may not be if a value
            # was assigned to a delegate in a constructor or setstate:
            if name in dict:
                # Remove the delegate listener:
                self.on_trait_change(
                    dict[name],
                    self._trait_delegate_name(
                        name, self.__class__.__listener_traits__[name][1]
                    ),
                    remove=True,
                )
                del dict[name]
                if len(dict) == 0:
                    del self.__dict__[ListenerTraits]

            return

        # Otherwise the local copy of the delegate value was deleted, restore
        # the delegate listener (unless it's already there):
        if name not in dict:
            self._init_trait_delegate_listener(
                name, 0, self.__class__.__listener_traits__[name][1]
            )

    def _init_trait_observers(self):
        """ Initialize observers prior to setting object state.
        """
        for name, states in self.__class__.__observer_traits__.items():
            for state in states:
                if not state["post_init"]:
                    observe_api.apply_observers(
                        object=self,
                        handler=state["handler_getter"](self, name),
                        graphs=state["graphs"],
                        dispatcher=_ObserverDispatchers[state["dispatch"]],
                    )

    def _post_init_trait_observers(self):
        """ Initialize observers after setting object state.
        """
        for name, states in self.__class__.__observer_traits__.items():
            for state in states:
                if state["post_init"]:
                    observe_api.apply_observers(
                        object=self,
                        handler=state["handler_getter"](self, name),
                        graphs=state["graphs"],
                        dispatcher=_ObserverDispatchers[state["dispatch"]],
                    )

    def _trait_delegate_name(self, name, pattern):
        """ Returns the fully-formed 'on_trait_change' name for a specified
            delegate.
        """
        if pattern[-1] == "*":
            pattern = "%s%s%s" % (
                pattern[:-1],
                self.__class__.__prefix__,
                name,
            )

        return pattern


# Patch the definition of _HasTraits to be the real 'HasTraits':
_HasTraits = HasTraits


class HasStrictTraits(HasTraits):
    """ This class guarantees that any object attribute that does not have an
    explicit or wildcard trait definition results in an exception.

    This feature can be useful in cases where a more rigorous software
    engineering approach is being used than is typical for Python programs. It
    also helps prevent typos and spelling mistakes in attribute names from
    going unnoticed; a misspelled attribute name typically causes an exception.
    """

    _ = Disallow  # Disallow access to any traits not explicitly defined


class HasRequiredTraits(HasStrictTraits):
    """ This class builds on the functionality of HasStrictTraits and ensures
    that any object attribute with `required=True` in its metadata must be
    passed as an argument on object initialization.

    This can be useful in cases where an object has traits which are required
    for it to function correctly.

    Raises
    ------
    TraitError
        If a required trait is not passed as an argument.

    Examples
    --------
    A class with required traits:

    >>> class RequiredTest(HasRequiredTraits):
    ...     required_trait = Any(required=True)
    ...     non_required_trait = Any()

    Creating an instance of a HasRequiredTraits subclass:

    >>> test_instance = RequiredTest(required_trait=13, non_required_trait=11)
    >>> test_instance2 = RequiredTest(required_trait=13)

    Forgetting to specify a required trait:

    >>> test_instance = RequiredTest(non_required_trait=11)
    traits.trait_errors.TraitError: The following required traits were not
    provided: required_trait.
    """

    def __init__(self, **traits):

        missing_required_traits = [
            name
            for name in self.trait_names(required=True)
            if name not in traits
        ]
        if missing_required_traits:
            raise TraitError(
                "The following required traits were not provided: "
                "{}.".format(", ".join(sorted(missing_required_traits)))
            )

        super().__init__(**traits)


class HasPrivateTraits(HasTraits):
    """ This class ensures that any public object attribute that does not have
    an explicit or wildcard trait definition results in an exception, but
    "private" attributes (whose names start with '_') have an initial value of
    **None**, and are not type-checked.

    This feature is useful in cases where a class needs private attributes to
    keep track of its internal object state, which are not part of the class's
    public API. Such attributes do not need to be type-checked, because they
    are manipulated only by the (presumably correct) methods of the class
    itself.
    """

    # Make 'private' traits (leading '_') have no type checking:
    __ = Any(private=True, transient=True)

    # Disallow access to all other traits not explicitly defined:
    _ = Disallow


# ABC classes with traits

class ABCMetaHasTraits(abc.ABCMeta, MetaHasTraits):
    """ A MetaHasTraits subclass which also inherits from
    abc.ABCMeta.

    .. note:: The ABCMeta class is cooperative and behaves nicely
        with MetaHasTraits, provided it is inherited first.
    """

    pass


class ABCHasTraits(HasTraits, metaclass=ABCMetaHasTraits):
    """ A HasTraits subclass which enables the features of Abstract
    Base Classes (ABC). See the 'abc' module in the standard library
    for more information.

    """


class ABCHasStrictTraits(ABCHasTraits):
    """ A HasTraits subclass which behaves like HasStrictTraits but
    also enables the features of Abstract Base Classes (ABC). See the
    'abc' module in the standard library for more information.

    """

    _ = Disallow


class Vetoable(HasStrictTraits):
    """ Defines a 'vetoable' request object and an associated event.
    """

    # Should the request be vetoed? (Can only be set to 'True')
    veto = Bool(False)

    def _veto_changed(self, state):
        self._trait_veto_notify(state)


VetoableEvent = Event(Vetoable)


class MetaInterface(ABCMetaHasTraits):
    """ Meta class for interfaces.

    Historically, there were some differences between interfaces
    and ABCs in Traits, but now Interface is a near synonym for
    ABCHasTraits.
    """


class Interface(HasTraits, metaclass=MetaInterface):
    """ The base class for all interfaces.
    """


def provides(*protocols):
    """ Class decorator to declare the protocols that a class provides.

    Parameters
    ----------
    *protocols :
        A list of protocols (Interface classes or Python ABCs) that the
        decorated class provides.

    """

    from abc import ABCMeta

    # Exit immediately if there is nothing to do.
    if len(protocols) == 0:
        return lambda klass: klass

    # Verify that each argument is a valid protocol.
    for protocol in protocols:
        if not issubclass(type(protocol), ABCMeta):
            raise TraitError(
                "All arguments to 'provides' must be "
                "subclasses of Interface or be a Python ABC."
            )

    def wrapped_class(klass):
        for protocol in protocols:
            # We use 'type(protocol)' in case the 'protocol' implements
            # its own 'register' method that overrides the ABC method.
            type(protocol).register(protocol, klass)

        # Make sure the class does provide the protocols it claims to.
        if CHECK_INTERFACES:
            from .interface_checker import check_implements

            warnings.warn(
                (
                    "In the future, the @provides decorator will not perform "
                    "interface checks. Set has_traits.CHECK_INTERFACES to 0 "
                    "to suppress this warning."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            check_implements(klass, protocols, CHECK_INTERFACES)

        return klass

    return wrapped_class


def isinterface(klass):
    """ Return True if the class is an Interface. """

    return isinstance(klass, MetaInterface)


class ISerializable(Interface):
    """ A class that implemented ISerializable requires that all HasTraits
        objects saved as part of its state also implement ISerializable.
    """
