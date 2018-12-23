.. index:: deferral

.. _deferring-traits:

Deferring Trait Definitions
===========================

One of the advanced capabilities of the Traits package is its support for trait
attributes to defer their definition and value to another object than the one
the attribute is defined on. This has many applications, especially in cases
where objects are logically contained within other objects and may wish to
inherit or derive some attributes from the object they are contained in or
associated with. Deferring leverages the common "has-a" relationship between
objects, rather than the "is-a" relationship that class inheritance provides.

.. index:: delegation, prototyping

There are two ways that a trait attribute can defer to another object's
attribute: *delegation* and *prototyping*. In delegation, the deferring
attribute is a complete reflection of the delegate attribute. Both the value and
validation of the delegate attribute are used for the deferring attribute;
changes to either one are reflected in both. In prototyping, the deferring
attribute gets its value and validation from the prototype attribute, *until the
deferring attribute is explicitly changed*. At that point, while the deferring
attribute still uses the prototype's validation, the link between the values is
broken, and the two attributes can change independently. This is essentially a
"copy on write" scheme.

The concepts of delegation and prototyping are implemented in the Traits package
by two classes derived from TraitType: DelegatesTo and PrototypedFrom. [5]_

.. _delegatesto:

DelegatesTo
-----------

.. class:: DelegatesTo(delegate[, prefix='', listenable=True, **metadata])

.. index:: delegate parameter to DelegatesTo initializer

The *delegate* parameter is a string that specifies the name of an attribute
on the same object, which refers to the object whose attribute is deferred to;
it is usually an Instance trait. The value of the delegating attribute changes
whenever:

* The value of the appropriate attribute on the delegate object changes.
* The object referenced by the trait named in the *delegate* parameter changes.
* The delegating attribute is explicitly changed.

Changes to the delegating attribute are propagated to the delegate object's
attribute.

The *prefix* and *listenable* parameters to the initializer function specify
additional information about how to do the delegation.

.. index::
   pair: delegation; examples

If *prefix* is the empty string or omitted, the delegation is to an attribute
of the delegate object with the same name as the trait defined by the
DelegatesTo object. Consider the following example::

    # delegate.py --- Example of trait delegation
    from traits.api \
        import DelegatesTo, HasTraits, Instance, Str

    class Parent(HasTraits):
        first_name = Str
        last_name  = Str

    class Child(HasTraits):
        first_name = Str
        last_name  = DelegatesTo('father')
        father     = Instance(Parent)
        mother     = Instance(Parent)

    """
    >>> tony  = Parent(first_name='Anthony', last_name='Jones')
    >>> alice = Parent(first_name='Alice', last_name='Smith')
    >>> sally = Child( first_name='Sally', father=tony, mother=alice)
    >>> print(sally.last_name)
    Jones
    >>> sally.last_name = 'Cooper' # Updates delegatee
    >>> print(tony.last_name)
    Cooper
    >>> sally.last_name = sally.mother # ERR: string expected
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "c:\src\trunk\enthought\traits\trait_handlers.py", line
    163, in error
        raise TraitError( object, name, self.info(), value )
    traits.trait_errors.TraitError:  The 'last_name' trait of a
    Parent instance must be a string, but a value of <__main__.Parent object at
    0x014D6D80> <class '__main__.Parent'> was specified.
    """

A Child object delegates its **last_name** attribute value to its **father**
object's **last_name** attribute. Because the *prefix* parameter was not
specified in the DelegatesTo initializer, the attribute name on the delegatee is
the same as the original attribute name. Thus, the **last_name** of a Child is
the same as the **last_name** of its **father**. When either the **last_name**
of the Child or the **last_name** of the father is changed, both attributes
reflect the new value.

.. _prototypedfrom:

PrototypedFrom
--------------
.. class:: PrototypedFrom(prototype[, prefix='', listenable=True, **metadata])

.. index:: prototype parameter to PrototypesFrom

The *prototype* parameter is a string that specifies the name of an attribute on
the same object, which refers to the object whose attribute is prototyped; it is
usually an Instance trait. The prototyped attribute behaves similarly to a
delegated attribute, until it is explicitly changed; from that point forward,
the prototyped attribute changes independently from its prototype.

The *prefix* and *listenable* parameters to the initializer function specify
additional information about how to do the prototyping.

.. _keyword-parameters:

Keyword Parameters
------------------

The *prefix* and *listenable* parameters of the DelegatesTo and PrototypedFrom
initializer functions behave similarly for both classes.

.. index:: prefix parameter to initializer methods

.. _prefix-keyword:

Prefix Keyword
``````````````

When the *prefix* parameter is a non-empty string, the rule for performing trait
attribute look-up in the deferred-to object is modified, with the modification
depending on the format of the prefix string:

* If *prefix* is a valid Python attribute name, then the original attribute
  name is replaced by prefix when looking up the deferred-to attribute.
