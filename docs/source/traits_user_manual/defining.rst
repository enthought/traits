.. index:: validation, using traits

.. _defining-traits-initialization-and-validation:

==============================================
Defining Traits: Initialization and Validation
==============================================

Using the Traits package in a Python program involves the following steps:

.. index:: importing Traits names, traits.api; importing from

1. Import the names you need from the Traits package traits.api.

2. Define the traits you want to use.

.. index:: HasTraits class

3. Define classes derived from HasTraits (or a subclass of HasTraits), with
   attributes that use the traits you have defined.

In practice, steps 2 and 3 are often combined by defining traits in-line
in an attribute definition. This strategy is used in many examples in this
guide. However, you can also define traits independently, and reuse the trait
definitions across multiple classes and attributes (see
:ref:`reusing-trait-definitions`).

In order to use trait attributes in a class, the class must inherit from the
HasTraits class in the Traits package (or from a subclass of HasTraits). The
following example defines a class called Person that has a single trait
attribute **weight**, which is initialized to 150.0 and can only take floating
point values.

.. index::
   single: examples; minimal

::

    # minimal.py --- Minimal example of using traits.

    from traits.api import HasTraits, Float

    class Person(HasTraits):
        weight = Float(150.0)

.. index:: attribute definition

In this example, the attribute named **weight** specifies that the class has a
corresponding trait called **weight**. The value associated with the attribute
**weight** (i.e., ``Float(150.0)``) specifies a predefined trait provided with
the Traits package, which requires that values assigned be of the standard
Python type **float**. The value 150.0 specifies the default value of the trait.

The value associated with each class-level attribute determines the
characteristics of the instance attribute identified by the attribute name.
For example::

    >>> from minimal import Person
    >>> # instantiate the class
    >>> joe = Person()
    >>> # Show the default value
    >>> joe.weight
    150.0
    >>> # Assign new values
    >>> joe.weight = 161.9     # OK to assign a float
    >>> joe.weight = 162       # OK to assign an int
    >>> joe.weight = 'average' # Error to assign a string
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "c:\svn\ets3\traits\enthought\traits\trait_handlers.py", line 175,
    in error value )
    traits.trait_errors.TraitError: The 'weight' trait of a Person
    instance must be a float, but a value of 'average' <type 'str'> was
    specified.

In this example, **joe** is an instance of the Person class defined in the
previous example. The **joe** object has an instance attribute **weight**,
whose initial value is the default value of the Person.weight trait (150.0),
and whose assignment is governed by the Person.weight trait's validation
rules. Assigning an integer to **weight** is acceptable because there is no
loss of precision (but assigning a float to an Int trait would cause an error).

The Traits package allows creation of a wide variety of trait types, ranging
from very simple to very sophisticated. The following section presents some of
the simpler, more commonly used forms.

.. index:: predefined traits

.. _predefined-traits:

Predefined Traits
-----------------
The Traits package includes a large number of predefined traits for commonly
used Python data types. In the simplest case, you can assign the trait name
to an attribute of a class derived from HasTraits; any instances of the class
will have that attribute initialized to the built-in default value for the
trait. For example::

    account_balance = Float

This statement defines an attribute whose value must be a floating point
number, and whose initial value is 0.0 (the built-in default value for Floats).

If you want to use an initial value other than the built-in default, you can
pass it as an argument to the trait::

    account_balance = Float(10.0)

Most predefined traits are callable, [2]_ and can accept a default value and
possibly other arguments; all that are callable can also accept metadata as
keyword arguments. (See :ref:`other-predefined-traits` for information on trait
signatures, and see :ref:`trait-metadata` for information on metadata
arguments.)

.. index:: simple types

.. _predefined-traits-for-simple-types:

Predefined Traits for Simple Types
``````````````````````````````````
There are two categories of predefined traits corresponding to Python simple
types: those that coerce values, and those that cast values. These categories
vary in the way that they handle assigned values that do not match the type
explicitly defined for the trait. However, they are similar in terms of the
Python types they correspond to, and their built-in default values, as listed
in the following table.

