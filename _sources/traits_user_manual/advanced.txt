.. _advanced-topics:

===============
Advanced Topics
===============

The preceding sections provide enough information for you to use traits for
manifestly-typed attributes, with initialization and validation. This section
describes the advanced features of the Traits package

.. _initialization-and-validation-revisited:

Initialization and Validation Revisited
---------------------------------------

The following sections present advanced topics related to the initialization and
validation features of the Traits package.

* Dynamic initialization
* Overriding default values
* Reusing trait definitions
* Trait attribute definition strategies
* Type-checked methods

.. index:: initialization; dynamic

.. _dynamic-initialization:

Dynamic Initialization
``````````````````````

When you define trait attributes using predefined traits, the Trait() factory
function or trait handlers, you typically specify their default values
statically. You can also define a method that dynamically initializes a trait
attribute the first time that the attribute value is accessed. To do this, you
define a method on the same class as the trait attribute, with a name based on
the name of the trait attribute:

.. index:: default value; method

.. method:: _name_default()

This method initializes the *name* trait attribute, returning its initial value.
The method overrides any default value specified in the trait definition.

.. index:: get_default_value()

It is also possible to define a dynamic method for the default value in a trait
type subclass (get_default_value()). However, however, using a
_\ *name*\ _default()  method avoids the overhead of subclassing a trait.

.. index:: default value; overriding in a subclass
.. index::
   pair: examples; overriding default values

.. _overriding-default-values-in-a-subclass:

Overriding Default Values in a Subclass
```````````````````````````````````````

Often, a subclass must override a trait attribute in a parent class by providing
a different default value. You can specify a new default value without
completely re-specifying the trait definition for the attribute. For example::

    # override_default.py -- Example of overriding a default value for
    #                        a trait attribute in a subclass
    from traits.api import HasTraits, Range, Str

    class Employee(HasTraits):
        name = Str
        salary_grade = Range(value=1, low=1, high=10)

    class Manager(Employee):
        salary_grade = 5

In this example, the **salary_grade** of the Employee class is a range from 1 to
10, with a default value of 1. In the Manager subclass, the default value of
**salary_grade** is 5, but it is still a range as defined in the Employee class.

.. index:: trait; definitions; reusing

.. _reusing-trait-definitions:

Reusing Trait Definitions
`````````````````````````

As mentioned in :ref:`defining-traits-initialization-and-validation`, in most
cases, traits are defined in-line in attribute definitions, but they can also be
defined independently. A trait definition only describes the characteristics of
a trait, and not the current value of a trait attribute, so it can be used in
the definition of any number of attributes. For example::

    # trait_reuse.py --- Example of reusing trait definitions
    from traits.api import HasTraits, Range

    coefficient = Range(-1.0, 1.0, 0.0))

    class quadratic(HasTraits):
        c2 = coefficient
        c1 = coefficient
        c0 = coefficient
        x  = Range(-100.0, 100.0, 0.0)

In this example, a trait named **coefficient** is defined externally to the
class **quadratic**, which references **coefficient** in the definitions of its
trait attributes **c2**, **c1**, and **c0**. Each of these attributes has a
unique value, but they all use the same trait definition to determine whether a
value assigned to them is valid.

.. index:: explicit trait attribute definition

.. _trait-attribute-definition-strategies:

