.. index:: custom traits

.. _custom-traits:

=============
Custom Traits
=============

The predefined traits such as those described in :ref:`predefined-traits` are
handy shortcuts for commonly used types. However, the Traits package also
provides facilities for defining complex or customized traits:

* Subclassing of traits
* The Trait() factory function
* Predefined or custom trait handlers

.. index:: subclassing traits, TraitType class

.. _trait-subclassing:

Trait Subclassing
-----------------

Starting with Traits version 3.0, most predefined traits are defined as
subclasses of traits.trait_handlers.TraitType. As a result, you can
subclass one of these traits, or TraitType, to derive new traits. Refer to the
*Traits API Reference* to see whether a particular predefined trait derives from
TraitType.

.. index::
   pair: subclassing traits; examples

Here's an example of subclassing a predefined trait class::

    # trait_subclass.py -- Example of subclassing a trait class
    from traits.api import BaseInt

    class OddInt ( BaseInt ):

        # Define the default value
        default_value = 1

        # Describe the trait type
        info_text = 'an odd integer'

        def validate ( self, object, name, value ):
            value = super().validate(object, name, value)
            if (value % 2) == 1:
                return value

            self.error( object, name, value )

The OddInt class defines a trait that must be an odd integer. It derives from
BaseInt, rather than Int, as you might initially expect. BaseInt and Int are
exactly the same, except that Int has a **fast_validate attribute**, which
causes it to quickly check types at the C level, not go through the expense of
executing the general validate() method. [6]_

As a subclass of BaseInt, OddInt can reuse and change any part of the BaseInt
class behavior that it needs to. In this case, it reuses the BaseInt class's
validate() method, via the call to super() in the OddInt validate() method.
Further, OddInt is related to BaseInt, which can be useful as documentation, and
in programming.

You can use the subclassing strategy to define either a trait type or a trait
property, depending on the specific methods and class constants that you define.
A trait type uses a validate() method, while a trait property uses get() and
set() methods.

The :class:`~.TraitType` initializer provides an optional argument
``default_value`` to support easy setting of the default value of the trait
type. The default value for that argument is :data:`~.NoDefaultSpecified`: we
don't follow the common Python idiom of using ``None`` to represent no default
here, since for many trait types ``None`` may be a valid default value. When
subclassing :class:`~.TraitType` and overriding or extending its ``__init__``
method, it's recommended to re-use the singleton :data:`~.NoDefaultSpecified`
if you need a way to indicate that no default value was specified.


.. index: trait type; defining

.. _defining-a-trait-type:

Defining a Trait Type
`````````````````````

The members that are specific to a trait type subclass are:

.. index:: default_value attribute, get_default_value()

* validate() method
* post_setattr() method
* **default_value** attribute or get_default_value() method

Of these, only the validate() method must be overridden in trait type
subclasses.

A trait type uses a validate() method to determine the validity of values
assigned to the trait. Optionally, it can define a post_setattr() method, which
performs additional processing after a value has been validated and assigned.

The signatures of these methods are:

.. method:: validate( object, name, value )
.. method:: post_setattr( object, name, value )

The parameters of these methods are:

.. index:: object parameter; validate(), name parameter; validate()
.. index:: value parameter; validate()

* *object*: The object whose trait attribute whose value is being assigned.
* *name*: The name of the trait attribute whose value is being assigned.
* *value*: The value being assigned.

The validate() method returns either the original value or any suitably coerced
or adapted value that is legal for the trait. If the value is not legal, and
cannot be coerced or adapted to be legal, the method must either raise a
TraitError, or calls the error() method to raise a TraitError on its behalf.

The subclass can define a default value either as a constant or as a computed
value. To use a constant, set the class-level **default_value attribute**. To
compute the default value, override the TraitType class's get_default_value()
method.

.. index:: trait property; defining

.. _defining-a-trait-property:

Defining a Trait Property
`````````````````````````

