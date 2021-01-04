# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Defines the 'core' traits for the Traits package. A trait is a type definition
that can be used for normal Python object attributes, giving the attributes
some additional characteristics:

Initialization:
    Traits have predefined values that do not need to be explicitly
    initialized in the class constructor or elsewhere.
Validation:
    Trait attributes have flexible, type-checked values.
Delegation:
    Trait attributes' values can be delegated to other objects.
Notification:
    Trait attributes can automatically notify interested parties when
    their values change.
Visualization:
    Trait attributes can automatically construct (automatic or
    programmer-defined) user interfaces that allow their values to be
    edited or displayed)

.. note:: 'trait' is a synonym for 'property', but is used instead of the
    word 'property' to differentiate it from the Python language 'property'
    feature.
"""

from types import FunctionType, MethodType
import warnings

from .constants import (
    ComparisonMode,
    DefaultValue,
    TraitKind,
)
from .ctrait import CTrait
from .trait_errors import TraitError
from .trait_base import (
    SequenceTypes,
    TypeTypes,
    add_article,
)
from .trait_converters import (
    trait_cast,
    check_trait as try_trait_cast,
)

from .trait_handler import TraitHandler
from .trait_type import (
    _infer_default_value_type,
    _read_only,
    _write_only,
)
from .trait_handlers import (
    TraitInstance,
    TraitFunction,
    TraitCoerceType,
    TraitCastType,
    TraitEnum,
    TraitCompound,
    TraitMap,
    _undefined_get,
    _undefined_set,
)
from .trait_factory import (
    TraitFactory,
)
from .util.deprecated import deprecated

# Constants

NoneType = type(None)  # Python 3's types does not include NoneType

ConstantTypes = (NoneType, int, float, complex, str)

PythonTypes = (
    str,
    int,
    float,
    complex,
    list,
    tuple,
    dict,
    FunctionType,
    MethodType,
    type,
    NoneType,
)

CallableTypes = (FunctionType, MethodType)

TraitTypes = (TraitHandler, CTrait)

DefaultValues = {
    str: "",
    int: 0,
    float: 0.0,
    complex: 0j,
    list: [],
    tuple: (),
    dict: {},
    bool: False,
}


# This function is needed when unpickling historical pickles (pickles
# created on versions of Traits prior to 6.0). It can be removed when
# there's no longer any need to support pickles generated on older
# versions of Traits.

def __newobj__(cls, *args):
    """ Unpickles new-style objects.
    """
    return cls.__new__(cls, *args)


# --- 'instance' traits -------------------------------------------------------


class _InstanceArgs(object):
    def __init__(self, factory, args, kw):
        self.args = (factory,) + args
        self.kw = kw


# --- 'creates a run-time default value' --------------------------------------


class Default(object):
    """ Generates a value the first time it is accessed.

    A Default object can be used anywhere a default trait value would normally
    be specified, to generate a default value dynamically.
    """

    def __init__(self, func=None, args=(), kw=None):
        self.default_value = (func, args, kw)


def Trait(*value_type, **metadata):
    """ Creates a trait definition.

    This function accepts a variety of forms of parameter lists:

    +-------------------+---------------+-------------------------------------+
    | Format            | Example       | Description                         |
    +===================+===============+=====================================+
    | Trait(*default*)  | Trait(150.0)  | The type of the trait is inferred   |
    |                   |               | from the type of the default value, |
    |                   |               | which must be in *ConstantTypes*.   |
    +-------------------+---------------+-------------------------------------+
    | Trait(*default*,  | Trait(None,   | The trait accepts any of the        |
    | *other1*,         | 0, 1, 2,      | enumerated values, with the first   |
    | *other2*, ...)    | 'many')       | value being the default value. The  |
    |                   |               | values must be of types in          |
    |                   |               | *ConstantTypes*, but they need not  |
    |                   |               | be of the same type. The *default*  |
    |                   |               | value is not valid for assignment   |
    |                   |               | unless it is repeated later in the  |
    |                   |               | list.                               |
    +-------------------+---------------+-------------------------------------+
    | Trait([*default*, | Trait([None,  | Similar to the previous format, but |
    | *other1*,         | 0, 1, 2,      | takes an explicit list or a list    |
    | *other2*, ...])   | 'many'])      | variable.                           |
    +-------------------+---------------+-------------------------------------+
    | Trait(*type*)     | Trait(Int)    | The *type* parameter must be a name |
    |                   |               | of a Python type (see               |
    |                   |               | *PythonTypes*). Assigned values     |
    |                   |               | must be of exactly the specified    |
    |                   |               | type; no casting or coercion is     |
    |                   |               | performed. The default value is the |
    |                   |               | appropriate form of zero, False,    |
    |                   |               | or emtpy string, set or sequence.   |
    +-------------------+---------------+-------------------------------------+
    | Trait(*class*)    |::             | Values must be instances of *class* |
    |                   |               | or of a subclass of *class*. The    |
    |                   | class MyClass:| default value is None, but None     |
    |                   |    pass       | cannot be assigned as a value.      |
    |                   | foo = Trait(  |                                     |
    |                   | MyClass)      |                                     |
    +-------------------+---------------+-------------------------------------+
    | Trait(None,       |::             | Similar to the previous format, but |
    | *class*)          |               | None *can* be assigned as a value.  |
    |                   | class MyClass:|                                     |
    |                   |   pass        |                                     |
    |                   | foo = Trait(  |                                     |
    |                   | None, MyClass)|                                     |
    +-------------------+---------------+-------------------------------------+
    | Trait(*instance*) |::             | Values must be instances of the     |
    |                   |               | same class as *instance*, or of a   |
    |                   | class MyClass:| subclass of that class. The         |
    |                   |    pass       | specified instance is the default   |
    |                   | i = MyClass() | value.                              |
    |                   | foo =         |                                     |
    |                   |   Trait(i)    |                                     |
    +-------------------+---------------+-------------------------------------+
    | Trait(*handler*)  | Trait(        | Assignment to this trait is         |
    |                   | TraitEnum )   | validated by an object derived from |
    |                   |               | **traits.TraitHandler**.            |
    +-------------------+---------------+-------------------------------------+
    | Trait(*default*,  | Trait(0.0, 0.0| This is the most general form of    |
    | { *type* |        | 'stuff',      | the function. The notation:         |
    | *constant* |      | TupleType)    | ``{...|...|...}+`` means a list of  |
    | *dict* | *class* ||               | one or more of any of the items     |
    | *function* |      |               | listed between the braces. Thus, the|
    | *handler* |       |               | most general form of the function   |
    | *trait* }+ )      |               | consists of a default value,        |
    |                   |               | followed by one or more of several  |
    |                   |               | possible items. A trait defined by  |
    |                   |               | multiple items is called a          |
    |                   |               | "compound" trait.                   |
    +-------------------+---------------+-------------------------------------+

    All forms of the Trait function accept both predefined and arbitrary
    keyword arguments. The value of each keyword argument becomes bound to the
    resulting trait object as the value of an attribute having the same name
    as the keyword. This feature lets you associate metadata with a trait.

    The following predefined keywords are accepted:

    desc : str
        Describes the intended meaning of the trait. It is used in
        exception messages and fly-over help in user interfaces.
    label : str
        Provides a human-readable name for the trait. It is used to label user
        interface editors for traits.
    editor : traits.api.Editor
        Instance of a subclass Editor object to use when creating a user
        interface editor for the trait. See the "Traits UI User Guide" for
        more information on trait editors.
    comparison_mode : int
        Indicates when trait change notifications should be generated based
        upon the result of comparing the old and new values of a trait
        assignment. Possible values come from the ``ComparisonMode`` enum:

        * 0 (none): The values are not compared and a trait change
          notification is generated on each assignment.
        * 1 (identity): A trait change notification is
          generated if the old and new values are not the same object.
        * 2 (equality): A trait change notification is generated if the
          old and new values are not equal using Python's standard equality
          testing. This is the default.

    """
    return _TraitMaker(*value_type, **metadata).as_ctrait()


class _TraitMaker(object):

    # Ctrait type map for special trait types:
    type_map = {"event": TraitKind.event, "constant": TraitKind.constant}

    def __init__(self, *value_type, **metadata):
        metadata.setdefault("type", "trait")
        self.define(*value_type, **metadata)

    def define(self, *value_type, **metadata):
        """ Define the trait. """
        default_value_type = DefaultValue.unspecified
        default_value = handler = clone = None

        if len(value_type) > 0:
            default_value = value_type[0]
            value_type = value_type[1:]

            if (len(value_type) == 0) and (
                type(default_value) in SequenceTypes
            ):
                default_value, value_type = default_value[0], default_value

            if len(value_type) == 0:
                default_value = try_trait_cast(default_value)

                if default_value in PythonTypes:
                    handler = TraitCoerceType(default_value)
                    default_value = DefaultValues.get(default_value)

                elif isinstance(default_value, CTrait):
                    clone = default_value
                    default_value_type, default_value = clone.default_value()
                    metadata["type"] = clone.type

                elif isinstance(default_value, TraitHandler):
                    handler = default_value
                    default_value = None

                else:
                    typeValue = type(default_value)
                    if typeValue in TypeTypes:
                        handler = TraitCastType(typeValue)

                    else:
                        metadata.setdefault(
                            "instance_handler", "_instance_changed_handler"
                        )
                        handler = TraitInstance(default_value)
                        if default_value is handler.aClass:
                            default_value = DefaultValues.get(default_value)
            else:
                enum = []
                other = []
                map = {}
                self.do_list(value_type, enum, map, other)

                if ((len(enum) == 1) and (enum[0] is None)) and (
                    (len(other) == 1) and isinstance(other[0], TraitInstance)
                ):
                    enum = []
                    other[0].allow_none()
                    metadata.setdefault(
                        "instance_handler", "_instance_changed_handler"
                    )
                if len(enum) > 0:
                    if ((len(map) + len(other)) == 0) and (
                        default_value not in enum
                    ):
                        enum.insert(0, default_value)

                    other.append(TraitEnum(enum))

                if len(map) > 0:
                    other.append(TraitMap(map))

                if len(other) == 0:
                    handler = TraitHandler()

                elif len(other) == 1:
                    handler = other[0]
                    if isinstance(handler, CTrait):
                        clone, handler = handler, None
                        metadata["type"] = clone.type

                    elif isinstance(handler, TraitInstance):
                        metadata.setdefault(
                            "instance_handler", "_instance_changed_handler"
                        )

                        if default_value is None:
                            handler.allow_none()

                        elif isinstance(default_value, _InstanceArgs):
                            default_value_type = (
                                DefaultValue.callable_and_args
                            )
                            default_value = (
                                handler.create_default_value,
                                default_value.args,
                                default_value.kw,
                            )

                        elif (len(enum) == 0) and (len(map) == 0):
                            aClass = handler.aClass
                            typeValue = type(default_value)

                            if typeValue is dict:
                                default_value_type = (
                                    DefaultValue.callable_and_args
                                )
                                default_value = (aClass, (), default_value)
                            elif not isinstance(default_value, aClass):
                                if typeValue is not tuple:
                                    default_value = (default_value,)
                                default_value_type = (
                                    DefaultValue.callable_and_args
                                )
                                default_value = (aClass, default_value, None)
                else:
                    for i, item in enumerate(other):
                        if isinstance(item, CTrait):
                            if item.type != "trait":
                                raise TraitError(
                                    "Cannot create a complex "
                                    "trait containing %s trait."
                                    % add_article(item.type)
                                )
                            handler = item.handler
                            if handler is None:
                                break
                            other[i] = handler
                    else:
                        handler = TraitCompound(other)

        # Save the results:
        self.handler = handler
        self.clone = clone

        if default_value_type < 0:
            if isinstance(default_value, Default):
                default_value_type = DefaultValue.callable_and_args
                default_value = default_value.default_value
            else:
                if (handler is None) and (clone is not None):
                    handler = clone.handler

                if handler is not None:
                    default_value_type = handler.default_value_type
                    if default_value_type < 0:
                        try:
                            default_value = handler.validate(
                                None, "", default_value
                            )
                        except:
                            pass

                if default_value_type < 0:
                    default_value_type = _infer_default_value_type(
                        default_value
                    )

        self.default_value_type = default_value_type
        self.default_value = default_value
        self.metadata = metadata.copy()

    def do_list(self, list, enum, map, other):
        """ Determine the correct TraitHandler for each item in a list. """
        for item in list:
            if item in PythonTypes:
                other.append(TraitCoerceType(item))
            else:
                item = try_trait_cast(item)
                typeItem = type(item)

                if typeItem in ConstantTypes:
                    enum.append(item)

                elif typeItem in SequenceTypes:
                    self.do_list(item, enum, map, other)

                elif typeItem is dict:
                    map.update(item)

                elif typeItem in CallableTypes:
                    other.append(TraitFunction(item))

                elif isinstance(item, TraitTypes):
                    other.append(item)

                else:
                    other.append(TraitInstance(item))

    def as_ctrait(self):
        """ Return a properly initialized 'CTrait' instance. """
        metadata = self.metadata
        trait = CTrait(
            self.type_map.get(metadata.get("type"), TraitKind.trait))
        clone = self.clone
        if clone is not None:
            trait.clone(clone)
            if clone.__dict__ is not None:
                trait.__dict__ = clone.__dict__.copy()

        trait.set_default_value(self.default_value_type, self.default_value)

        handler = self.handler
        if handler is not None:
            trait.handler = handler
            validate = getattr(handler, "fast_validate", None)
            if validate is None:
                validate = handler.validate
            trait.set_validate(validate)

            post_setattr = getattr(handler, "post_setattr", None)
            if post_setattr is not None:
                trait.post_setattr = post_setattr
                trait.is_mapped = handler.is_mapped

        rich_compare = metadata.get("rich_compare")
        if rich_compare is not None:
            # Ref: enthought/traits#602
            warnings.warn(
                "The 'rich_compare' metadata has been deprecated. Please "
                "use the 'comparison_mode' metadata instead. In a future "
                "release, rich_compare will have no effect.",
                DeprecationWarning,
                stacklevel=4,
            )
            if rich_compare:
                trait.comparison_mode = ComparisonMode.equality
            else:
                trait.comparison_mode = ComparisonMode.identity

        comparison_mode = metadata.pop("comparison_mode", None)
        if comparison_mode is not None:
            trait.comparison_mode = comparison_mode

        if len(metadata) > 0:
            if trait.__dict__ is None:
                trait.__dict__ = metadata
            else:
                trait.__dict__.update(metadata)

        return trait


def Property(
    fget=None,
    fset=None,
    fvalidate=None,
    force=False,
    handler=None,
    trait=None,
    **metadata
):
    """ Returns a trait whose value is a Python property.

    If no getter, setter or validate functions are specified (and **force** is
    not True), it is assumed that they are defined elsewhere on the class whose
    attribute this trait is assigned to. For example::

        class Bar(HasTraits):

            # A float traits Property that should be always positive.
            foo = Property(Float)

            # Shadow trait attribute
            _foo = Float

            def _set_foo(self,x):
                self._foo = x

            def _validate_foo(self, x):
                if x <= 0:
                    raise TraitError(
                        'foo property should be a positive number')
                return x

            def _get_foo(self):
                return self._foo

    You can use the **observe** metadata attribute to indicate that the
    property depends on the value of another trait. The value of **observe**
    follows the same signature as the **expression** parameter in
    ``HasTraits.observe``. The property will fire a trait change notification
    if any of the traits specified by **observe** change. For example::

        class Wheel(Part):
            axle = Instance(Axle)
            position = Property(observe='axle.chassis.position')

    For details of the extended trait name syntax, refer to the
    observe() method of the HasTraits class.

    Parameters
    ----------
    fget : function
        The "getter" function for the property.
    fset : function
        The "setter" function for the property.
    fvalidate : function
        The validation function for the property. The method should return the
        value to set or raise TraitError if the new value is not valid.
    force : bool
        Indicates whether to use only the function definitions specified by
        **fget** and **fset**, and not look elsewhere on the class.
    handler : function
        A trait handler function for the trait.
    trait : Trait or value
        A trait definition or a value that can be converted to a trait that
        constrains the values of the property trait.
    """
    metadata["type"] = "property"

    # If no parameters specified, must be a forward reference (if not forced):
    if (not force) and (fset is None):
        sum = (
            (fget is not None) + (fvalidate is not None) + (trait is not None)
        )
        if sum <= 1:
            if sum == 0:
                return ForwardProperty(metadata)

            handler = None
            if fget is not None:
                trait = fget

            if trait is not None:
                trait = trait_cast(trait)
                if trait is not None:
                    fvalidate = handler = trait.handler
                    if fvalidate is not None:
                        fvalidate = handler.validate

            if (fvalidate is not None) or (trait is not None):
                if "editor" not in metadata:
                    if (trait is not None) and (trait.editor is not None):
                        metadata["editor"] = trait.editor

                return ForwardProperty(metadata, fvalidate, handler)

    if fget is None:
        metadata["transient"] = True
        if fset is None:
            fget = _undefined_get
            fset = _undefined_set
        else:
            fget = _write_only

    elif fset is None:
        fset = _read_only
        metadata["transient"] = True

    if trait is not None:
        trait = trait_cast(trait)
        handler = trait.handler
        if (fvalidate is None) and (handler is not None):
            fvalidate = handler.validate

        if ("editor" not in metadata) and (trait.editor is not None):
            metadata["editor"] = trait.editor

    metadata.setdefault("depends_on", getattr(fget, "depends_on", None))
    if getattr(fget, "cached_property", False):
        metadata.setdefault("cached", True)

    trait = CTrait(TraitKind.property)
    trait.__dict__ = metadata.copy()
    trait.property_fields = (fget, fset, fvalidate)
    trait.handler = handler

    return trait


Property = TraitFactory(Property)


class ForwardProperty(object):
    """ Used to implement Property traits where accessor functions are defined
    implicitly on the class.
    """

    def __init__(self, metadata, validate=None, handler=None):
        self.metadata = metadata.copy()
        self.validate = validate
        self.handler = handler


# Predefined, reusable trait instances

# Generic trait with 'object' behavior:
generic_trait = CTrait(TraitKind.generic)


# User interface related color and font traits

@deprecated("'Color' in 'traits' package has been deprecated. "
            "Use 'Color' from 'traitsui' package instead.")
def Color(*args, **metadata):
    """ Returns a trait whose value must be a GUI toolkit-specific color.

    .. deprecated:: 6.1.0
        ``Color`` trait in this package will be removed in the future. It is
        replaced by ``Color`` trait in TraitsUI package.
    """
    from traitsui.toolkit_traits import ColorTrait

    return ColorTrait(*args, **metadata)


Color = TraitFactory(Color)


@deprecated("'RGBColor' in 'traits' package has been deprecated. "
            "Use 'RGBColor' from 'traitsui' package instead.")
def RGBColor(*args, **metadata):
    """ Returns a trait whose value must be a GUI toolkit-specific RGB-based
    color.

    .. deprecated:: 6.1.0
        ``RGBColor`` trait in this package will be removed in the future. It is
        replaced by ``RGBColor`` trait in TraitsUI package.
    """
    from traitsui.toolkit_traits import RGBColorTrait

    return RGBColorTrait(*args, **metadata)


RGBColor = TraitFactory(RGBColor)


@deprecated("'Font' in 'traits' package has been deprecated. "
            "Use 'Font' from 'traitsui' package instead.")
def Font(*args, **metadata):
    """ Returns a trait whose value must be a GUI toolkit-specific font.

    .. deprecated:: 6.1.0
        ``Font`` trait in this package will be removed in the future. It is
        replaced by ``Font`` trait in TraitsUI package.
    """
    from traitsui.toolkit_traits import FontTrait

    return FontTrait(*args, **metadata)


Font = TraitFactory(Font)