Trait Attribute Definition Strategies
`````````````````````````````````````

In the preceding examples in this guide, all trait attribute definitions have
bound a single object attribute to a specified trait definition. This is known
as "explicit" trait attribute definition. The Traits package supports other
strategies for defining trait attributes. You can associate a category of
attributes with a particular trait definition, using the trait attribute name
wildcard. You can also dynamically create trait attributes that are specific to
an instance, using the add_trait() method, rather than defined on a class. These
strategies are described in the following sections.

.. index:: wildcard; trait attribute names
   pair: wildcard; examples

.. _trait-attribute-name-wildcard:

Trait Attribute Name Wildcard
:::::::::::::::::::::::::::::

The Traits package enables you to define a category of trait attributes
associated with a particular trait definition, by including an underscore ('_')
as a wildcard at the end of a trait attribute name. For example::

    # temp_wildcard.py --- Example of using a wildcard with a Trait
    #                      attribute name
    from traits.api import Any, HasTraits

    class Person(HasTraits):
        temp_ = Any

This example defines a class Person, with a category of attributes that have
names beginning with ``temp``, and that are defined by the Any trait. Thus, any
part of the program that uses a Person instance can reference attributes such as
**tempCount**, **temp_name**, or **temp_whatever**, without having to explicitly
declare these trait attributes. Each such attribute has None as the initial
value and allows assignment of any value (because it is based on the Any trait).

You can even give all object attributes a default trait definition, by
specifying only the wildcard character for the attribute name::

    # all_wildcard.py --- Example of trait attribute wildcard rules
    from traits.api import Any, HasTraits, Int, Str

    class Person ( HasTraits ):

        # Normal, explicitly defined trait:
        name = Str

        # By default, let all traits have any value:
        _ = Any

        # Except for this one, which must be an Int:
        age = Int
    """
    >>> bill = Person()
    >>> # These assignments should all work:
    >>> bill.name      = 'William'
    >>> bill.address  = '121 Drury Lane'
    >>> bill.zip_code = 55212
    >>> bill.age      = 49
    >>> # This should generate an error (must be an Int):
    >>> bill.age = 'middle age'
    Traceback (most recent call last):
      File "all_wildcard.py", line 33, in <module>
        bill.age = 'middle age'
      File "c:\wrk\src\lib\enthought\traits\\trait_handlers.py", line 163, in error
        raise TraitError, ( object, name, self.info(), value )
    TraitError: The 'age' trait of a Person instance must be an integer, but a value
     of 'middle age' <type 'str'> was specified.
    """

In this case, all Person instance attributes can be created on the fly and are
defined by the Any trait.

.. index:: wildard; rules

.. _wildcard-rules:

Wildcard Rules
''''''''''''''

When using wildcard characters in trait attribute names, the following rules are
used to determine what trait definition governs an attribute:

1. If an attribute name exactly matches a name without a wildcard character,
   that definition applies.
2. Otherwise, if an attribute name matches one or more names with wildcard
   characters, the definition with the longest name applies.

Note that all possible attribute names are covered by one of these two rules.
The base HasTraits class implicitly contains the attribute definition
``_ = Python``. This rule guarantees that, by default, all attributes have
standard Python language semantics.

These rules are demonstrated by the following example::

    # wildcard_rules.py -- Example of trait attribute wildcard rules
    from traits.api import Any, HasTraits, Int, Python

    class Person(HasTraits):
        temp_count = Int(-1)
        temp_      = Any
        _          = Python

In this example, the Person class has a **temp_count** attribute, which must be
an integer and which has an initial value of -1. Any other attribute with a name
starting with ``temp`` has an initial value of None and allows any value to be
assigned. All other object attributes behave like normal Python attributes
(i.e., they allow any value to be assigned, but they must have a value assigned
to them before their first reference).

.. index:: Disallow; object, examples; Disallow object

.. _disallow-object:

Disallow Object
'''''''''''''''

The singleton object Disallow can be used with wildcards to disallow all
attributes that are not explicitly defined. For example::

    # disallow.py --- Example of using Disallow with wildcards
    from traits.api import \
        Disallow, Float, HasTraits, Int, Str

    class Person (HasTraits):
        name   = Str
        age    = Int
        weight = Float
        _      = Disallow

In this example, a Person instance has three trait attributes:

* **name**: Must be a string; its initial value is ''.
* **age**: Must be an integer; its initial value is 0.
* **weight**: Must be a float; its initial value is 0.0.

All other object attributes are explicitly disallowed. That is, any attempt to
read or set any object attribute other than **name**, **age**, or **weight**
causes an exception.

.. index:: HasTraits class; predefined subclasses

.. _hastraits-subclasses:

HasTraits Subclasses
''''''''''''''''''''

Because the HasTraits class implicitly contains the attribute definition
``_ = Python``, subclasses of HasTraits by default have very standard Python
attribute behavior for any attribute not explicitly defined as a trait
attribute. However, the wildcard trait attribute definition rules make it easy
to create subclasses of HasTraits with very non-standard attribute behavior. Two
such subclasses are predefined in the Traits package: HasStrictTraits and
HasPrivateTraits.

.. index:: HasStrictTraits class

.. _hasstricttraits:

HasStrictTraits
'''''''''''''''

This class guarantees that accessing any object attribute that does not have an
explicit or wildcard trait definition results in an exception. This can be
useful in cases where a more rigorous software engineering approach is employed
than is typical for Python programs. It also helps prevent typos and spelling
mistakes in attribute names from going unnoticed; a misspelled attribute name
typically causes an exception. The definition of HasStrictTraits is the
following::

    class HasStrictTraits(HasTraits):
          _ = Disallow

HasStrictTraits can be used to create type-checked data structures, as in the
following example::

   class TreeNode(HasStrictTraits):
       left = This
       right = This
       value = Str

This example defines a TreeNode class that has three attributes: **left**,
**right**, and **value**. The **left** and **right** attributes can only be
references to other instances of TreeNode (or subclasses), while the **value**
attribute must be a string. Attempting to set other types of values generates an
exception, as does attempting to set an attribute that is not one of the three
defined attributes. In essence, TreeNode behaves like a type-checked data
structure.

.. index:: HasPrivateTraits class

.. _hasprivatetraits:

HasPrivateTraits
''''''''''''''''

This class is similar to HasStrictTraits, but allows attributes beginning with
'_' to have an initial value of None, and to not be type-checked. This is useful
in cases where a class needs private attributes, which are not part of the
class's public API, to keep track of internal object state. Such attributes do
not need to be type-checked because they are only manipulated by the (presumably
correct) methods of the class itself. The definition of HasPrivateTraits is the
following::

    class HasPrivateTraits(HasTraits):
          __ = Any
          _  = Disallow

These subclasses of HasTraits are provided as a convenience, and their use is
completely optional. However, they do illustrate how easy it is to create
subclasses with customized default attribute behavior if desired.

.. index:: trait attributes; per-object

.. _per-object-trait-attributes:

Per-Object Trait Attributes
'''''''''''''''''''''''''''

The Traits package allows you to define dynamic trait attributes that are
object-, rather than class-, specific. This is accomplished using the
add_trait() method of the HasTraits class:

.. method:: add_trait(name, trait)

.. index:: examples; per-object trait attributes

For example::

    # object_trait_attrs.py --- Example of per-object trait attributes
    from traits.api import HasTraits, Range

    class GUISlider (HasTraits):

        def __init__(self, eval=None, label='Value',
                     trait=None, min=0.0, max=1.0,
                     initial=None, **traits):
            HasTraits.__init__(self, **traits)
            if trait is None:
                if min > max:
                    min, max = max, min
                if initial is None:
                    initial = min
                elif not (min <= initial <= max):
                    initial = [min, max][
                                abs(initial - min) >
                                abs(initial - max)]
                trait = Range(min, max, value = initial)
            self.add_trait(label, trait)

This example creates a GUISlider class, whose __init__() method can accept a
string label and either a trait definition or minimum, maximum, and initial
values. If no trait definition is specified, one is constructed based on the
**max** and **min** values. A trait attribute whose name is the value of label
is added to the object, using the trait definition (whether specified or
constructed). Thus, the label trait attribute on the GUISlider object is
determined by the calling code, and added in the __init__() method using
add_trait().

You can require that add_trait() must be used in order to add attributes to a
class, by deriving the class from HasStrictTraits (see :ref:`hasstricttraits`).
When a class inherits from HasStrictTraits, the program cannot create a new
attribute (either a trait attribute or a regular attribute) simply by assigning
to it, as is normally the case in Python. In this case, add_trait() is the only
way to create a new attribute for the class outside of the class definition.

.. index:: methods; type-checking, type-checking methods

.. _type-checked-methods:

Type-Checked Methods
````````````````````

In addition type-checked attributes, the Traits package provides the ability to
create type-checked methods.

.. index::
   pair: examples; type-checking methods

A type-checked method is created by writing a normal method definition within a
class, preceded by a method() signature function call, as shown in the following
example::

    # type_checked_methods.py --- Example of traits-based method type
    #                             checking
    from traits.api import HasTraits, method, Tuple

    Color = Tuple(int, int, int, int)

    class Palette(HasTraits):

        method(Color, color1=Color, color2=Color)
        def blend (self, color1, color2):
            return ((color1[0] + color2[0]) / 2,
                    (color1[1] + color2[1]) / 2,
                    (color1[2] + color2[2]) / 2,
                    (color1[3] + color2[3]) / 2 )

        method(Color, Color, Color)
        def max (self, color1, color2):
            return (max( color1[0], color2[0]),
                    max( color1[1], color2[1]),
                    max( color1[2], color2[2]),
                    max( color1[3], color2[3]) )

In this example, Color is defined to be a trait that accepts tuples of four
integer values. The method() signature function appearing before the definition
of the blend() method ensures that the two arguments to blend() both match the
Color trait definition, as does the result returned by blend(). The method
signature appearing before the max() method does exactly the same thing, but
uses positional rather than keyword arguments. When

Use of the method() signature function is optional. Methods not preceded by a
method() function have standard Python behavior (i.e., no type-checking of
arguments or results is performed). Also, the method() function can be used in
classes that do not subclass from HasTraits, because the resulting method
performs the type checking directly. And finally, when the method() function is
used, it must directly precede the definition of the method whose type signature
it defines. (However, white space is allowed.) If it does not, a TraitError is
raised.

.. index:: interfaces

.. _interfaces:

Interfaces
----------

Starting in version 3.0, the Traits package supports declaring and implementing
*interfaces*. An interface is an abstract data type that defines a set of
attributes and methods that an object must have to work in a given situation.
The interface says nothing about what the attributes or methods do, or how they
do it; it just says that they have to be there. Interfaces in Traits are similar
to those in Java. They can be used to declare a relationship among classes which
have similar behavior but do not have an inheritance relationship. Like Traits
in general, Traits interfaces don't make anything possible that is not already
possible in Python, but they can make relationships more explicit and enforced.
Python programmers routinely use implicit, informal interfaces (what's known as
"duck typing"). Traits allows programmers to define explicit and formal
interfaces, so that programmers reading the code can more easily understand what
kinds of objects are actually *intended* to be used in a given situation.

.. index:: interfaces; defining, examples; interface definition

.. _defining-an-interface:

Defining an Interface
`````````````````````