A trait property uses get() and set() methods to interact with the value of the
trait. If a TraitType subclass contains a get() method or a set() method, any
definition it might have for validate() is ignored.

The signatures of these methods are:

.. method:: get( object, name)
.. method:: set( object, name, value)

In these signatures, the parameters are:

* *object*: The object that the property applies to.
* *name*: The name of the trait property attribute on the object.
* *value*: The value being assigned to the property.

If only a get() method is defined, the property behaves as read-only. If only a
set() method is defined, the property behaves as write-only.

The get() method returns the value of the *name* property for the specified
object. The set() method does not return a value, but will raise a TraitError if
the specified *value* is not valid, and cannot be coerced or adapted to a valid
value.

In order for the property to trigger notifications you must call either:

* object.trait_property_changed(name, old, value) to not cache the value.
* self.set_value(object, name, value) to cache the value.

Likewise if the property will not be read only the get method must use
self.get_value(object, name) in order to behave correctly.

The following example demonstrates the use of a property trait to set temperature::

    class TempFloat(BaseFloat):
        default_value = 20.0
        info_text = 'A calculated temperature float in Celsius'

        def set(self, obj, name, value):
            celsius = (value - 32) * (5/9)
            setattr(self, name, celsius)
            self.set_value(obj, name, celsius)

        def get(self, obj, name):
            val = self.get_value(obj, name)
            if val is None:
                val = self.default_value
            return val

.. index:: TraitType class; members

.. _other-traittype-members:

Other TraitType Members
```````````````````````

The following members can be specified for either a trait type or a trait
property:

.. index:: info_text attribute, info(), init(), create_editor()

* **info_text** attribute or info() method
* init() method
* create_editor() method

A trait must have an information string that describes the values accepted by
the trait type (for example 'an odd integer'). Similarly to the default value,
the subclass's information string can be either a constant string or a computed
string. To use a constant, set the class-level info_text attribute. To compute
the info string, override the TraitType class's info() method, which takes no
parameters.

If there is type-specific initialization that must be performed when the trait
type is created, you can override the init() method. This method is
automatically called from the __init__() method of the TraitType class.

If you want to specify a default TraitsUI editor for the new trait type, you
can override the create_editor() method. This method has no parameters, and
returns the default trait editor to use for any instances of the type.

For complete details on the members that can be overridden, refer to the *Traits
API Reference* sections on the TraitType and BaseTraitHandler classes.

.. index:: Trait()

.. _the-trait-factory-function:

The Trait() Factory Function
----------------------------

The Trait() function is a generic factory for trait definitions. It has many
forms, many of which are redundant with the predefined shortcut traits. For
example, the simplest form Trait(default_value), is equivalent to the functions
for simple types described in :ref:`predefined-traits-for-simple-types`. For the
full variety of forms of the Trait() function, refer to the *Traits API
Reference*.

The most general form of the Trait() function is:

.. currentmodule:: traits.traits
.. function:: Trait(default_value, {type | constant_value | dictionary | class | function | trait_handler | trait }+ )
    :noindex:

.. index:: compound traits

The notation ``{ | | }+`` means a list of one or more of any of the items listed
between the braces. Thus, this form of the function consists of a default value,
followed by one or more of several possible items. A trait defined with multiple
items is called a compound trait. When more than one item is specified, a trait
value is considered valid if it meets the criteria of at least one of the items
in the list.

.. index::
   pair: Trait() function; examples

The following is an example of a compound trait with multiple criteria::

    # compound.py -- Example of multiple criteria in a trait definition
    from traits.api import HasTraits, Trait, Range

    class Die ( HasTraits ):

        # Define a compound trait definition:
        value = Trait( 1, Range( 1, 6 ),
                      'one', 'two', 'three', 'four', 'five', 'six' )

The Die class has a **value trait**, which has a default value of 1, and can have
any of the following values:

* An integer in the range of 1 to 6
* One of the following strings: 'one', 'two', 'three', 'four', 'five', 'six'

.. index:: Trait(); parameters

.. _trait-parameters:

Trait () Parameters
```````````````````

