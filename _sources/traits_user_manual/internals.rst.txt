.. index:: internals

Traits internals
================

This section of the documentation is intended both for those developing Traits
itself, and for those using Traits who would like a better understanding of
the Traits internals.


Fundamentals
------------

The runtime behavior of Traits is governed by two key classes: |CTrait| and
|HasTraits|. Each of these classes inherits from a superclass implemented in
the |ctraits| C extension module: |CTrait| inherits from |cTrait|, while
|HasTraits| inherits from |CHasTraits|.

The |CHasTraits| and |cTrait| base classes are not intended for direct use and
do not provide a complete, coherent API: that API is provided by their
respective subclasses |HasTraits| and |CTrait|. The existence and precise
semantics of the base classes should be regarded as implementation details.
In what follows, we'll frequently refer to behavior of |HasTraits| and |CTrait|
even when the behavior we're referring to is actually implemented by
|CHasTraits| or |cTrait|.

We'll examine both of these classes, along with some of their hidden state, in
more detail below.


Key class: |HasTraits|
~~~~~~~~~~~~~~~~~~~~~~

The primary purpose of the |HasTraits| class is to override Python's normal
rules for attribute access. It does this by overriding the
``__getattribute__``, ``__setattr__`` and ``__delattr__`` special methods. At C
level, this is done through providing ``tp_getattro`` and ``tp_setattro``
"slots" to the |CHasTraits| ``PyTypeObject``: ``tp_getattro`` controls
attribute retrieval operations, while ``tp_setattro`` is called for both
attribute set and attribute deletion operations.

To support trait get and set operations, a |HasTraits| object (that is, in
normal use, an instance of a user-defined subclass of |HasTraits|) has two key
pieces of state: a dictionary of **class traits**, and a second dictionary of
**instance traits**. Each dictionary is a mapping from trait attribute names to
|CTrait| objects. A |CTrait| object encapsulates the rules for getting and
setting the corresponding attribute, as well as providing an attachment point
for trait notifications.

In addition to these two dictionaries, a |HasTraits| object has a ``__dict__``
that stores attribute values for that object in the normal way.

Analogously to class variables and instance variables in a normal Python class,
the class traits dictionary for a given |HasTraits| subclass is shared between
instances of that class, while the instance traits dictionary is specific to a
particular |HasTraits| instance. (As an internal optimization, the instance
traits dictionary is created on demand when first needed, while the class
traits dictionary is always present for each instance.)

For introspection and debugging purposes, both of these dictionaries can
be retrieved directly, using the |_instance_traits| and |_class_traits|
methods. However, it's not recommended to use either of these methods in
production code, and you should be especially careful when modifying either
of these dictionaries.

For example, consider the following |HasTraits| subclass::

    from traits.api import Float, HasTraits, Str

    class Ingredient(HasTraits):
        """ An ingredient in a recipe listing. """

        #: The name of the ingredient.
        name = Str()

        #: Ingredient quantity.
        quantity = Float()

Here's what happens when we create an instance of this ingredient and inspect
the instance and class trait dictionaries::

    >>> eggs = Ingredient(name="eggs", quantity=12)
    >>> eggs._instance_traits()
    {}
    >>> eggs._class_traits()
    {
        'name': <traits.ctrait.CTrait object at 0x1020cd400>,
        'quantity': <traits.ctrait.CTrait object at 0x1020cd360>,
        'trait_added': <traits.ctrait.CTrait object at 0x1020cd4a0>,
        'trait_modified': <traits.ctrait.CTrait object at 0x1020079a0>,
    }
    >>> eggs.__dict__
    {'name': 'eggs', 'quantity': 12.0}

Note that the actual values for the ingredient are stored in the ``__dict__``
as usual, not in the ``CTrait`` objects.

If we create a second ingredient, it shares class traits (but not
instance traits) with the first one::

    >>> flour = Ingredient(name="flour", quantity=3.5)
    >>> flour._class_traits() is eggs._class_traits()
    True
    >>> flour._instance_traits() is eggs._instance_traits()
    False


Key class: |CTrait|
~~~~~~~~~~~~~~~~~~~

A |CTrait| object has two main purposes:

- It encapsulates the rules for getting and setting a traited attribute on
  a |HasTraits| object.