To define an interface, create a subclass of Interface::

    # interface_definition.py -- Example of defining an interface
    from traits.api import Interface

    class IName(Interface):

        def get_name(self):
            ''' Returns a string which is the name of an object. '''

Interface classes serve primarily has documentation of the methods and
attributes that the interface defines. In this case, a class that implements the
IName interface must have a method named get_name(), which takes no arguments
and returns a string. Do not include any implementation code in an interface
declaration. However, the Traits package does not actually check to ensure that
interfaces do not contain implementations.

By convention, interface names have a capital 'I' at the beginning of the name.

.. index:: interfaces; implementing

.. _implementing-an-interface:

Implementing an Interface
`````````````````````````

A class declares that it implements one or more interfaces using the
implements() function, which has the signature:

.. currentmodule:: traits.has_traits
.. function:: implements( interface[, interface2 , ... , interfaceN] )

.. index:: examples; interface implementation, interfaces; implementation; example

Interface names beyond the first one are optional. The call to implements() must
occur at class scope within the class definition. For example::

    # interface_implementation.py -- Example of implementing an
    #                                interface
    from traits.api import HasTraits, implements, Str
    from interface_definition import IName

    class Person(HasTraits):
        implements(IName)

        first_name = Str( 'John' )
        last_name  = Str( 'Doe' )

        # Implementation of the 'IName' interface:
        def get_name ( self ):
            ''' Returns the name of an object. '''
            return ('%s %s' % ( self.first_name, self.last_name ))

A class can contain at most one call to implements().

In version 3.0, you can specify whether the implements() function verifies that
the class calling it actually implements the interface that it says it does.
This is determined by the CHECK_INTERFACES variable, which can take one of three
values:

* 0 (default): Does not check whether classes implement their declared interfaces.
* 1: Verifies that classes implement the interfaces they say they do, and logs
  a warning if they don't.
* 2: Verifies that classes implement the interfaces they say they do, and raises
  an InterfaceError if they don't.

The CHECK_INTERFACES variable must be imported directly from the
traits.has_traits module::

    import traits.has_traits
    traits.has_traits.CHECK_INTERFACES = 1

.. index:: interfaces; using, examples; interface usage

.. _using-interfaces:

Using Interfaces
````````````````

You can use an interface at any place where you would normally use a class name.
The most common way to use interfaces is with the Instance trait::

    >>> from traits.api import HasTraits, Instance
    >>> from interface_definition import IName
    >>> class Apartment(HasTraits):
    ...     renter = Instance(IName)
    >>> from interface_implementation import Person
    >>> william = Person(first_name='William', last_name='Adams')
    >>> apt1 = Apartment( renter=william )
    >>> print 'Renter is: ', apt1.renter.get_name()
    Renter is: William Adams

Using an interface class with an Instance trait definition declares that the
trait accepts only values that implement the specified interface. (If the
assigned object does not implement the interface, the Traits package may
automatically substitute an adapter object that implements the specified
interface. See :ref:`adaptation` for more information.)

.. index:: adaptation

.. _adaptation:

Adaptation
----------

Adaptation is the process of transforming an object that does not implement a
specific interface (or set of interfaces) into an object that does. In Traits,
this process is accomplished with *adapters*, which are special classes whose
purpose is to adapt objects from one set of interfaces to another. Once adapter
classes are defined, they are implicitly instantiated whenever they are needed
to fulfill interface requirements. That is, if an Instance trait requires its
values to implement interface IFoo, and an object is assigned to it which is of
class Bar, which does not implement IFoo, then an adapter from Bar to IFoo is
instantiated (if such an adapter class exists), and the adapter object is
assigned to the trait. If necessary, a "chain" of adapter objects might be
created, in order to perform the required adaptation.

.. index:: adapters; defining

.. _defining-adapters:

Defining Adapters
`````````````````