The items listed as possible arguments to the Trait() function merit some
further explanation.

.. index:: type; parameter to Trait(), constant_value parameter to Trait()
.. index:: dictionary parameter to Trait(), class parameter to Trait()
.. index:: function parameter to Trait(), trait handler; parameter to Trait()
.. index:: trait; parameter to Trait()

* *type*: See :ref:`type`.
* *constant_value*: See :ref:`constant-value`.
* *dictionary*: See :ref:`mapped-traits`.
* *class*: Specifies that the trait value must be an instance of the specified
  class or one of its subclasses.
* *function*: A "validator" function that determines whether a value being
  assigned to the attribute is a legal value. Traits version 3.0 provides a
  more flexible approach, which is to subclass an existing trait (or TraitType)
  and override the validate() method.
* *trait_handler*: See :ref:`trait-handlers`.
* *trait*: Another trait object can be passed as a parameter; any value that is
  valid for the specified trait is also valid for the trait referencing it.

.. index:: type; parameter to Trait()

.. _type:

Type
::::

A *type* parameter to the Trait() function can be any of the following standard
Python types:

* str or StringType
* int or IntType
* float or FloatType
* complex or ComplexType
* bool or BooleanType
* list or ListType
* tuple or TupleType
* dict or DictType
* FunctionType
* MethodType
* type
* NoneType

Specifying one of these types means that the trait value must be of the
corresponding Python type.

.. index:: constant_value parameter to Trait()

.. _constant-value:

Constant Value
::::::::::::::

A *constant_value* parameter to the Trait() function can be any constant
belonging to one of the following standard Python types:

* NoneType
* int
* float
* complex
* bool
* str

Specifying a constant means that the trait can have the constant as a valid
value. Passing a list of constants to the Trait() function is equivalent to
using the Enum predefined trait.

.. index:: mapped traits

.. _mapped-traits:

Mapped Traits
`````````````

If the Trait() function is called with parameters that include one or more
dictionaries, then the resulting trait is called a "mapped" trait. In practice,
this means that the resulting object actually contains two attributes:

.. index:: shadow values

* An attribute whose value is a key in the dictionary used to define the trait.
* An attribute containing its corresponding value (i.e., the mapped or
  "shadow" value). The name of the shadow attribute is simply the base
  attribute name with an underscore appended.

Mapped traits can be used to allow a variety of user-friendly input values to be
mapped to a set of internal, program-friendly values.

.. index:: mapped traits; examples

The following examples illustrates mapped traits that map color names to tuples
representing red, green, blue, and transparency values::

    # mapped.py --- Example of a mapped trait
    from traits.api import HasTraits, Trait

    standard_color = Trait ('black',
                  {'black':       (0.0, 0.0, 0.0, 1.0),
                   'blue':        (0.0, 0.0, 1.0, 1.0),
                   'cyan':        (0.0, 1.0, 1.0, 1.0),
                   'green':       (0.0, 1.0, 0.0, 1.0),
                   'magenta':     (1.0, 0.0, 1.0, 1.0),
                   'orange':      (0.8, 0.196, 0.196, 1.0),
                   'purple':      (0.69, 0.0, 1.0, 1.0),
                   'red':         (1.0, 0.0, 0.0, 1.0),
                   'violet':      (0.31, 0.184, 0.31, 1.0),
                   'yellow':      (1.0, 1.0, 0.0, 1.0),
                   'white':       (1.0, 1.0, 1.0, 1.0),
                   'transparent': (1.0, 1.0, 1.0, 0.0) } )

    red_color = Trait ('red', standard_color)

    class GraphicShape (HasTraits):
        line_color = standard_color
        fill_color = red_color

The GraphicShape class has two attributes: **line_color** and **fill_color**.
These attributes are defined in terms of the **standard_color** trait, which
uses a dictionary. The **standard_color** trait is a mapped trait, which means
that each GraphicShape instance has two shadow attributes: **line_color_**
and **fill_color_**. Any time a new value is assigned to either **line_color**
or **fill_color**, the corresponding shadow attribute is updated with the
value in the dictionary corresponding to the value assigned. For example::

    >>> import mapped
    >>> my_shape1 = mapped.GraphicShape()
    >>> print(my_shape1.line_color, my_shape1.fill_color)
    black red
    >>> print(my_shape1.line_color_, my_shape1.fill_color_)
    (0.0, 0.0, 0.0, 1.0) (1.0, 0.0, 0.0, 1.0)
    >>> my_shape2 = mapped.GraphicShape()
    >>> my_shape2.line_color = 'blue'
    >>> my_shape2.fill_color = 'green'
    >>> print(my_shape2.line_color, my_shape2.fill_color)
    blue green
    >>> print(my_shape2.line_color_, my_shape2.fill_color_)
    (0.0, 0.0, 1.0, 1.0) (0.0, 1.0, 0.0, 1.0)

This example shows how a mapped trait can be used to create a user-friendly
attribute (such as **line_color**) and a corresponding program-friendly shadow
attribute (such as **line_color_**). The shadow attribute is program-friendly
because it is usually in a form that can be directly used by program logic.

There are a few other points to keep in mind when creating a mapped trait:

* If not all values passed to the Trait() function are dictionaries, the
  non-dictionary values are copied directly to the shadow attribute (i.e.,
  the mapping used is the identity mapping).
* Assigning directly to a shadow attribute (the attribute with the trailing
  underscore in the name) is not allowed, and raises a TraitError.

The concept of a mapped trait extends beyond traits defined via a dictionary.
Any trait that has a shadow value is a mapped trait. For example, for the
Expression trait, the assigned value must be a valid Python expression, and the
shadow value is the compiled form of the expression.

.. index:: trait handler; classes

.. _trait-handlers:

Trait Handlers
--------------

In some cases, you may want to define a customized trait that is unrelated to
any predefined trait behavior, or that is related to a predefined trait that
happens to not be derived from TraitType. The option for such cases is to use a
trait handler, either a predefined one or a custom one that you write.

.. index:: TraitHandler class

A trait handler is an instance of the
traits.trait_handlers.TraitHandler class, or of a subclass, whose
task is to verify the correctness of values assigned to object traits. When a
value is assigned to an object trait that has a trait handler, the trait
handler's validate() method checks the value, and assigns that value or a
computed value, or raises a TraitError if the assigned value is not valid. Both
TraitHandler and TraitType derive from BaseTraitHandler; TraitHandler has a more
limited interface.

The Traits package provides a number of predefined TraitHandler subclasses. A few
of the predefined trait handler classes are described in the following sections.
These sections also demonstrate how to define a trait using a trait handler and
the Trait() factory function. For a complete list and descriptions of predefined
TraitHandler subclasses, refer to the *Traits API Reference*, in the section on
the traits.trait_handlers module.

.. index:: TraitPrefixList class

.. _traitprefixlist:

TraitPrefixList
```````````````

The TraitPrefixList handler accepts not only a specified set of strings as
values, but also any unique prefix substring of those values. The value assigned
to the trait attribute is the full string that the substring matches.

.. index::
   pair: TraitPrefixList class; examples