* If *prefix* ends with an asterisk ('*'), and is longer than one character,
  then *prefix*, minus the trailing asterisk, is added to the front of the
  original attribute name when looking up the object attribute.
* If *prefix* is equal to a single asterisk ('*'), the value of the object
  class's **__prefix__** attribute is added to the front of the original
  attribute name when looking up the object attribute.

.. index::
   single: examples; prototype prefix
   pair: examples; prototyping

Each of these three possibilities is illustrated in the following example, using
PrototypedFrom::

    # prototype_prefix.py --- Examples of PrototypedFrom()
    #                         prefix parameter
    from traits.api import \
        PrototypedFrom, Float, HasTraits, Instance, Str

    class Parent (HasTraits):
        first_name = Str
        family_name = ''
        favorite_first_name = Str
        child_allowance = Float(1.00)
    class Child (HasTraits):
        __prefix__ = 'child_'
        first_name = PrototypedFrom('mother', 'favorite_*')
        last_name  = PrototypedFrom('father', 'family_name')
        allowance  = PrototypedFrom('father', '*')
        father     = Instance(Parent)
        mother     = Instance(Parent)

    """
    >>> fred = Parent( first_name = 'Fred', family_name = 'Lopez', \
    ... favorite_first_name = 'Diego', child_allowance = 5.0 )
    >>> maria = Parent(first_name = 'Maria', family_name = 'Gonzalez',\
    ... favorite_first_name = 'Tomas', child_allowance = 10.0 )
    >>> nino = Child( father=fred, mother=maria )
    >>> print('%s %s gets $%.2f for allowance' % (nino.first_name, \ ... nino.last_name, nino.allowance))
    Tomas Lopez gets $5.00 for allowance
    """

In this example, instances of the Child class have three prototyped trait
attributes:

* **first_name**, which prototypes from the **favorite_first_name** attribute
  of its **mother** object.
* **last_name**, which prototyped from the **family_name attribute** of its
  **father** object.
* **allowance**, which prototypes from the **child_allowance** attribute of its
  **father** object.

.. index:: listenable parameter to initializer methods

.. _listenable-keyword:

Listenable Keyword
``````````````````

By default, you can attach listeners to deferred trait attributes, just as you
can attach listeners to most other trait attributes, as described in the
following section. However, implementing the notifications correctly requires
hooking up complicated listeners under the covers. Hooking up these listeners
can be rather more expensive than hooking up other listeners. Since a common use
case of deferring is to have a large number of deferred attributes for static
object hierarchies, this feature can be turned off by setting
``listenable=False`` in order to speed up instantiation.

.. index::
   single: deferral; notification with
   pair: examples; deferral

.. _notification-with-deferring:

Notification with Deferring
---------------------------

While two trait attributes are linked by a deferring relationship (either
delegation, or prototyping before the link is broken), notifications for changes
to those attributes are linked as well. When the value of a deferred-to
attribute changes, notification is sent to any handlers on the deferring object,
as well as on the deferred-to object. This behavior is new in Traits version
3.0. In previous versions, only handlers for the deferred-to object (the object
directly changed) were notified. This behavior is shown in the following
example::

    # deferring_notification.py -- Example of notification with deferring
    from traits.api \
        import HasTraits, Instance, PrototypedFrom, Str

    class Parent ( HasTraits ):

        first_name = Str
        last_name  = Str

        def _last_name_changed(self, new):
            print("Parent's last name changed to %s." % new)

    class Child ( HasTraits ):

        father = Instance( Parent )
        first_name = Str
        last_name  = PrototypedFrom( 'father' )

        def _last_name_changed(self, new):
            print("Child's last name changed to %s." % new)

    """
    >>> dad = Parent( first_name='William', last_name='Chase' )
    Parent's last name changed to Chase.
    >>> son = Child( first_name='John', father=dad )
    Child's last name changed to Chase.
    >>> dad.last_name='Jones'
    Parent's last name changed to Jones.
    Child's last name changed to Jones.
    >>> son.last_name='Thomas'
    Child's last name changed to Thomas.
    >>> dad.last_name='Riley'
    Parent's last name changed to Riley.
    >>> del son.last_name
    Child's last name changed to Riley.
    >>> dad.last_name='Simmons'
    Parent's last name changed to Simmons.
    Child's last name changed to Simmons.
    """

Initially, changing the last name of the father triggers notification on both
the father and the son. Explicitly setting the son's last name breaks the
deferring link to the father; therefore changing the father's last name does not
notify the son. When the son reverts to using the father's last name (by
deleting the explicit value), changes to the father's last name again affect and
notif

.. rubric:: Footnotes

.. [5] Both of these class es inherit from the Delegate class. Explicit use of
   Delegate is deprecated, as its name and default behavior (prototyping) are
   incongruous.