The Traits package provides several mechanisms for defining adapter classes:

* Subclassing Adapter
* Defining an adapter class without subclassing Adapter
* Declaring a class to be an adapter externally to the class

.. index:: Adapter class

.. _subclassing-adapter:

Subclassing Adapter
:::::::::::::::::::

The Traits package provides an Adapter class as convenience. This class
streamlines the process of creating a new adapter class. It has a standard
constructor that does not normally need to be overridden by subclasses. This
constructor accepts one parameter, which is the object to be adapted, and
assigns that object to the adaptee trait attribute.

As an adapter writer, the only members you need to add to a subclass of Adapter
are:

.. index:: adaptee attribute

* A call to implements() declaring which interfaces the adapter class
  implements on behalf of the object it is adapting.
* A trait attribute named **adaptee** that declares what type of object it is
  an adapter for. Usually, this is an Instance trait.
* Implementations of the interfaces declared in the implements() call. Usually,
  these methods are implemented using appropriate members on the adaptee object.

.. index::
   pair: examples; Adapter class

The following code example shows a definition of a simple adapter class::

    # simple_adapter.py -- Example of adaptation using Adapter
    from traits.api import Adapter, Instance, implements
    from interface_definition import IName
    from interface_implementation import Person

    class PersonINameAdapter( Adapter ):

        # Declare what interfaces this adapter implements for its
        # client:
        implements( IName )

        # Declare the type of client it supports:
        adaptee = Instance( Person )

        # Implement the 'IName' interface on behalf of its client:
        def get_name ( self ):
            return ('%s %s' % ( self.adaptee.first_name,
                                self.adaptee.last_name ))