- It provides an attachment point for trait notifiers.

The hidden state for a |CTrait| instance is encapsulated in the
``trait_object`` C ``struct`` in the |ctraits| source. There are several
interesting fields, not all of which are exposed at Python level.

Of particular interest are the ``getattr`` and ``setattr`` fields, which
hold pointers to C functions that act as the entry points for attribute
access via the given trait. See below for a fuller description of attribute
access mechanics.


Attribute retrieval
~~~~~~~~~~~~~~~~~~~

When evaluating ``obj.name`` for a ``HasTraits`` object ``obj``, the following
sequence of steps occurs (see ``has_traits_getattro`` in the C source):

- The ``name`` is looked up in ``obj.__dict__``. If found, the corresponding
  value is returned immediately.
- If ``name`` is not found in ``obj.__dict__``, we look first for an instance
  trait named ``name``, and then for a class trait named ``name``. Thus an
  instance trait with a given name will shadow a class trait with the same
  name.
- If a matching trait is found, its ``getattr`` field is invoked to retrieve
  the trait's value for the given object.
- If no matching trait is found, we try to access the attribute value
  using Python's usual attribute rules (via the ``PyObject_GenericGetAttr``
  C-API call).
- Finally, if the ``PyObject_GenericGetAttr`` call fails, we invoke the
  **prefix trait** machinery to get a new ``CTrait`` object, and use that
  new trait to get a value.

Note that the above sequence of steps applies to method access as well as
attribute access. Note also that there's no mechanism to automatically
search for ``CTrait`` objects in superclasses of the immediate ``HasTraits``
subclass.


Attribute set operations
~~~~~~~~~~~~~~~~~~~~~~~~

The rules for setting an attribute (evaluating ``obj.name = value`` for a
``HasTraits`` object ``obj``) are analogous to those for attribute retrieval.
The starting point is ``has_traits_setattro`` in the source.

- First we look for the name ``name`` in ``obj._instance_traits()``,
  and retrieve the corresponding ``CTrait`` instance if present.
- If no matching entry is found, we then look up ``name`` in
  ``obj._class_traits()``, and again retrieve the corresponding ``CTrait``.
- If still not found, we invoke the **prefix trait** machinery to get a new
  ``CTrait`` object. By default, this goes through the
  ``HasTraits.__prefix_trait__`` method (which is implemented in Python), and
  this may still fail with an exception.
- If one of the above steps succeeded, we now have a ``CTrait`` object, and
  its ``setattr`` function is invoked (passing along the trait object, ``obj``,
  ``name`` and ``value``) to perform the actual attribute set operation.


Attribute deletion
~~~~~~~~~~~~~~~~~~

Attribute deletion (``del obj.name``) goes through the same code path as
attribute set operations. Most ``CTrait`` types do not permit deletion.

Traits Containers
-----------------

Traits has the ability to watch for changes in standard Python containers:
lists, dictionaries and sets.  To achieve this Traits provides special
subclasses of the standard Python classes that can validate elements and can
fire trait notifications when the contents change.  These classes are,
respectively, |TraitList|, |TraitDict| and |TraitSet| (not to be confused with
the deprecated Trait Handlers of the same names).

In addition to being able to take an appropriate value to initialize the
container (such as a sequence or mapping), these container subclasses also
take keyword-only arguments for validators (either a single item validator for
|TraitList| and |TraitSet|, or key and value validators for |TraitDict|) and
notifiers.

These classes were introduced in Traits 6.1 and the implementation details
described here are provisional and may change.

Backwards Compatibility
~~~~~~~~~~~~~~~~~~~~~~~

In practice, most traits containers are instances of |TraitListObject|,
|TraitDictObject| and |TraitSetObject| which are subclasses that are
created by the validators of |List|, |Dict| and |Set| traits respectively and
supplied with appropriate element validators that wrap the standard trait
validators so that constructs like ``List(Str)`` can work.

These objects are designed to be API compatible with the classes of the
same name from Traits 6.0 and before, and so have different constructors and
may behave slightly differently from the base classes in some cases.

In particular |TraitListObject| classes can have restrictions on their
length, which is not part of the base |TraitList| API.

