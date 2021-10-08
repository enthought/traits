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
Python type **float**. The value 150.0 specifies the default value of the
trait.

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
        ...
    traits.trait_errors.TraitError: The 'weight' trait of a Person instance
    must be a float, but a value of 'average' <type 'str'> was specified.

In this example, **joe** is an instance of the Person class defined in the
previous example. The **joe** object has an instance attribute **weight**,
whose initial value is the default value of the Person.weight trait (150.0),
and whose assignment is governed by the Person.weight trait's validation
rules. Assigning an integer to **weight** is acceptable because there is no
loss of precision (but assigning a float to an Int trait would cause an error).

The Traits package allows creation of a wide variety of trait types, ranging
from very simple to very sophisticated. The following section presents some of
the simpler, more commonly used forms.

.. warning:: Unless otherwise stated as safe to do so, avoid naming
   attributes with the prefix 'trait' or '_trait'. This avoids overshadowing
   existing methods on HasTraits.


A note about the Traits package structure
-----------------------------------------

We described above how trait type definitions and the :class:`~.HasTraits`
class can be imported from the ``traits.api`` module. For example::

    from traits.api import Float, HasTraits, Int

In fact, the :class:`HasTraits` class and various trait type classes are
defined in other modules nested inside the Traits package structure, but
they're re-imported to ``traits.api`` for user convenience. In general,
everything you need should be available in either ``traits.api`` or one of the
other ``*.api`` modules inside the package structure (for example,
``traits.adaptation.api`` or ``traits.observation.api``). As a matter of best
practices, you should import the things you need directly from one of these
``*.api`` modules. If you discover that there's something that you need that's
not available from one of these modules, please discuss with the Traits
development team (for example, by opening an issue on the `Traits bug
tracker`_).


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
   pair: type; string
.. index:: Boolean type, Bool trait, CBool trait, Complex trait, CComplex trait
.. index:: Float trait, CFloat trait, Int trait, CInt trait
.. index:: integer type, floating point number type, complex number type
.. index:: Str trait, CStr trait, Bytes trait, CBytes trait

.. _predefined-defaults-for-simple-types-table:

.. rubric:: Predefined defaults for simple types

============== ============= ====================== ======================
Coercing Trait Casting Trait Python Type            Built-in Default Value
============== ============= ====================== ======================
Bool           CBool         Boolean                False
Complex        CComplex      Complex number         0+0j
Float          CFloat        Floating point number  0.0
Int            CInt          Integer                0
Str            CStr          String                 ''
Bytes          CBytes        Bytes                  b''
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
Complex       Floating point number, integer
Float         Integer
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
* bytes()

.. index::
   single: examples; coercing vs. casting

The following example illustrates the difference between coercing traits and
casting traits::

    >>> from traits.api import HasTraits, Float, CFloat
    >>> class Person ( HasTraits ):
    ...    weight  = Float
    ...    cweight = CFloat
    ...
    >>> bill = Person()
    >>> bill.weight  = 180    # OK, coerced to 180.0
    >>> bill.cweight = 180    # OK, cast to float(180)
    >>> bill.weight  = '180'  # Error, invalid coercion
    Traceback (most recent call last):
        ...
    traits.trait_errors.TraitError: The 'weight' trait of a Person instance
    must be a float, but a value of '180' <type 'str'> was specified.
    >>> bill.cweight = '180'  # OK, cast to float('180')
    >>> print(bill.cweight)
    180.0


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