.. index:: adapters; creating from scratch

.. _creating-an-adapter-from-scratch:

Creating an Adapter from Scratch
::::::::::::::::::::::::::::::::

You can create an adapter class without subclassing Adapter. If so, you must
provide the same information and setup that are implicitly provided by Adapter.

In particular, you must use the adapts() function instead of the implements()
function, and you must define a constructor that corresponds to the constructor
of Adapter. The adapts() function defines the class that contains it as an
adapter class, and declares the set of interfaces that the class implements.

The signature  of the adapts() function is:

.. currentmodule:: traits.adapter
.. function:: adapts( adaptee_class, interface[, interface2, ... , interfaceN])

This signature is very similar to that of implements(), but adds the class being
adapted as the first parameter. Interface names beyond the first one are
optional.

The constructor for the adapter class must accept one parameter, which is the
object being adapted, and it must save this reference in an attribute that can
be used by implementation code.

.. index:: examples; adapter from scratch

The following code shows an example of implementing an adapter without
subclassing Adapter::

    # scratch_adapter.py -- Example of writing an adapter from scratch
    from traits.api import HasTraits, Instance, adapts
    from interface_definition import IName
    from interface_implementation import Person


    class PersonINameAdapter ( HasTraits ):
        # Declare what interfaces this adapter implements,
        # and for what class:
        adapts( Person, IName )
        # Declare the type of client it supports:
        client = Instance( Person )

        # Implement the adapter's constructor:
        def __init__ ( self, client ):
            self.client = client

        # Implement the 'IName' interface on behalf of its client:
        def get_name ( self ):
            return ('%s %s' % ( self.client.first_name,
                                self.client.last_name ))

.. index:: adapters; declaring externally

.. _declaring-a-class-as-an-adapter-externally:

Declaring a Class as an Adapter Externally
::::::::::::::::::::::::::::::::::::::::::

You can declare a class to be an adapter by calling the adapts() function
externally to the class definition. The class must provide the same information
and setup as the Adapter class, just as in the case where adapts() is called
within the class definition. That is, it must provide a constructor that accepts
the object being adapted as a parameter, and it must implement the interfaces
specified in the call to adapts().

In this case, signature of the adapts() function is:

.. function: adapts( adapter_class, adaptee_class, interface[, interface2, ... , interfaceN] )

As with implements() and the other form of adapts(), interface names beyond the
first one are optional.

.. index:: examples; adapter externally declared

The following code shows this use of the adapts() function::

    # external_adapter.py -- Example of declaring a class as an
    #                        adapter externally to the class
    from traits.api import adapts
    from interface_definition import IName
    from interface_implementation import Person

    class AnotherPersonAdapter ( object ):

        # Implement the adapter's constructor:
        def __init__ ( self, person ):
            self.person = person

        # Implement the 'IName' interface on behalf of its client:
        def get_name ( self ):
            return ('%s %s' % ( self.person.first_name,
                                self.person.last_name ))

    adapts( AnotherPersonAdapter, Person, IName )

.. index:: adapters; using

.. _using-adapters:

Using Adapters
``````````````

You define adapter classes as described in the preceding sections, but you do
not explicitly create instances of these classes. The Traits package
automatically creates them whenever an object is assigned to an interface
Instance trait, and the object being assigned does not implement the required
interface. If an adapter class exists that can adapt the specified object to the
required interface, an instance of the adapter class is created for the object,
and is assigned as the actual value of the Instance trait.

In some cases, no single adapter class exists that adapts the object to the
required interface, but a series of adapter classes exist that together perform
the required adaptation. In such cases, the necessary set of adapter objects are
created, and the "last" link in the chain, the one that actually implements the
required interface, is assigned as the trait value. When a situation like this
arises, the adapted object assigned to the trait always contains the smallest
set of adapter objects needed to adapt the original object.

.. index:: adapters; controlling

.. _controlling-adaptation:

Controlling Adaptation
``````````````````````