All of these backward compatibility classes are strongly tied to a particular
object and trait, and are not designed to operate as stand-alone entities.
These relationships are required to support the `object.*_items`-style event
traits, but complicate the implementation, for example by having to use
weak references to the object, and having to take this additional structure
into account when serializing and deserializing.

It is a long-term goal to phase out the use of these backwards compatibility
classes.

Container Validators
~~~~~~~~~~~~~~~~~~~~

Container validators are callables that are expected to take a single value
and either return a validated value or raise a TraitError.  The default
validators simply pass the input value directly through, but validators can
potentially do much more.   Validators are expected to be idempotent:
``validate(validate(x)) == validate(x)`` should hold as long as
``validate(x)`` does not raise an error.

For example, the following validator casts the list items to integers,
raising a TraitError if that fails::

    def int_validator(value):
        try:
            return int(value)
        except ValueError:
            raise TraitError(
                "List items must be castable to an int, but a value %r was specified."
                % value
            )

So if we were to use this as the validator for a |TraitList| we would get the
following behaviour::

    >>> int_list = TraitList(item_validator=int_validator)
    >>> int_list.append("5")
    >>> int_list
    [5]
    >>> int_list.extend([3, 5, "aaaarrrghh"])
    TraitError: List items must be castable to an int, but a value 'aaaarrrghh' was specified.

In Traits 6.1 validation is not done uniformly before performing operations
to keep behaviour the same as Traits 6.0 and earlier, so results of operations can
sometimes be surprising::

    >>> int_list.append("6")
    >>> int_list.remove("6")
    ValueError: list.remove(x): x not in list

This is expected to be resolved in a future traits version by providing clear
guidance to users about when validation is performed, and possibly changing the
behaviour.

Container Notifiers
~~~~~~~~~~~~~~~~~~~

Container objects also have a list of notifiers that fire when the contents of
the container change.  Like trait notifiers, container notifiers are low-level
callbacks that are used by the higher-level, more user-friendly observer and
listener systems.  They have a fixed signature, which is slightly different for
lists, dicts and sets, but in all cases starts with the container object itself.
Notifiers are called in the order that they appear in the notifiers list and
should not mutate the parameters that they have been passed.

List notifiers must take 4 arguments: the **trait_list** object, the **index**
value or slice that identifies where the change occurred, a list of
**removed** elements, and a list of **added** elements.  The |TraitList|
methods make an attempt to normalize indices and slices to make things easier
for notification writers.

Dict notifiers expect 4 arguments: the **trait_dict** object, a dictionary of
**removed** items, a dictionary of **added** elements, and a dictionary of
**changed** items, where the values are the old values held in the keys.

Set notifiers expect 3 arguments: the **trait_set** object, the set of
**removed** elements, and the set of **added** elements.

Users should not usually need to interact with the container notifiers directly,
just as they do not usually need to interact with trait notifiers.


..
   # substitutions

.. |_class_traits| replace:: :meth:`~traits.ctraits.CHasTraits._class_traits`
.. |_instance_traits| replace:: :meth:`~traits.ctraits.CHasTraits._instance_traits`
.. |cTrait| replace:: :class:`~traits.ctraits.cTrait`
.. |CTrait| replace:: :class:`~traits.ctrait.CTrait`
.. |ctraits| replace:: :mod:`~traits.ctraits`
.. |CHasTraits| replace:: :class:`~traits.ctraits.CHasTraits`
.. |HasTraits| replace:: :class:`~traits.has_traits.HasTraits`
.. |TraitList| replace:: :class:`~traits.trait_list_object.TraitList`
.. |TraitDict| replace:: :class:`~traits.trait_dict_object.TraitDict`
.. |TraitSet| replace:: :class:`~traits.trait_dict_object.TraitSet`
.. |TraitListObject| replace:: :class:`~traits.trait_list_object.TraitListObject`
.. |TraitDictObject| replace:: :class:`~traits.trait_dict_object.TraitDictObject`
.. |TraitSetObject| replace:: :class:`~traits.trait_dict_object.TraitSetObject`
.. |List| replace:: :class:`~traits.trait_types.List`
.. |Dict| replace:: :class:`~traits.trait_types.Dict`
.. |Set| replace:: :class:`~traits.trait_types.Set`