.. index::
   pair: types; casting
   pair: types; coercing
   pair: plain; integer type
   pair: long; integer type
   pair: type; string
   pair: type; Unicode
.. index:: Boolean type, Bool trait, CBool trait, Complex trait, CComplex trait
.. index:: complex number type, Float trait, CFloat trait, Int trait, CInt trait
.. index:: floating point number type, Long trait, CLong trait, Str trait
.. index:: CStr trait, Unicode; trait, CUnicode trait

.. _predefined-defaults-for-simple-types-table:

.. rubric:: Predefined defaults for simple types

============== ============= ====================== ======================
Coercing Trait Casting Trait Python Type            Built-in Default Value
============== ============= ====================== ======================
Bool           CBool         Boolean                False
Complex        CComplex      Complex number         0+0j
Float          CFloat        Floating point number  0.0
Int            CInt          Plain integer          0
Long           CLong         Long integer           0L
Str            CStr          String                 ''
Unicode        CUnicode      Unicode                u''
============== ============= ====================== ======================

.. index::
   pair: types; coercing

.. _trait-type-coercion:

Trait Type Coercion
:::::::::::::::::::
For trait attributes defined using the predefined "coercing"
traits, if a value is assigned to a trait attribute that is not of the type
defined for the trait, but it can be coerced to the required type, then the
coerced value is assigned to the attribute. If the value cannot be coerced to
the required type, a TraitError exception is raised. Only widening coercions
are allowed, to avoid any possible loss of precision. The following table
lists traits that coerce values, and the types that each coerces.

.. index::
   pair: types; coercing

.. _type-coercions-permitted-for-coercing-traits-table:

.. rubric:: Type coercions permitted for coercing traits

============= ===========================================
Trait         Coercible Types
============= ===========================================
Complex       Floating point number, plain integer
Float         Plain integer
Long          Plain integer
Unicode       String
============= ===========================================

.. index::
   pair: types; casting

.. _trait-type-casting:

Trait Type Casting
::::::::::::::::::
For trait attributes defined using the predefined "casting"
traits, if a value is assigned to a trait attribute that is not of the type
defined for the trait, but it can be cast to the required type, then the cast
value is assigned to the attribute. If the value cannot be cast to the required
type, a TraitError exception is raised. Internally, casting is done using the
Python built-in functions for type conversion:

* bool()
* complex()
* float()
* int()
* str()
* unicode()

.. index::
   single: examples; coercing vs. casting

The following example illustrates the difference between coercing traits and
casting traits::

    >>> from traits.api import HasTraits, Float, CFloat
    >>> class Person ( HasTraits ):
    ...    weight  = Float
    ...    cweight = CFloat
    >>>
    >>> bill = Person()
    >>> bill.weight  = 180    # OK, coerced to 180.0
    >>> bill.cweight = 180    # OK, cast to float(180)
    >>> bill.weight  = '180'  # Error, invalid coercion
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "c:\svn\ets3\traits\enthought\traits\trait_handlers.py", line 175,
    in error value )
    traits.trait_errors.TraitError: The 'weight' trait of a Person
    instance must be a float, but a value of '180' <type 'str'> was specified.
    >>> bill.cweight = '180'  # OK, cast to float('180')
    >>> print bill.cweight
    180.0
    >>>

.. _other-predefined-traits:

Other Predefined Traits
```````````````````````
The Traits package provides a number of other predefined traits besides those
for simple types, corresponding to other commonly used data types; these
predefined traits are listed in the following table. Refer to  the
*Traits API Reference*, in the section for the module traits.traits,
for details. Most can be used either as simple names, which use their built-in
default values, or as callables, which can take additional arguments. If the
trait cannot be used as a simple name, it is omitted from the Name column of
the table.

.. index:: Any(), Array(), Button(), Callable(), CArray(), Class(), Code()
.. index:: Color(), CSet(), Constant(), Dict()
.. index:: Directory(), Disallow, Either(), Enum()
.. index:: Event(), Expression(), false, File(), Font()
.. index:: Instance(), List(), Method(), Module()
.. index:: Password(), Property(), Python()
.. index:: PythonValue(), Range(), ReadOnly(), Regex()
.. index:: RGBColor(), Set() String(), This,
.. index:: ToolbarButton(), true, Tuple(), Type()
.. index:: undefined, UUID(), ValidatedTuple(), WeakRef()

.. _predefined-traits-beyond-simple-types-table:

.. rubric:: Predefined traits beyond simple types

+------------------+----------------------------------------------------------+
| Name             | Callable Signature                                       |
+==================+==========================================================+
| Any              | Any( [*value* = None, \*\*\ *metadata*] )                |
+------------------+----------------------------------------------------------+
| Array            | Array( [*dtype* = None, *shape* = None, *value* = None,  |
|                  | *typecode* = None, \*\*\ *metadata*] )                   |
+------------------+----------------------------------------------------------+
| ArrayOrNone      | ArrayOrNone( [*dtype* = None, *shape* = None,            |
|                  | *value* = None, *typecode* = None, \*\*\ *metadata*] )   |
+------------------+----------------------------------------------------------+
| Button           | Button( [*label* = '', *image* = None, *style* =         |
|                  | 'button', *orientation* = 'vertical', *width_padding* =  |
|                  | 7, *height_padding* = 5, \*\*\ *metadata*] )             |
+------------------+----------------------------------------------------------+
| Callable         | Callable( [*value* = None, \*\*\ *metadata*] )           |
+------------------+----------------------------------------------------------+
| CArray           | CArray( [*dtype* = None, *shape* = None, *value* = None, |
|                  | *typecode* = None, \*\*\ *metadata*] )                   |
+------------------+----------------------------------------------------------+
| Class            | Class( [*value*, \*\*\ *metadata*] )                     |
+------------------+----------------------------------------------------------+
| Code             | Code( [*value* = '', *minlen* = 0, *maxlen* = sys.maxint,|
|                  | *regex* = '', \*\*\ *metadata*] )                        |
+------------------+----------------------------------------------------------+
| Color            | Color( [\*\ *args*, \*\*\ *metadata*] )                  |
+------------------+----------------------------------------------------------+
| CSet             | CSet( [*trait* = None, *value* = None, *items* = True,   |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| n/a              | Constant( *value*[, \*\*\ *metadata*] )                  |
+------------------+----------------------------------------------------------+
| Dict, DictStrAny,| Dict( [*key_trait* = None, *value_trait* = None,         |
| DictStrBool,     | *value* = None, *items* = True, \*\*\ *metadata*] )      |
| DictStrFloat,    |                                                          |
| DictStrInt,      |                                                          |
| DictStrList,     |                                                          |
| DictStrLong,     |                                                          |
| DictStrStr       |                                                          |
+------------------+----------------------------------------------------------+
| Directory        | Directory( [*value* = '', *auto_set* = False, *entries* =|
|                  | 10, *exists* = False, \*\*\ *metadata*] )                |
+------------------+----------------------------------------------------------+
| Disallow         | n/a                                                      |
+------------------+----------------------------------------------------------+
| n/a              | Either( *val1*[, *val2*, ..., *valN*, \*\*\ *metadata*] )|
+------------------+----------------------------------------------------------+
| Enum             | Enum( *values*[, \*\*\ *metadata*] )                     |
+------------------+----------------------------------------------------------+
| Event            | Event( [*trait* = None, \*\*\ *metadata*] )              |
+------------------+----------------------------------------------------------+
| Expression       | Expression( [*value* = '0', \*\*\ *metadata*] )          |
+------------------+----------------------------------------------------------+
| false            | n/a                                                      |
+------------------+----------------------------------------------------------+
| File             | File( [*value* = '', *filter* = None, *auto_set* = False,|
|                  | *entries* = 10, *exists* = False,  \*\*\ *metadata* ] )  |
+------------------+----------------------------------------------------------+
| Font             | Font( [\*\ *args*, \*\*\ *metadata*] )                   |
+------------------+----------------------------------------------------------+
| Function         | Function( [*value* = None, \*\*\ *metadata*] )           |
+------------------+----------------------------------------------------------+
| Generic          | Generic( [*value* = None, \*\*\ *metadata*] )            |
+------------------+----------------------------------------------------------+
| generic_trait    | n/a                                                      |
+------------------+----------------------------------------------------------+
| HTML             | HTML( [*value* = '', *minlen* = 0, *maxlen* = sys.maxint,|
|                  | *regex* = '',  \*\*\ *metadata* ] )                      |
+------------------+----------------------------------------------------------+
| Instance         | Instance( [*klass* = None, *factory* = None, *args* =    |
|                  | None, *kw* = None, *allow_none* = True, *adapt* = None,  |
|                  | *module* = None, \*\*\ *metadata*] )                     |
+------------------+----------------------------------------------------------+
| List, ListBool,  | List([*trait* = None, *value* = None, *minlen* = 0,      |
| ListClass,       | *maxlen* = sys.maxint, *items* = True, \*\*\ *metadata*])|
| ListComplex,     |                                                          |
| ListFloat,       |                                                          |
| ListFunction,    |                                                          |
| ListInstance,    |                                                          |
| ListInt,         |                                                          |
| ListMethod,      |                                                          |
| ListStr,         |                                                          |
| ListThis,        |                                                          |
| ListUnicode      |                                                          |
+------------------+----------------------------------------------------------+
| Method           | Method ([\*\*\ *metadata*] )                             |
+------------------+----------------------------------------------------------+
| Module           | Module ( [\*\*\ *metadata*] )                            |
+------------------+----------------------------------------------------------+
| Password         | Password( [*value* = '', *minlen* = 0, *maxlen* =        |
|                  | sys.maxint, *regex* = '', \*\*\ *metadata*] )            |
+------------------+----------------------------------------------------------+
| Property         | Property( [*fget* = None, *fset* = None, *fvalidate* =   |
|                  | None, *force* = False, *handler* = None, *trait* = None, |
|                  | \*\* \ *metadata*] )                                     |
|                  |                                                          |
|                  | See :ref:`property-traits`, for details.                 |
+------------------+----------------------------------------------------------+
| Python           | Python ( [*value* = None, \*\*\ *metadata*] )            |
+------------------+----------------------------------------------------------+
| PythonValue      | PythonValue( [*value* = None, \*\*\ *metadata*] )        |
+------------------+----------------------------------------------------------+
| Range            | Range( [*low* = None, *high* = None, *value* = None,     |
|                  | *exclude_low* = False, *exclude_high* = False,           |
|                  | \*\ *metadata*] )                                        |
+------------------+----------------------------------------------------------+
| ReadOnly         | ReadOnly( [*value* = Undefined, \*\*\ *metadata*] )      |
+------------------+----------------------------------------------------------+
| Regex            | Regex( [*value* = '', *regex* = '.\*', \*\*\ *metadata*])|
+------------------+----------------------------------------------------------+
| RGBColor         | RGBColor( [\*\ *args*, \*\*\ *metadata*] )               |
+------------------+----------------------------------------------------------+
| self             | n/a                                                      |
+------------------+----------------------------------------------------------+
| Set              | Set( [*trait* = None, *value* = None, *items* = True,    |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| String           | String( [*value* = '', *minlen* = 0, *maxlen* =          |
|                  | sys.maxint, *regex* = '', \*\*\ *metadata*] )            |
+------------------+----------------------------------------------------------+
| This             | n/a                                                      |
+------------------+----------------------------------------------------------+
| ToolbarButton    | ToolbarButton( [*label* = '', *image* = None, *style* =  |
|                  | 'toolbar', *orientation* = 'vertical', *width_padding* = |
|                  | 2, *height_padding* = 2, \*\*\ *metadata*] )             |
+------------------+----------------------------------------------------------+
| true             | n/a                                                      |
+------------------+----------------------------------------------------------+
| Tuple            | Tuple( [\*\ *traits*, \*\*\ *metadata*] )                |
+------------------+----------------------------------------------------------+
| Type             | Type( [*value* = None, *klass* = None, *allow_none* =    |
|                  | True, \*\*\ *metadata*] )                                |
+------------------+----------------------------------------------------------+
| undefined        | n/a                                                      |
+------------------+----------------------------------------------------------+
| UStr             | UStr( [*owner*, *list_name*, *str_name*, *default_value =|
|                  | NoDefaultSpecified, \*\*\ *metadata*])                   |
+------------------+----------------------------------------------------------+
| UUID [3]_        | UUID( [\*\*\ *metadata*] )                               |
+------------------+----------------------------------------------------------+
| ValidatedTuple   | ValidatedTuple( [\*\ *traits*, *fvalidate* = None,       |
|                  | *fvalidate_info* = '' , \*\*\ *metadata*] )              |
+------------------+----------------------------------------------------------+
| WeakRef          | WeakRef( [*klass* = 'traits.HasTraits',                  |
|                  | *allow_none* = False, *adapt* = 'yes', \*\*\ *metadata*])|
+------------------+----------------------------------------------------------+

.. index:: This trait, self trait

.. _this-and-self:

This and self
:::::::::::::
A couple of predefined traits that merit special explanation are This and
**self**. They are intended for attributes whose values must be of the same
class (or a subclass) as the enclosing class. The default value of This is
None; the default value of **self** is the object containing the attribute.

.. index::
   pair: This trait; examples

The following is an example of using This::

    # this.py --- Example of This predefined trait

    from traits.api import HasTraits, This

    class Employee(HasTraits):
        manager = This

This example defines an Employee class, which has a **manager** trait
attribute, which accepts only other Employee instances as its value. It might
be more intuitive to write the following::

    # bad_self_ref.py --- Non-working example with self- referencing
    #                     class definition
    from traits.api import HasTraits, Instance
    class Employee(HasTraits):
        manager = Instance(Employee)

However, the Employee class is not fully defined at the time that the
**manager** attribute is defined. Handling this common design pattern is the
main reason for providing the This trait.

Note that if a trait attribute is defined using This on one class and is
referenced on an instance of a subclass, the This trait verifies values based
on the class on which it was defined. For example::

    >>> from traits.api import HasTraits, This
    >>> class Employee(HasTraits):
    ...    manager = This
    ...
    >>> class Executive(Employee):
    ...  pass
    ...
    >>> fred = Employee()
    >>> mary = Executive()
    >>> # The following is OK, because fred's manager can be an
    >>> # instance of Employee or any subclass.
    >>> fred.manager = mary
    >>> # This is also OK, because mary's manager can be an Employee
    >>> mary.manager = fred

.. index:: multiple values, defining trait with

.. _list-of-possibl-values:

List of Possible Values
:::::::::::::::::::::::
You can define a trait whose possible values include disparate types. To do
this, use the predefined Enum trait, and pass it a list of all possible values.
The values must all be of simple Python data types, such as strings, integers,
and floats, but they do not have to be all of the same type. This list of
values can be a typical parameter list, an explicit (bracketed) list, or a
variable whose type is list. The first item in the list is used as the default
value.

.. index:: examples; list of values

A trait defined in this fashion can accept only values that are contained in
the list of permitted values. The default value is the first value specified;
it is also a valid value for assignment.
::

    >>> from traits.api import Enum, HasTraits, Str
    >>> class InventoryItem(HasTraits):
    ...    name  = Str # String value, default is ''
    ...    stock = Enum(None, 0, 1, 2, 3, 'many')
    ...            # Enumerated list, default value is
    ...            #'None'
    ...
    >>> hats = InventoryItem()
    >>> hats.name = 'Stetson'

    >>> print '%s: %s' % (hats.name, hats.stock)
    Stetson: None

    >>> hats.stock = 2      # OK
    >>> hats.stock = 'many' # OK
    >>> hats.stock = 4      # Error, value is not in \
    >>>                     # permitted list
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "c:\svn\ets3\traits_3.0.3\enthought\traits\trait_handlers.py", line 175,
    in error value )
    traits.trait_errors.TraitError: The 'stock' trait of an InventoryItem
    instance must be None or 0 or 1 or 2 or 3 or 'many', but a value of 4 <type
    'int'> was specified.

This example defines an InventoryItem class, with two trait attributes,
**name**, and **stock**. The name attribute is simply a string. The **stock**
attribute has an initial value of None, and can be assigned the values None, 0,
1, 2, 3, and 'many'. The example then creates an instance of the InventoryItem
class named **hats**, and assigns values to its attributes.

.. index:: metadata attributes; on traits

.. _trait-metadata:

Trait Metadata
--------------
Trait objects can contain metadata attributes, which fall into three categories:

* Internal attributes, which you can query but not set.
* Recognized attributes, which you can set to determine the behavior of the
  trait.
* Arbitrary attributes, which you can use for your own purposes.

You can specify values for recognized or arbitrary metadata attributes by
passing them as keyword arguments to callable traits. The value of each
keyword argument becomes bound to the resulting trait object as the value
of an attribute having the same name as the keyword.

.. index:: metadata attributes; internal

.. _internal-metadata-attributes:

Internal Metadata Attributes
````````````````````````````
The following metadata attributes are used internally by the Traits package,
and can be queried:

.. index:: array metadata attribute, default metadata attribute
.. index:: default_kind metadata attribute, delegate; metadata attribute
.. index:: inner_traits metadata attribute, parent metadata attribute
.. index:: prefix metadata attribute, trait_type metadata attribute
.. index:: type metadata attribute

* **array**: Indicates whether the trait is an array.
* **default**: Returns the default value for the trait, if known; otherwise it
  returns Undefined.
* **default_kind**: Returns a string describing the type of value returned by
  the default attribute for the trait. The possible values are:

  * ``value``: The default attribute returns the actual default value.
  * ``list``: A copy of the list default value.
  * ``dict``: A copy of the dictionary default value.
  * ``self``: The default value is the object the trait is bound to; the
    **default** attribute returns Undefined.
  * ``factory``: The default value is created by calling a factory; the
    **default** attribute returns Undefined.
  * ``method``: The default value is created by calling a method on the object
    the trait is bound to; the **default** attribute returns Undefined.

* **delegate**: The name of the attribute on this object that references the
  object that this object delegates to.
* **inner_traits**: Returns a tuple containing the "inner" traits
  for the trait. For most traits, this is empty, but for List and Dict traits,
  it contains the traits that define the items in the list or the keys and
  values in the dictionary.
* **parent**: The trait from which this one is derived.
* **prefix**: A prefix or substitution applied to the delegate attribute.
  See :ref:`deferring-traits` for details.
* **trait_type**: Returns the type of the trait, which is typically a handler
  derived from TraitType.
* **type**: One of the following, depending on the nature of the trait:

  * ``constant``
  * ``delegate``
  * ``event``
  * ``property``
  * ``trait``

.. index:: recognized metadata attributes, metadata attributes; recognized

.. _recognized-metadata-attributes:

Recognized Metadata Attributes
``````````````````````````````
The following metadata attributes are not predefined, but are recognized by
HasTraits objects:

.. index:: desc metadata attribute, editor metadata attribute, TraitValue class
.. index:: label; metadata attribute, rich_compare metadata attribute
.. index:: trait_value metadata attribute, transient metadata attribute

* **desc**: A string describing the intended meaning of the trait. It is used
  in exception messages and fly-over help in user interface trait editors.
* **editor**: Specifies an instance of a subclass of TraitEditor to use when
  creating a user interface editor for the trait. Refer to the
  `TraitsUI User Manual
  <http://docs.enthought.com/traitsui/traitsui_user_manual/index.html>`_
  for more information on trait editors.