Adaptation normally happens automatically when needed, and when appropriate
adapter classes are available. However, the Instance trait lets you control how
adaptation is performed, through its **adapt** metadata attribute. The **adapt**
metadata attribute can have one of the following values:

* ``no``: Adaptation is not allowed for this trait attribute.
* ``yes``: Adaptation is allowed. If adaptation fails, an exception is raised.
* ``default``: Adaptation is allowed. If adaptation fails, the default value
  for the trait is assigned instead.

.. index:: adapt metadata

The default value for the **adapt** metadata attribute is ``yes``.

.. index::
   pair: examples; adapt metadata

The following code is an example of an interface Instance trait attribute that
uses adapt metadata::

    # adapt_metadata.py -- Example of using 'adapt' metadata
    from traits.api import HasTraits, Instance
    from interface_definition import IName

    class Apartment( HasTraits ):
        renter = Instance( IName, adapt='no' )

Using this definition, any value assigned to renter must implement the IName
interface. Otherwise, an exception is raised.

.. index:: property traits

.. _property-traits:

Property Traits
---------------

The predefined Property() trait factory function defines a Traits-based version
of a Python property, with "getter" and "setter" methods. This type of trait
provides a powerful technique for defining trait attributes whose values depend
on the state of other object attributes. In particular, this can be very useful
for creating synthetic trait attributes which are editable or displayable in a
Trait UI view.

.. _property-factory-function:

Property Factory Function
`````````````````````````

The Property() function has the following signature:

.. currentmodule:: traits.traits
.. function:: Property( [fget=None, fset=None, fvalidate=None, force=False, handler=None, trait=None, **metadata] )

All parameters are optional, including the *fget* "getter" and *fset* "setter"
methods. If no parameters are specified, then the trait looks for and uses
methods on the same class as the attribute that the trait is assigned to, with
names of the form _get_\ *name*\ () and _set_\ *name*\ (), where *name* is the
name of the trait attribute.

If you specify a trait as either the *fget* parameter or the *trait* parameter,
that trait's handler supersedes the *handler* argument, if any. Because the
*fget* parameter accepts either a method or a trait, you can define a Property
trait by simply passing another trait. For example::

    source = Property( Code )

This line defines a trait whose value is validated by the Code trait, and whose
getter and setter methods are defined elsewhere on the same class.

If a Property trait has only a getter function, it acts as read-only; if it has
only a setter function, it acts as write-only. It can lack a function due to two
situations:

* A function with the appropriate name is not defined on the class.
* The *force* option is True, (which requires the Property() factory function
  to ignore functions on the class) and one of the access functions was not
  specified in the arguments.

.. index:: property traits; caching value

.. _caching-a-property-value:

Caching a Property Value
````````````````````````

In some cases, the cost of computing the value of a property trait attribute may
be very high. In such cases, it is a good idea to cache the most recently
computed value, and to return it as the property value without recomputing it.
When a change occurs in one of the attributes on which the cached value depends,
the cache should be cleared, and the property value should be recomputed the
next time its value is requested.

.. index:: cached_property decorator, depends_on metadata

One strategy to accomplish caching would be to use a private attribute for the
cached value, and notification listener methods on the attributes that are
depended on. However, to simplify the situation, Property traits support a
@cached_property decorator and **depends_on** metadata. Use @cached_property to
indicate that a getter method's return value should be cached. Use
**depends_on** to indicate the other attributes that the property depends on.

.. index:: examples; cached property

For example::

    # cached_prop.py -- Example of @cached_property decorator
    from traits.api import HasPrivateTraits, List, Int,\
                                     Property, cached_property

    class TestScores ( HasPrivateTraits ):

        scores  = List( Int )
        average = Property( depends_on = 'scores' )

        @cached_property
        def _get_average ( self ):
            s = self.scores
            return (float( reduce( lambda n1, n2: n1 + n2, s, 0 ) )
                     / len( s ))

The @cached_property decorator takes no arguments. Place it on the line
preceding the property's getter method.

The **depends_on** metadata attribute accepts extended trait references, using
the same syntax as the on_trait_change() method's name parameter, described in
:ref:`the-name-parameter`. As a result, it can take values that specify
attributes on referenced objects, multiple attributes, or attributes that are
selected based on their metadata attributes.

.. index:: persistence, __getstate__(), __setstate__()

.. _persistence:

Persistence
-----------

In version 3.0, the Traits package provides __getstate__() and __setstate__()
methods on HasTraits, to implement traits-aware policies for serialization and
deserialization (i.e., pickling and unpickling).

.. index:: HasTraits class; pickling, pickling HasTraits objects

.. _pickling-hastraits-objects:

Pickling HasTraits Objects
``````````````````````````

Often, you may wish to control for a HasTraits subclass which parts of an
instance's state are saved, and which are discarded. A typical approach is to
define a __getstate__() method that copies the object's __dict__ attribute, and
deletes those items that should not be saved. This approach works, but can have
drawbacks, especially related to inheritance.

.. index:: transient; metadata

The HasTraits __getstate__() method uses a more generic approach, which
developers can customize through the use of traits metadata attributes, often
without needing to override or define a __getstate__() method in their
application classes. In particular, the HasTraits __getstate__() method discards
the values of all trait attributes that have the **transient** metadata
attribute set to True, and saves all other trait attributes. So, to mark which
trait values should not be saved, you set **transient** to True in the metadata
for those trait attributes. The benefits of this approach are that you do not
need to override __getstate__(), and that the metadata helps document the
pickling behavior of the class.

.. index:: examples; transient metadata

For example::

    # transient_metadata.py -- Example of using 'transient' metadata
    from traits.api import HasTraits, File, Any

    class DataBase ( HasTraits ):
        # The name of the data base file:
        file_name = File

        # The open file handle used to access the data base:
        file = Any( transient = True )

In this example, the DataBase class's file trait is marked as transient because
it normally contains an open file handle used to access a data base. Since file
handles typically cannot be pickled and restored, the file handle should not be
saved as part of the object's persistent state. Normally, the file handle would
be re-opened by application code after the object has been restored from its
persisted state.

.. index:: transient; predefined traits

.. _predefined-transient-traits:

Predefined Transient Traits
```````````````````````````