For example::

    >>> from traits.api import HasTraits, Trait
    >>> from traits.api import TraitPrefixList
    >>> class Alien(HasTraits):
    ...   heads = Trait('one', TraitPrefixList(['one','two','three']))
    ...
    >>> alf = Alien()
    >>> alf.heads = 'o'
    >>> print(alf.heads)
    one
    >>> alf.heads = 'tw'
    >>> print(alf.heads)
    two
    >>> alf.heads = 't'  # Error, not a unique prefix
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "c:\svn\ets3\traits_3.0.3\enthought\traits\trait_handlers.py", line 1802,
     in validate self.error( object, name, value )
      File "c:\svn\ets3\traits_3.0.3\enthought\traits\trait_handlers.py", line 175,
    in error value )
    traits.trait_errors.TraitError: The 'heads' trait of an Alien instance
     must be 'one' or 'two' or 'three' (or any unique prefix), but a value of 't'
     <type 'str'> was specified.

.. index:: TraitPrefixMap class

.. _traitprefixmap:

TraitPrefixMap
``````````````

The TraitPrefixMap handler combines the TraitPrefixList with mapped traits. Its
constructor takes a parameter that is a dictionary whose keys are strings. A
string is a valid value if it is a unique prefix for a key in the dictionary.
The value assigned is the dictionary value corresponding to the matched key.

.. index::
   pair: TraitPrefixMap class; examples

The following example uses TraitPrefixMap to define a Boolean trait that accepts
any prefix of 'true', 'yes', 'false', or 'no', and maps them to 1 or 0.
::

    # traitprefixmap.py --- Example of using the TraitPrefixMap handler
    from traits.api import Trait, TraitPrefixMap

    boolean_map = Trait('true', TraitPrefixMap( {
                                  'true': 1,
                                  'yes':  1,
                                  'false': 0,
                                  'no':   0 } ) )

.. index:: handler classes; custom

.. _custom-trait-handlers:

Custom Trait Handlers
---------------------

If you need a trait that cannot be defined using a predefined trait handler
class, you can create your own subclass of TraitHandler. The constructor
(i.e., __init__() method) for your TraitHandler subclass can accept whatever
additional information, if any, is needed to completely specify the trait. The
constructor does not need to call the TraitHandler base class's constructor.

The only method that a custom trait handler must implement is validate(). Refer
to the *Traits API Reference* for details about this function.

.. index::
   pair: custom trait handler; examples

.. _example-custom-trait-handler:

Example Custom Trait Handler
````````````````````````````

The following example defines the OddInt trait (also implemented as a trait type
in :ref:`defining-a-trait-type`) using a TraitHandler subclass.
::

    # custom_traithandler.py --- Example of a custom TraitHandler
    import types
    from traits.api import TraitHandler

    class TraitOddInteger(TraitHandler):
        def validate(self, object, name, value):
            if ((type(value) is types.IntType) and
                (value > 0) and ((value % 2) == 1)):
                return value
            self.error(object, name, value)

        def info(self):
            return '**a positive odd integer**'

An application could use this new trait handler to define traits such as the
following::

    # use_custom_th.py --- Example of using a custom TraitHandler
    from traits.api import HasTraits, Range, Trait
    from custom_traithandler import TraitOddInteger

    class AnOddClass(HasTraits):
        oddball = Trait(1, TraitOddInteger())
        very_odd = Trait(-1, TraitOddInteger(), Range(-10, -1))

The following example demonstrates why the info() method returns a phrase rather
than a complete sentence::

    >>> from use_custom_th import AnOddClass
    >>> odd_stuff = AnOddClass()
    >>> odd_stuff.very_odd = 0
    Traceback (most recent call last):
      File "test.py", line 25, in ?
        odd_stuff.very_odd = 0
      File "C:\wrk\src\lib\enthought\traits\traits.py", line 1119, in validate
        raise TraitError(excp)
    traits.traits.TraitError: The 'very_odd' trait of an AnOddClass instance
    must be **a positive odd integer** or -10 <= an integer <= -1, but a value
    of 0 <type 'int'> was specified.

Note the emphasized result returned by the info() method, which is embedded in
the exception generated by the invalid assignment.

.. rubric:: Footnotes

.. [6] All of the basic predefined traits (such as Float and Str) have a
   BaseType version that does not have the **fast_validate** attribute.