.. index:: Any(), Array(), Button(), Callable(), CArray(), Code()
.. index:: CSet(), Constant(), Dict()
.. index:: Directory(), Disallow, Either(), Enum()
.. index:: Event(), Expression(), false, File()
.. index:: Instance(), List(), Method(), Module()
.. index:: Password(), Property(), Python()
.. index:: PythonValue(), Range(), ReadOnly(), Regex()
.. index:: Set() String(), This,
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
| Code             | Code( [*value* = '', *minlen* = 0,                       |
|                  | *maxlen* = sys.maxsize, *regex* = '',                    |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| CSet             | CSet( [*trait* = None, *value* = None, *items* = True,   |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| Constant         | Constant( *value*\ [, \*\*\ *metadata*] )                |
+------------------+----------------------------------------------------------+
| Dict             | Dict( [*key_trait* = None, *value_trait* = None,         |
|                  | *value* = None, *items* = True, \*\*\ *metadata*] )      |
+------------------+----------------------------------------------------------+
| Directory        | Directory( [*value* = '', *auto_set* = False, *entries* =|
|                  | 10, *exists* = False, \*\*\ *metadata*] )                |
+------------------+----------------------------------------------------------+
| Disallow         | n/a                                                      |
+------------------+----------------------------------------------------------+
| Either           | Either( *val1*\ [, *val2*, ..., *valN*,                  |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| Enum             | Enum( *values*\ [, \*\*\ *metadata*] )                   |
+------------------+----------------------------------------------------------+
| Event            | Event( [*trait* = None, \*\*\ *metadata*] )              |
+------------------+----------------------------------------------------------+
| Expression       | Expression( [*value* = '0', \*\*\ *metadata*] )          |
+------------------+----------------------------------------------------------+
| File             | File( [*value* = '', *filter* = None, *auto_set* = False,|
|                  | *entries* = 10, *exists* = False,  \*\*\ *metadata* ] )  |
+------------------+----------------------------------------------------------+
| Function [3]_    | Function( [*value* = None, \*\*\ *metadata*] )           |
+------------------+----------------------------------------------------------+
| generic_trait    | n/a                                                      |
+------------------+----------------------------------------------------------+
| HTML             | HTML( [*value* = '', *minlen* = 0,                       |
|                  | *maxlen* = sys.maxsize, *regex* = '',                    |
|                  | \*\*\ *metadata* ] )                                     |
+------------------+----------------------------------------------------------+
| Instance         | Instance( [*klass* = None, *factory* = None, *args* =    |
|                  | None, *kw* = None, *allow_none* = True, *adapt* = None,  |
|                  | *module* = None, \*\*\ *metadata*] )                     |
+------------------+----------------------------------------------------------+
| List             | List( [*trait* = None, *value* = None, *minlen* = 0,     |
|                  | *maxlen* = sys.maxsize, *items* = True,                  |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| Map              | Map( *map*\ [, \*\*\ *metadata*] )                       |
+------------------+----------------------------------------------------------+
| Method [3]_      | Method ([\*\*\ *metadata*] )                             |
+------------------+----------------------------------------------------------+
| Module           | Module ( [\*\*\ *metadata*] )                            |
+------------------+----------------------------------------------------------+
| Password         | Password( [*value* = '', *minlen* = 0, *maxlen* =        |
|                  | sys.maxsize, *regex* = '', \*\*\ *metadata*] )           |
+------------------+----------------------------------------------------------+
| PrefixList       | PrefixList( *values*\ [, \*\*\ *metadata*] )             |
+------------------+----------------------------------------------------------+
| PrefixMap        | PrefixMap( *map*\ [, \*\*\ *metadata*] )                 |
+------------------+----------------------------------------------------------+
| Property         | Property( [*fget* = None, *fset* = None, *fvalidate* =   |
|                  | None, *force* = False, *handler* = None, *trait* = None, |
|                  | \*\*\ *metadata*] )                                      |
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
| self             | n/a                                                      |
+------------------+----------------------------------------------------------+
| Set              | Set( [*trait* = None, *value* = None, *items* = True,    |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| String           | String( [*value* = '', *minlen* = 0, *maxlen* =          |
|                  | sys.maxsize, *regex* = '', \*\*\ *metadata*] )           |
+------------------+----------------------------------------------------------+
| Subclass         | Subclass( [*value* = None, *klass* = None, *allow_none* =|
|                  | True, \*\*\ *metadata*] )                                |
+------------------+----------------------------------------------------------+
| This             | n/a                                                      |
+------------------+----------------------------------------------------------+
| ToolbarButton    | ToolbarButton( [*label* = '', *image* = None, *style* =  |
|                  | 'toolbar', *orientation* = 'vertical', *width_padding* = |
|                  | 2, *height_padding* = 2, \*\*\ *metadata*] )             |
+------------------+----------------------------------------------------------+
| Tuple            | Tuple( [\*\ *traits*, \*\*\ *metadata*] )                |
+------------------+----------------------------------------------------------+
| Type             | Type( [*value* = None, *klass* = None, *allow_none* =    |
|                  | True, \*\*\ *metadata*] )                                |
+------------------+----------------------------------------------------------+
| Union            | Union( *val1*\ [, *val2*, ..., *valN*,                   |
|                  | \*\*\ *metadata*] )                                      |
+------------------+----------------------------------------------------------+
| UUID [4]_        | UUID( [\*\*\ *metadata*] )                               |
+------------------+----------------------------------------------------------+
| ValidatedTuple   | ValidatedTuple( [\*\ *traits*, *fvalidate* = None,       |
|                  | *fvalidate_info* = '' , \*\*\ *metadata*] )              |
+------------------+----------------------------------------------------------+
| WeakRef          | WeakRef( [*klass* = 'traits.HasTraits',                  |
|                  | *allow_none* = False, *adapt* = 'yes', \*\*\ *metadata*])|
+------------------+----------------------------------------------------------+

.. index:: Instance trait

.. _instance:

Instance
::::::::
One of the most fundamental and useful predefined trait types is
:class:`~.Instance`. Instance trait values are an instance of a particular class
or its subclasses, as specified by the **klass** argument. **klass** can be
either an instance of a class or a class itself (note this applies to all python
classes, not necessarily just :class:`~.HasTraits` subclasses).  However, one should
typically provide the type or interface they want an instance of, instead of
providing an instance of a class.

If **klass** is an instance or if it is a class and **args** and **kw** are not
specified, the default value is ``None``. Otherwise, the default value is
obtained by calling the callable **factory** argument (or **klass** if
**factory** is None) with **args** and **kw**. Further, there is the
**allow_none** argument which dictates whether the trait can take on a value of
``None``. However, this does not include the default value for the trait. For
example::

    # instance_trait_defaults.py --- Example of Instance trait default values
    from traits.api import HasTraits, Instance

    class Parent(HasTraits):
        pass

    class Child(HasTraits):
        # default value is None
        father = Instance(Parent)
        # default value is still None, but None can not be assigned
        grandfather = Instance(Parent, allow_none=False)
        # default value is Parent()
        mother = Instance(Parent, args=())

In the last case, the default ``Parent`` instance is not immediately
created, but rather is lazily instantiated when the trait is first accessed.
The default ``Parent`` will also be instantiated if the trait is assigned to
and there is a change handler defined on the trait (to detect changes from the
default value). For more details on change handlers and trait notification see
:ref:`observe-notification`.

Somewhat surprisingly, ``mother = Instance(Parent, ())`` will also yield a
default value of ``Parent()``, even though in that case it is **factory** that
is ``()`` not **args**.  This is a result of implementation details, however
the recommended way of writing this code is to explicitly pass **args** by
keyword like so ``mother = Instance(Parent, args=())``. Another common mistake
is passing in another trait type to Instance. For example,
``some_trait = Instance(Int)``. This will likely lead to unexpected behavior
and potential errors. Instead simply do ``some_trait = Int()``.

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

.. index:: Map trait

.. _map:

Map
:::
The map trait ensures that the value assigned to a trait attribute
is a key of a specified dictionary, and also assigns the dictionary
value corresponding to that key to a shadow attribute.

.. index::
   pair: Map trait; examples

The following is an example of using Map::

    # map.py --- Example of Map predefined trait

    from traits.api import HasTraits, Map

    class Person(HasTraits):
        married = Map({'yes': 1, 'no': 0 }, default_value="yes")

This example defines a Person class which has a **married** trait
attribute which accepts values "yes" and "no". The default value
is set to "yes". The name of the shadow attribute is the name of
the Map attribute followed by an underscore, i.e ``married_``
Instantiating the class produces the following::

    >>> from traits.api import HasTraits, Map
    >>> bob = Person()
    >>> print(bob.married)
    yes
    >>> print(bob.married_)
    1

.. index:: PrefixMap trait

.. _prefixmap:

PrefixMap
:::::::::
Like Map, PrefixMap is created using a dictionary, but in this
case, the keys of the dictionary must be strings. Like PrefixList,
a string *v* is a valid value for the trait attribute if it is a prefix of
one and only one key *k* in the dictionary. The actual values assigned to
the trait attribute is *k*, and its corresponding mapped attribute is map[*k*].

.. index::
   pair: PrefixMap trait; examples

The following is an example of using PrefixMap::

    # prefixmap.py --- Example of PrefixMap predefined trait

    from traits.api import HasTraits, PrefixMap

    class Person(HasTraits):
        married = PrefixMap({'yes': 1, 'no': 0 }, default_value="yes")

This example defines a Person class which has a **married** trait
attribute which accepts values "yes" and "no" or any unique
prefix. The default value is set to "yes". The name of the shadow attribute
is the name of the PrefixMap attribute followed by an underscore, i.e ``married_``
Instantiating the class produces the following::

    >>> bob = Person()
    >>> print(bob.married)
    yes
    >>> print(bob.married_)
    1
    >>> bob.married = "n" # Setting a prefix
    >>> print(bob.married)
    no
    >>> print(bob.married_)
    0

.. index:: PrefixList trait

.. _prefixlist:

PrefixList
::::::::::
Ensures that a value assigned to the attribute is a member of a list of
specified string values, or is a unique prefix of one of those values.
The values that can be assigned to a trait attribute of type PrefixList
is the set of all strings supplied to the PrefixList constructor, as well
as any unique prefix of those strings. The actual value assigned to the
trait is limited to the set of complete strings assigned to the
PrefixList constructor.

.. index::
   pair: PrefixList trait; examples

The following is an example of using PrefixList::

    # prefixlist.py --- Example of PrefixList predefined trait

    from traits.api import HasTraits, PrefixList

    class Person(HasTraits):
        married = PrefixList(["yes", "no"])

This example defines a Person class which has a **married** trait
attribute which accepts values "yes" and "no" or any unique
prefix. Instantiating the class produces the following::

    >>> bob = Person()
    >>> print(bob.married)
    yes
    >>> bob.married = "n" # Setting a prefix
    >>> print(bob.married)
    no

.. index:: Either trait

.. _either:

Either
::::::
Another predefined trait that merits special explanation is Either. The
Either trait is intended for attributes that may take a value of more than
a single trait type, including None. The default value of Either is None, even
if None is not one of the types the user explicitly defines in the constructor,
but a different default value can be provided using the ``default`` argument.

.. index::
   pair: Either trait; examples

The following is an example of using Either::

    # either.py --- Example of Either predefined trait

    from traits.api import HasTraits, Either, Str

    class Employee(HasTraits):
        manager_name = Either(Str, None)

This example defines an Employee class, which has a **manager_name** trait
attribute, which accepts either an Str instance or None as its value, and
will raise a TraitError if a value of any other type is assigned. For example::

    >>> from traits.api import HasTraits, Either, Str
    >>> class Employee(HasTraits):
    ...     manager_name = Either(Str, None)
    ...
    >>> steven = Employee(manager_name="Jenni")
    >>> # Here steven's manager is named "Jenni"
    >>> steven.manager_name
    'Jenni'
    >>> eric = Employee(manager_name=None)
    >>> # Eric is the boss, so he has no manager.
    >>> eric.manager_name is None
    True
    >>> # Assigning a value that is neither a string nor None will fail.
    >>> steven.manager_name = 5
    traits.trait_errors.TraitError: The 'manager_name' trait of an Employee instance must be a string or None, but a value of 5 <type 'int'> was specified.

.. index:: Union trait

.. _union:

Union
::::::
The Union trait accepts a value that is considered valid by at least one
of the traits in its definition. It is a simpler and therefore less error-prone
alternative to the `Either` trait, which allows more complex constructs and
may sometimes exhibit mysterious validation behaviour. The Union trait however,
validates the value assigned to it against each of the traits in its definition
in the order they are defined. Union only accepts trait types or trait type
instances or None in its definition. Prefer to use Union over `Either` to
remain future proof.

.. index::
   pair: Union trait; examples

The following is an example of using Union::

    # union.py --- Example of Union predefined trait

    from traits.api import HasTraits, Union, Int, Float, Instance

    class Salary(HasTraits):
        basic = Float
        bonus = Float

    class Employee(HasTraits):
        manager_name = Union(Str, None)
        pay = Union(Instance(Salary), Float)

This example defines an Employee class, which has a **manager_name** trait
attribute, which accepts either an Str instance or None as its value, a
**salary** trait that accepts an instance of Salary or Float and will raise a
TraitError if a value of any other type is assigned. For example::

    >>> from traits.api import HasTraits, Either, Str
    >>> class Employee(HasTraits):
    ...     manager_name = Union(Str, None)
    ...
    >>> steven = Employee(manager_name="Jenni")
    >>> # Here steven's manager is named "Jenni"
    >>> # Assigning a value that is neither a string nor None will fail.
    >>> steven.manager_name = 5
    traits.trait_errors.TraitError: The 'manager_name' trait of an Employee instance must be a string or a None type, but a value of 5 <class 'int'> was specified.

The following example illustrates the difference between `Either` and `Union`::

    >>> from traits.api import HasTraits, Either, Union, Str
    >>> class IntegerClass(HasTraits):
    ...     primes = Either([2], None, {'3':6}, 5, 7, 11)
    ...
    >>> i = IntegerClass(primes=2) # Acceptable value, no error
    >>> i = IntegerClass(primes=4)
    traits.trait_errors.TraitError: The 'primes' trait of an IntegerClass instance must be 2 or None or 5 or 7 or 11 or '3', but a value of 4 <class 'int'> was specified.
    >>>
    >>> # But Union does not allow such declarations.
    >>> class IntegerClass(HasTraits):
    ...     primes = Union([2], None, {'3':6}, 5, 7, 11)
    ValueError: Union trait declaration expects a trait type or an instance of trait type or None, but got [2] instead


.. _migration_either_to_union:

.. rubric:: Migration from Either to Union

* Static default values are defined on Union via the **default_value**
  attribute, whereas Either uses the **default** attribute. The naming of
  **default_value** is consistent with other trait types.
  For example::

      Either(None, Str(), default="unknown")

  would be changed to::

      Union(None, Str(), default_value="unknown")

* If a default value is not defined, Union uses the default value from the
  first trait in its definition, whereas Either uses None.

  For example::

      Either(Int(), Float())

  has a default value of None. However None is not one of the allowed values.
  If the trait is later set to None from a non-None value, a validation error
  will occur.

  If the trait definition is changed to::

      Union(Int(), Float())

  Then the default value will be 0, which is the default value of the first
  trait.

  To keep None as the default, use None as the first item::

      Union(None, Int(), Float())

  With this, None also becomes one of the allowed values.

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

    >>> print('%s: %s' % (hats.name, hats.stock))
    Stetson: None

    >>> hats.stock = 2      # OK
    >>> hats.stock = 'many' # OK
    >>> hats.stock = 4      # Error, value is not in \
    >>>                     # permitted list
    Traceback (most recent call last):
        ...
    traits.trait_errors.TraitError: The 'stock' trait of an InventoryItem
    instance must be None or 0 or 1 or 2 or 3 or 'many', but a value of 4
    <type 'int'> was specified.


This defines an :py:class:`InventoryItem` class, with two trait attributes,
**name**, and **stock**. The name attribute is simply a string. The **stock**
attribute has an initial value of None, and can be assigned the values None, 0,
1, 2, 3, and 'many'. The example then creates an instance of the InventoryItem
class named **hats**, and assigns values to its attributes.

When the list of possible values can change during the lifetime of the object,
one can specify **another trait** that holds the list of possible values::

    >>> from traits.api import Enum, HasTraits, List
    >>> class InventoryItem(HasTraits):
    ...    possible_stock_states = List([None, 0, 1, 2, 3, 'many'])
    ...    stock = Enum(0, values="possible_stock_states")
    ...            # Enumerated list, default value is 0. The list of
    ...            # allowed values is whatever possible_stock_states holds
    ...

    >>> hats = InventoryItem()
    >>> hats.stock
    0
    >>> hats.stock = 2      # OK
    >>> hats.stock = 4      # TraitError like above
    Traceback (most recent call last):
        ...
    traits.trait_errors.TraitError: The 'stock' trait of an InventoryItem
    instance must be None or 0 or 1 or 2 or 3 or 'many', but a value of 4
    <type 'int'> was specified.

    >>> hats.possible_stock_states.append(4)  # Add 4 to list of allowed values
    >>> hats.stock = 4      # OK


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

.. index:: desc metadata attribute, editor metadata attribute
.. index:: label; metadata attribute, comparison_mode metadata attribute
.. index:: transient metadata attribute

* **desc**: A string describing the intended meaning of the trait. It is used
  in exception messages and fly-over help in user interface trait editors.
* **editor**: Specifies an instance of a subclass of TraitEditor to use when
  creating a user interface editor for the trait. Refer to the
  `TraitsUI User Manual
  <http://docs.enthought.com/traitsui/traitsui_user_manual/index.html>`_
  for more information on trait editors.
* **label**: A string providing a human-readable name for the trait. It is
  used to label trait attribute values in user interface trait editors.
* **comparison_mode**: Indicates when trait change notifications should be
  generated based upon the result of comparing the old and new values of a
  trait assignment. This should be a member of the
  :class:`~traits.constants.ComparisonMode` enumeration class.
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

    print(t.trait( 'i' ).default)                      # 99
    print(t.trait( 'i' ).default_kind)                 # value
    print(t.trait( 'i' ).inner_traits)                 # ()
    print(t.trait( 'i' ).is_trait_type( Int ))         # True
    print(t.trait( 'i' ).is_trait_type( Float ))       # False

    print(t.trait( 'lf' ).default)                     # []
    print(t.trait( 'lf' ).default_kind)                # list
    print(t.trait( 'lf' ).inner_traits)
             # (<traits.traits.CTrait object at 0x01B24138>,)
    print(t.trait( 'lf' ).is_trait_type( List ))       # True
    print(t.trait( 'lf' ).is_trait_type( TraitType ))  # True
    print(t.trait( 'lf' ).is_trait_type( Float ))      # False
    print(t.trait( 'lf' ).inner_traits[0].is_trait_type( Float )) # True

    print(t.trait( 'foo' ).default)                    # <undefined>
    print(t.trait( 'foo' ).default_kind)               # factory
    print(t.trait( 'foo' ).inner_traits)               # ()
    print(t.trait( 'foo' ).is_trait_type( Instance ))  # True
    print(t.trait( 'foo' ).is_trait_type( List  ))     # False

    print(t.trait( 'any' ).default)                    # [1, 2, 3]
    print(t.trait( 'any' ).default_kind)               # list
    print(t.trait( 'any' ).inner_traits)               # ()
    print(t.trait( 'any' ).is_trait_type( Any ))       # True
    print(t.trait( 'any' ).is_trait_type( List ))      # False

.. rubric:: Footnotes
.. [2] Most callable predefined traits are classes, but a few are functions.
       The distinction does not make a difference unless you are trying to
       extend an existing predefined trait. See the *Traits API Reference* for
       details on particular traits, and see Chapter 5 for details on extending
       existing traits.
.. [3] The Function and Method trait types are now deprecated. See |Function|,
       |Method|
.. [4] Available in Python 2.5.

..
   external urls

.. _Traits bug tracker: https://github.com/enthought/traits/issues

..
   # substitutions

.. |Function| replace:: :class:`~traits.trait_types.Function`
.. |Method| replace:: :class:`~traits.trait_types.Method`