A number of the predefined traits in the Traits package are defined with
**transient** set to True, so you do not need to explicitly mark them. The
automatically transient traits are:

* Constant
* Event
* Read-only and write-only Property traits (See :ref:`property-factory-function`)
* Shadow attributes for mapped traits (See :ref:`mapped-traits`)
* Private attributes of HasPrivateTraits subclasses (See :ref:`hasprivatetraits`)
* Delegate traits that do not have a local value overriding the delegation.
  Delegate traits with a local value are non-transient, i.e., they are
  serialized. (See :ref:`delegatesto`) You can mark a Delegate trait as
  transient if you do not want its value to ever be serialized.

.. index:: __getstate__(); overriding

.. _overriding_getstate:

Overriding __getstate__()
`````````````````````````

In general, try to avoid overriding __getstate__() in subclasses of HasTraits.
Instead, mark traits that should not be pickled with ``transient = True``
metadata.

However, in cases where this strategy is insufficient, use the following pattern
to override __getstate__() to remove items that should not be persisted::

    def __getstate__ ( self ):
        state = super( XXX, self ).__getstate__()

        for key in [ 'foo', 'bar' ]:
            if state.has_key( key ):
                del state[ key ]

        return state

.. index:: unpickling HasTraits objects, HasTraits class; unpickling

.. _unpicking-hastraits-objects:

Unpickling HasTraits Objects
````````````````````````````

The __setstate__() method of HasTraits differs from the default Python behavior
in one important respect: it explicitly sets the value of each attribute using
the values from the state dictionary, rather than simply storing or copying the
entire state dictionary to its **__dict__** attribute. While slower, this
strategy has the advantage of generating trait change notifications for each
attribute. These notifications are important for classes that rely on them to
ensure that their internal object state remains consistent and up to date.

.. index:: __setstate__(); overriding

.. _overriding-setstate:

Overriding __setstate__()
`````````````````````````

You may wish to override the HasTraits __setstate__() method, for example for
classes that do not need to receive trait change notifications, and where the
overhead of explicitly setting each attribute is undesirable. You can
override __setstate__() to update the object's __dict__ directly. However, in
such cases, it is important ensure that trait notifications are properly set
up so that later change notifications are handled. You can do this in two ways:

* Call the __setstate__() super method (for example, with an empty state
  dictionary).

* Call the HasTraits class's private _init_trait_listeners() method; this
  method has no parameters and does not return a result.

.. index:: HasTraits class; methods

.. _useful-methods-on-hastraits:

Useful Methods on HasTraits
---------------------------

The HasTraits class defines a number of methods, which are available to any
class derived from it, i.e., any class that uses trait attributes. This section
provides examples of a sampling of these methods. Refer to the *Traits API
Reference* for a complete list of HasTraits methods.

.. index:: add_trait()

.. _add-trait:

add_trait()
```````````

This method adds a trait attribute to an object dynamically, after the object
has been created. For more information, see :ref:`per-object-trait-attributes`.

.. index:: clone_traits()

.. _clone-traits:

clone_traits()
``````````````

This method copies trait attributes from one object to another. It can copy
specified attributes, all explicitly defined trait attributes, or all explicitly
and implicitly defined trait attributes on the source object.

This method is useful if you want to allow a user to edit a clone of an object,
so that changes are made permanent only when the user commits them. In such a
case, you might clone an object and its trait attributes; allow the user to
modify the clone; and then re-clone only the trait attributes back to the
original object when the user commits changes.

.. index:: set()

.. _set:

set()
`````

