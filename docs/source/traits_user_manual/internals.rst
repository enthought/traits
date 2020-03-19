.. index:: internals

.. todo:: what is a Trait?  Terminology ...
.. todo:: add links to further information on CPython internals (tp_getattro, ...)

Traits internals
================

This section of the documentation is intended both for those developing Traits
itself, and for those using Traits who would like a better understanding of
the Traits internals.


Fundamentals
------------

The runtime behavior of Traits is governed by two key classes: |CTrait| and
|HasTraits|. Each of these classes inherits from a superclass that's
implemented in the |ctraits| extension module: |CTrait| inherits from
|cTrait|, while |HasTraits| inherits from |CHasTraits|.

The base classes |CHasTraits| and |cTrait| are not intended for direct use and
do not provide a complete, coherent API: that API is provided by their
subclasses |HasTraits| and |CTrait|. The existence and precise semantics of the
base classes should be regarded as implementation details. In what follows,
we'll frequently refer to behavior of |HasTraits| and |CTrait| even when the
behavior we're referring to is actually implemented by |CHasTraits| or
|cTrait|.


We'll examine each of these classes, along with some of their hidden state, in
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

To support trait get and set operations, a |HasTraits| object (that is, an
instance of a user-defined subclass of |HasTraits|) has two key pieces of
state: a dictionary of **class traits**, and a second dictionary of **instance
traits**. Each dictionary is a mapping from trait names to |CTrait| objects. A
|CTrait| object encapsulates the rules for getting and setting the
corresponding attribute, as well as providing an attachment point for
trait notifications.

In addition to these dictionaries, a |HasTraits| object also has a ``__dict__``
that stores attribute values for that object in the normal way.

Analogously to class variables and instance variables, a class traits
dictionary is shared between all instances of a given |HasTraits| subclass,
while the instance traits dictionary is specific to a particular |HasTraits|
instance. The instance traits dictionary is created on demand when first
needed, while the class traits dictionary is always present.

For introspection and debugging purposes, both of these dictionaries can
be retrieved directly, using the |_instance_traits| and |_class_traits|
methods. However, it's not recommended to use either of these methods in
production code.

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

And if we create a second ingredient, it shares class traits (but not
instance traits) with the first one::

    >>> flour = Ingredient(name="flour", quantity=3.5)
    >>> flour._class_traits() is eggs._class_traits()
    True
    >>> flour._instance_traits() is eggs._instance_traits()
    False


Key class: |CTrait|
~~~~~~~~~~~~~~~~~~~

A |CTrait| object has two main purposes:

- Encapsulate the rules for getting and setting a traited attribute on
  a |HasTraits| object.
- Provide an attachment point for trait notifiers.


Attribute retrieval
~~~~~~~~~~~~~~~~~~~

When evaluating ``obj.name`` for a ``HasTraits`` object ``obj``, the following
sequence of steps occurs:

- The ``name`` is looked up in ``obj.__dict__``. If found, the corresponding
  value is returned immediately.
- If ``name`` is not found in ``obj.__dict__``, we look first for an instance
  trait named ``name``, and then for a class trait named ``name``. Thus an
  instance trait with a given name will shadow a class trait with the same
  name.
- If a matching trait is found, its ``getattr`` slot is invoked to retrieve
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







When



- determine which |CTrait| instance controls this operation
- delegate the retrieval of the corresponding value to this |CTrait| instance








A |HasTraits| object also allows notifiers.




has two types of traits ...



..
   # substitutions

.. |_class_traits| replace:: :meth:`~traits.ctraits.CHasTraits._class_traits`
.. |_instance_traits| replace:: :meth:`~traits.ctraits.CHasTraits._instance_traits`
.. |cTrait| replace:: :class:`~traits.ctraits.cTrait`
.. |CTrait| replace:: :class:`~traits.ctrait.CTrait`
.. |ctraits| replace:: :mod:`~traits.ctraits`
.. |CHasTraits| replace:: :class:`~traits.ctraits.CHasTraits`
.. |HasTraits| replace:: :class:`~traits.has_traits.HasTraits`