* **label**: A string providing a human-readable name for the trait. It is
  used to label trait attribute values in user interface trait editors.
* **rich_compare**: A Boolean indicating whether the basis for considering a
  trait attribute value to have changed is a "rich" comparison (True, the
  default), or simple object identity (False). This attribute can be useful
  in cases where a detailed comparison of two objects is very expensive, or
  where you do not care if the details of an object change, as long as the
  same object is used.
* **trait_value**: A Boolean indicating whether the trait attribute accepts
  values that are instances of TraitValue. The default is False. The TraitValue
  class provides a mechanism for dynamically modifying trait definitions. See
  the *Traits API Reference* for details on TraitValue. If **trait_value** is
  True, then setting the trait attribute to TraitValue(), with no arguments,
  resets the attribute to it original default value.
* **transient**: A Boolean indicating that the trait value is not persisted
  when the object containing it is persisted. The default value for most
  predefined traits is False (the value will be persisted if its container is).
  You can set it to True for traits whose values you know you do not want to
  persist. Do not set it to True on traits where it is set internally to
  False, as doing so is likely to create unintended consequences. See
  :ref:`persistence` for more information.

Other metadata attributes may be recognized by specific predefined traits.

.. index:: metadata attributes; accessing

.. _accessing-metadata-attributes:

Accessing Metadata Attributes
`````````````````````````````
.. index::
   pair: examples; metadata attributes

Here is an example of setting trait metadata using keyword arguments::

    # keywords.py --- Example of trait keywords
    from traits.api import HasTraits, Str

    class Person(HasTraits):
        first_name = Str('',
                         desc='first or personal name',
                         label='First Name')
        last_name =  Str('',
                         desc='last or family name',
                         label='Last Name')

In this example, in a user interface editor for a Person object, the labels
"First Name" and "Last Name" would be used for entry
fields corresponding to the **first_name** and **last_name** trait attributes.
If the user interface editor supports rollover tips, then the **first_name**
field would display "first or personal name" when the user moves
the mouse over it; the last_name field would display "last or family
name" when moused over.

To get the value of a trait metadata attribute, you can use the trait() method
on a HasTraits object to get a reference to a specific trait, and then access
the metadata attribute::

    # metadata.py --- Example of accessing trait metadata attributes
    from traits.api import HasTraits, Int, List, Float, \
                                     Instance, Any, TraitType

    class Foo( HasTraits ): pass

    class Test( HasTraits ):
        i = Int(99)
        lf = List(Float)
        foo = Instance( Foo, () )
        any = Any( [1, 2, 3 ] )

    t = Test()

    print t.trait( 'i' ).default                      # 99
    print t.trait( 'i' ).default_kind                 # value
    print t.trait( 'i' ).inner_traits                 # ()
    print t.trait( 'i' ).is_trait_type( Int )         # True
    print t.trait( 'i' ).is_trait_type( Float )       # False

    print t.trait( 'lf' ).default                     # []
    print t.trait( 'lf' ).default_kind                # list
    print t.trait( 'lf' ).inner_traits
             # (<traits.traits.CTrait object at 0x01B24138>,)
    print t.trait( 'lf' ).is_trait_type( List )       # True
    print t.trait( 'lf' ).is_trait_type( TraitType )  # True
    print t.trait( 'lf' ).is_trait_type( Float )      # False
    print t.trait( 'lf' ).inner_traits[0].is_trait_type( Float ) # True

    print t.trait( 'foo' ).default                    # <undefined>
    print t.trait( 'foo' ).default_kind               # factory
    print t.trait( 'foo' ).inner_traits               # ()
    print t.trait( 'foo' ).is_trait_type( Instance )  # True
    print t.trait( 'foo' ).is_trait_type( List  )     # False

    print t.trait( 'any' ).default                    # [1, 2, 3]
    print t.trait( 'any' ).default_kind               # list
    print t.trait( 'any' ).inner_traits               # ()
    print t.trait( 'any' ).is_trait_type( Any )       # True
    print t.trait( 'any' ).is_trait_type( List )      # False

.. rubric:: Footnotes
.. [2] Most callable predefined traits are classes, but a few are functions.
       The distinction does not make a difference unless you are trying to
       extend an existing predefined trait. See the *Traits API Reference* for
       details on particular traits, and see Chapter 5 for details on extending
       existing traits.
.. [3] Available in Python 2.5.