This method takes a list of keyword-value pairs, and sets the trait attribute
corresponding to each keyword to the matching value. This shorthand is useful
when a number of trait attributes need to be set on an object, or a trait
attribute value needs to be set in a lambda function. For example::

    person.set(name='Bill', age=27)

The statement above is equivalent to the following::

    person.name = 'Bill'
    person.age = 27

.. index:: add_class_trait()

.. _add-class-trait:

add_class_trait()
`````````````````

The add_class_trait() method is a class method, while the preceding HasTraits
methods are instance methods. This method is very similar to the add_trait()
instance method. The difference is that adding a trait attribute by using
add_class_trait() is the same as having declared the trait as part of the class
definition. That is, any trait attribute added using add_class_trait() is
defined in every subsequently-created instance of the class, and in any
subsequently-defined subclasses of the class. In contrast, the add_trait()
method adds the specified trait attribute only to the object instance it is
applied to.

In addition, if the name of the trait attribute ends with a '_', then a new (or
replacement) prefix rule is added to the class definition, just as if the prefix
rule had been specified statically in the class definition. It is not possible
to define new prefix rules using the add_trait() method.

One of the main uses of the add_class_trait() method is to add trait attribute
definitions that could not be defined statically as part of the body of the
class definition. This occurs, for example, when two classes with trait
attributes are being defined and each class has a trait attribute that should
contain a reference to the other. For the class that occurs first in lexical
order, it is not possible to define the trait attribute that references the
other class, since the class it needs to refer to has not yet been defined.

.. index::
   pair: examples; add_class_trait()

This is illustrated in the following example::

    # circular_definition.py --- Non-working example of mutually-
    #                            referring classes
    from traits.api import HasTraits, Trait

    class Chicken(HasTraits):
        hatched_from = Trait(Egg)

    class Egg(HasTraits):
        created_by = Trait(Chicken)

As it stands, this example will not run because the **hatched_from** attribute
references the Egg class, which has not yet been defined. Reversing the
definition order of the classes does not fix the problem, because then the
**created_by** trait references the Chicken class, which has not yet been defined.

The problem can be solved using the add_class_trait() method, as shown in the
following code::

    # add_class_trait.py --- Example of mutually-referring classes
    #                        using add_class_trait()
    from traits.api import HasTraits, Trait

    class Chicken(HasTraits):
        pass

    class Egg(HasTraits):
        created_by = Trait(Chicken)

    Chicken.add_class_trait('hatched_from', Egg)

.. index:: performance of Traits

.. _performance-considerations-of-traits:

Performance Considerations of Traits
------------------------------------

Using traits can potentially impose a performance penalty on attribute access
over and above that of normal Python attributes. For the most part, this
penalty, if any, is small, because the core of the Traits package is written in
C, just like the Python interpreter. In fact, for some common cases, subclasses
of HasTraits can actually have the same or better performance than old or new
style Python classes.

However, there are a couple of performance-related factors to keep in mind when
defining classes and attributes using traits:

* Whether a trait attribute defers its value through delegation or prototyping
* The complexity of a trait definition

If a trait attribute does not defer its value, the performance penalty can be
characterized as follows:

* Getting a value: No penalty (i.e., standard Python attribute access speed or
  faster)
* Setting a value: Depends upon the complexity of the validation tests
  performed by the trait definition. Many of the predefined trait handlers
  defined in the Traits package support fast C-level validation. For most of
  these, the cost of validation is usually negligible. For other trait
  handlers, with Python-level validation methods, the cost can be quite a bit
  higher.

If a trait attribute does defer its value, the cases to be considered are:

* Getting the default value: Cost of following the deferral chain. The chain
  is resolved at the C level, and is quite fast, but its cost is linear with
  the number of deferral links that must be followed to find the default value
  for the trait.
* Getting an explicitly assigned value for a prototype: No penalty (i.e.,
  standard Python attribute access speed or faster)
* Getting an explicitly assigned value for a delegate: Cost of following the
  deferral chain.
* Setting: Cost of following the deferral chain plus the cost of performing
  the validation of the new value. The preceding discussions about deferral
  chain following and fast versus slow validation apply here as well.

In a typical application scenario, where attributes are read more often than
they are written, and deferral is not used, the impact of using traits is often
minimal, because the only cost occurs when attributes are assigned and
validated.

The worst case scenario occurs when deferral is used heavily, either for
delegation, or for prototyping to provide attributes with default values that
are seldom changed. In this case, the cost of frequently following deferral
chains may impose a measurable performance detriment on the application. Of
course, this is offset by the convenience and flexibility provided by the
deferral model. As with any powerful tool, it is best to understand its
strengths and weaknesses and apply that understanding in determining when use of
the tool is justified and appropriate.



