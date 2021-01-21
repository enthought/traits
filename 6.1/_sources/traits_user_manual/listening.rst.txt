.. _on-trait-change-notification:

===========================================
Trait Notification with **on_trait_change**
===========================================

**on_trait_change** is an older method for setting up change notifications. It
has several design flaws and limitations. A newer mechanism **observe** is
introduced for overcoming them. See :ref:`observe-notification` for details and
for how to migrate.

Change notifications can be set up with **on_trait_change** in several ways:

.. index:: notification; strategies

* Dynamically, by calling on_trait_change() or on_trait_event() to establish
  (or remove) change notification handlers.
* Statically, by decorating methods on the class with the @on_trait_change
  decorator to indicate that they handle notification for specified attributes.
* Statically, by using a special naming convention for methods on the class to
  indicate that they handle notifications for specific trait attributes.

.. index:: notification; dynamic

.. _dynamic-notification:

Dynamic Notification
--------------------

Dynamic notification is useful in cases where a notification handler cannot be
defined on the class (or a subclass) whose trait attribute changes are to be
monitored, or if you want to monitor changes on certain instances of a class,
but not all of them. To use dynamic notification, you define a handler method
or function, and then invoke the on_trait_change() or on_trait_event() method
to register that handler with the object being monitored. Multiple handlers can
be defined for the same object, or even for the same trait attribute on the
same object. The handler registration methods have the following signatures:

.. index:: on_trait_change; method

.. method:: on_trait_change(handler[, name=None, remove=False, dispatch='same'])

.. index:: on_trait_event(); method

.. method:: on_trait_event(handler[, name=None, remove=False, dispatch='same'])

In these signatures:

* *handler*: Specifies the function or bound method to be called whenever the
  trait attributes specified by the *name* parameter are modified.
* *name*: Specifies trait attributes whose changes trigger the handler being
  called. If this parameter is omitted or is None, the handler is called
  whenever *any* trait attribute of the object is modified. The syntax
  supported by this parameter is discussed in :ref:`the-name-parameter`.
* *remove*: If True (or non-zero), then handler will no longer be called when
  the specified trait attributes are modified. In other words, it causes the
  handler to be "unhooked".
* *dispatch*: String indicating the thread on which notifications must be run.
  In most cases, it can be omitted. See the *Traits API Reference* for details
  on non-default values.

.. index:: examples; dynamic notification

.. _example-of-a-dynamic-notification-handler:

Example of a Dynamic Notification Handler
`````````````````````````````````````````

Setting up a dynamic trait attribute change notification handler is illustrated
in the following example::

    # dynamic_notification.py --- Example of dynamic notification
    from traits.api import Float, HasTraits, Instance

    class Part (HasTraits):
      cost = Float(0.0)

    class Widget (HasTraits):
      part1 = Instance(Part)
      part2 = Instance(Part)
      cost  = Float(0.0)

      def __init__(self):
        self.part1 = Part()
        self.part2 = Part()
        self.part1.on_trait_change(self.update_cost, 'cost')
        self.part2.on_trait_change(self.update_cost, 'cost')

      def update_cost(self):
        self.cost = self.part1.cost + self.part2.cost

    # Example:
    w = Widget()
    w.part1.cost = 2.25
    w.part2.cost = 5.31
    print w.cost
    # Result: 7.56

In this example, the Widget constructor sets up a dynamic trait attribute
change notification so that its update_cost() method is called whenever the
**cost** attribute of either its **part1** or **part2** attribute is modified.
This method then updates the cost attribute of the widget object.

.. index:: name parameter; on_trait_change()

.. _the-name-parameter:

The *name* Parameter
````````````````````

The *name* parameter of on_trait_change() and on_trait_event() provides
significant flexibility in specifying the name or names of one or more trait
attributes that the handler applies to. It supports syntax for specifying
names of trait attributes not just directly on the current object, but also
on sub-objects referenced by the current object.

The *name* parameter can take any of the following values:

* Omitted, None, or 'anytrait': The handler applies to any trait attribute on
  the object.
* A name or list of names: The handler applies to each trait attribute on the
  object with the specified names.
* An "extended" name or list of extended names: The handler applies to each
  trait attribute that matches the specified extended names.

.. index::
   pair: extended trait names; syntax

.. _syntax:

Syntax
::::::

Extended names use the following syntax:

.. productionList::
   xname: xname2['.'xname2]*
   xname2: ( xname3 | '['xname3[','xname3]*']' ) ['*']
   xname3: xname | ['+'|'-'][name] | name['?' | ('+'|'-')[name]]

A *name* is any valid Python attribute name.

.. index::
   pair: extended trait names; semantics

.. _semantics:

Semantics
:::::::::

.. _semantics-of-extended-name-notation-table:

.. rubric:: Semantics of extended name notation

+------------------------------+----------------------------------------------+
| Pattern                      | Meaning                                      |
+==============================+==============================================+
|*item1*\ .\ *item2*           |A trait named item1 contains an object (or    |
|                              |objects, if *item1* is a list or dictionary), |
|                              |with a trait named *item2*. Changes to either |
|                              |*item1* or *item2* trigger a  notification.   |
+------------------------------+----------------------------------------------+
|*item1*\ :*item2*             |A trait named **item1** contains an object (or|
|                              |objects, if *item1* is a list or dictionary), |
|                              |with a trait named *item2*. Changes to *item2*|
|                              |trigger a notification, while changes to      |
|                              |*item1* do not (i.e., the ':' indicates that  |
|                              |changes to the link object are not reported.  |
+------------------------------+----------------------------------------------+
|[*item1*, *item2*, ...,       |A list that matches any of the specified      |
|*itemN*]                      |items. Note that at the topmost level, the    |
|                              |surrounding square brackets are optional.     |
+------------------------------+----------------------------------------------+
|*item*\ []                    |A trait named *item* is a list. Changes to    |
|                              |*item* or to its members triggers a           |
|                              |notification.                                 |
+------------------------------+----------------------------------------------+
|*name*?                       |If the current object does not have an        |
|                              |attribute called *name*, the reference can be |
|                              |ignored. If the '?' character is omitted, the |
|                              |current object must have a trait called       |
|                              |*name*; otherwise, an exception is raised.    |
+------------------------------+----------------------------------------------+
|*prefix*\ +                   |Matches any trait attribute on the object     |
|                              |whose name begins with *prefix*.              |
+------------------------------+----------------------------------------------+
|+\ *metadata_name*            |Matches any trait on the object that has a    |
|                              |metadata attribute called *metadata_name*.    |
+------------------------------+----------------------------------------------+
|-*metadata_name*              |Matches any trait on the current object that  |
|                              |does *not* have a metadata attribute called   |
|                              |*metadata_name*.                              |
+------------------------------+----------------------------------------------+
|*prefix*\ +\ *metadata_name*  |Matches any trait on the object whose name    |
|                              |begins with *prefix* and that has a metadata  |
|                              |attribute called *metadata_name*.             |
+------------------------------+----------------------------------------------+
|*prefix*\ -*metadata_name*    |Matches any trait on the object whose name    |
|                              |begins with *prefix* and that does *not* have |
|                              |a metadata attribute called *metadata_name*.  |
+------------------------------+----------------------------------------------+
|``+``                         |Matches all traits on the object.             |
+------------------------------+----------------------------------------------+
|*pattern*\ *                  |Matches object graphs where *pattern* occurs  |
|                              |one or more times. This option is useful for  |
|                              |setting up listeners on recursive data        |
|                              |structures like trees or linked lists.        |
+------------------------------+----------------------------------------------+

.. index:: extended trait names; examples

.. _examples-of-extended-name-notation-table:

.. rubric:: Examples of extended name notation

+--------------------------+--------------------------------------------------+
|Example                   | Meaning                                          |
+==========================+==================================================+
|``'foo, bar, baz'``       |Matches *object*.\ **foo**, *object*.\ **bar**,   |
|                          |and *object*.\ **baz**.                           |
+--------------------------+--------------------------------------------------+
|``['foo', 'bar', 'baz']`` |Equivalent to ``'foo, bar, baz'``, but may be     |
|                          |useful in cases where the individual items are    |
|                          |computed.                                         |
+--------------------------+--------------------------------------------------+
|``'foo.bar.baz'``         |Matches *object*.\ **foo.bar.baz**                |
+--------------------------+--------------------------------------------------+
|``'foo.[bar,baz]'``       |Matches *object*.\ **foo.bar** and                |
|                          |*object*.\ **foo.baz**                            |
+--------------------------+--------------------------------------------------+
|``'foo[]'``               |Matches a list trait on *object* named **foo**.   |
+--------------------------+--------------------------------------------------+
|``'([left,right]).name*'``|Matches the **name** trait of each tree node      |
|                          |object that is linked from the **left** or        |
|                          |**right** traits of a parent node, starting with  |
|                          |the current object as the root node. This pattern |
|                          |also matches the **name** trait of the current    |
|                          |object, as the **left** and **right** modifiers   |
|                          |are optional.                                     |
+--------------------------+--------------------------------------------------+
|``'+dirty'``              |Matches any trait on the current object that has a|
|                          |metadata attribute named **dirty** set.           |
+--------------------------+--------------------------------------------------+
|``'foo.+dirty'``          |Matches any trait on *object*.\ **foo** that has a|
|                          |metadata attribute named **dirty** set.           |
+--------------------------+--------------------------------------------------+
|``'foo.[bar,-dirty]'``    |Matches *object*.\ **foo.bar** or any trait on    |
|                          |*object*.\ **foo** that does not have a metadata  |
|                          |attribute named **dirty** set.                    |
+--------------------------+--------------------------------------------------+

For a pattern that references multiple objects, any of the intermediate
(non-final) links can be traits of type Instance, List, or Dict. In the case of
List or Dict traits, the subsequent portion of the pattern is applied to each
item in the list or value in the dictionary. For example, if **self.children**
is a list, a handler set for ``'children.name'`` listens for changes to the
**name** trait for each item in the **self.children** list.

.. note::
    In the case of Dict, List, and Set with nested patterns (e.g.,
    ``'children.name'``), not all handler signatures (see
    :ref:`notification-handler-signatures`) are supported; see section
    :ref:`dynamic-handler-special-cases` for more details.

The handler routine is also invoked when items are added or removed from a list
or dictionary, because this is treated as an implied change to the item's trait
being monitored.

.. index:: notification; dynamic

.. _notification-handler-signatures:

Notification Handler Signatures
```````````````````````````````

The handler passed to on_trait_change() or on_trait_event() can have any one of
the following signatures:

.. index:: handler; signatures, trait change handler; signatures

- handler()
- handler(*new*)
- handler(*name*, *new*)
- handler(*object*, *name*, *new*)
- handler(*object*, *name*, *old*, *new*)

These signatures use the following parameters:

.. index:: object parameter; notification handlers

* *object*: The object whose trait attribute changed.

.. index:: name parameter; notification handlers

* *name*: The attribute that changed. If one of the objects in a sequence is a
  List or Dict, and its membership changes, then this is the name of the trait
  that references it, with '_items appended. For example, if the handler is
  monitoring ``'foo.bar.baz'``, where **bar** is a List, and an item is added
  to **bar**, then the value of the *name* parameter is 'bar_items'.

.. index:: new parameter to the notification handlers

* *new*: The new value of the trait attribute that changed. For changes to
  List and Dict objects, this is a list of items that were added.

.. index:: old parameter to the notification handlers

* *old*: The old value of the trait attribute that changed. For changes to List
  and Dict object, this is a list of items that were deleted. For event traits,
  this is Undefined.

If the handler is a bound method, it also implicitly has *self* as a first
argument.

.. index:: notification; special cases

.. _dynamic-handler-special-cases:

Dynamic Handler Special Cases
`````````````````````````````

In the one- and two-parameter signatures, the handler does not receive enough
information to distinguish between a change to the final trait attribute being
monitored, and a change to an intermediate object. In this case, the
notification dispatcher attempts to map a change to an intermediate object to
its effective change on the final trait attribute. This mapping is only
possible if all the intermediate objects are single values (such as Instance or
Any traits), and not List or Dict traits. If the change involves a List or
Dict, then the notification dispatcher raises a TraitError when attempting to
call a one- or two-parameter handler function, because it cannot unambiguously
resolve the effective value for the final trait attribute.

Zero-parameter signature handlers receive special treatment if the final trait
attribute is a List or Dict, and if the string used for the *name* parameter is
not just a simple trait name. In this case, the handler is automatically called
when the membership of a final List or Dict trait is changed. This behavior can
be useful in cases where the handler needs to know only that some aspect of the
final trait has changed. For all other signatures, the handler function must be
explicitly set for the *name*\ _items trait in order to called when the
membership of the name trait changes. (Note that the *prefix*\ + and *item*\ []
syntaxes are both ways to specify both a trait name and its '_items' variant.)

This behavior for zero-parameter handlers is not triggered for simple trait
names, to preserve compatibility with code written for versions of Traits
prior to 3.0. Earlier versions of Traits required handlers to be separately
set for a trait and its items, which would result in redundant notifications
under the Traits 3.0 behavior. Earlier versions also did not support the
extended trait name syntax, accepting only simple trait names. Therefore, to
use the "new style" behavior of zero-parameter handlers, be sure to include
some aspect of the extended trait name syntax in the name specifier.

.. index:: examples; handlers

::

    # list_notifier.py -- Example of zero-parameter handlers for an object
    #                     containing a list
    from traits.api import HasTraits, List

    class Employee: pass

    class Department( HasTraits ):
        employees = List(Employee)

    def a_handler(): print("A handler")
    def b_handler(): print("B handler")
    def c_handler(): print("C handler")

    fred = Employee()
    mary = Employee()
    donna = Employee()

    dept = Department(employees=[fred, mary])

    # "Old style" name syntax
    # a_handler is called only if the list is replaced:
    dept.on_trait_change( a_handler, 'employees' )
    # b_handler is called if the membership of the list changes:
    dept.on_trait_change( b_handler, 'employees_items')

    # "New style" name syntax
    # c_handler is called if 'employees' or its membership change:
    dept.on_trait_change( c_handler, 'employees[]' )

    print("Changing list items")
    dept.employees[1] = donna     # Calls B and C
    print("Replacing list")
    dept.employees = [donna]      # Calls A and C

.. index:: notification; static

.. _static-notification:

Static Notification
-------------------

The static approach is the most convenient option, but it is not always
possible. Writing a static change notification handler requires that, for a
class whose trait attribute changes you are interested in, you write a method
on that class (or a subclass).  Therefore, you must know in advance what
classes and attributes you want notification for, and you must be the author
of those classes. Static notification also entails that every instance of the
class has the same notification handlers.

To indicate that a particular method is a static notification handler for a
particular trait, you have two options:

.. index::
   pair: decorator; on_trait_change

* Apply the @on_trait_change decorator to the method.
* Give the method a special name based on the name of the trait attribute it
  "listens" to.

.. _handler-decorator:

Handler Decorator
`````````````````
The most flexible method of statically specifying that a method is a
notification handler for a trait is to use the @on_trait_change() decorator.
The @on_trait_change() decorator is more flexible than specially-named method
handlers, because it supports the very powerful extended trait name syntax
(see :ref:`the-name-parameter`). You can use the decorator to set handlers on
multiple attributes at once, on trait attributes of linked objects, and on
attributes that are selected based on trait metadata.

.. index::
   pair: on_trait_change; syntax

.. _decorator-syntax:

Decorator Syntax
::::::::::::::::

The syntax for the decorator is::

    @on_trait_change( 'extended_trait_name' )
    def any_method_name( self, ...):
    ...

In this case, *extended_trait_name* is a specifier for one or more trait
attributes, using the syntax described in :ref:`the-name-parameter`.

The signatures that are recognized for "decorated" handlers are the same as
those for dynamic notification handlers, as described in
:ref:`notification-handler-signatures`. That is, they can have an *object*
parameter, because they can handle notifications for trait attributes that do
not belong to the same object.

.. index::
   pair: on_trait_change; semantics

.. _decorator-semantics:

Decorator Semantics
:::::::::::::::::::

The functionality provided by the @on_trait_change() decorator is identical to
that of specially-named handlers, in that both result in a call to
on_trait_change() to register the method as a notification handler. However,
the two approaches differ in when the call is made. Specially-named handlers
are registered at class construction time; decorated handlers are registered at
instance creation time.

By default, decorated handlers are registered prior to setting the object
state. When an instance is constructed with a trait value that is different
from the default, that is considered a change and will fire the associated
change handlers. The ``post_init`` argument in @on_trait_change can be used
to delay registering the handler to after the state is set.

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/post_init_notification.py
   :start-after: post_init_notification

.. index:: notification; specially-named handlers

.. _specially-named-notification-handlers:

Specially-named Notification Handlers
`````````````````````````````````````

There are two kinds of special method names that can be used for static trait
attribute change notifications. One is attribute-specific, and the other
applies to all trait attributes on a class.

.. index:: _name_changed(), _name_fired()

To notify about changes to a single trait attribute named name, define a method
named _\ *name*\ _changed() or _\ *name*\ _fired(). The leading underscore
indicates that attribute-specific notification handlers are normally part of a
class's private API. Methods named _\ *name*\ _fired() are normally used with
traits that are events, described in :ref:`trait-events`.

To notify about changes to any trait attribute on a class, define a method
named _anytrait_changed().

.. index::
   pair: examples; _any_trait_changed()
   pair: static notification; examples

Both of these types of static trait attribute notification methods are
illustrated in the following example::

    # static_notification.py --- Example of static attribute
    #                            notification
    from traits.api import HasTraits, Float

    class Person(HasTraits):
        weight_kg = Float(0.0)
        height_m =  Float(1.0)
        bmi = Float(0.0)

        def _weight_kg_changed(self, old, new):
             print('weight_kg changed from %s to %s ' % (old, new))
             if self.height_m != 0.0:
                 self.bmi = self.weight_kg / (self.height_m**2)

        def _anytrait_changed(self, name, old, new):
             print('The %s trait changed from %s to %s ' \
                    % (name, old, new))
    """
    >>> bob = Person()
    >>> bob.height_m = 1.75
    The height_m trait changed from 1.0 to 1.75
    >>> bob.weight_kg = 100.0
    The weight_kg trait changed from 0.0 to 100.0
    weight_kg changed from 0.0 to 100.0
    The bmi trait changed from 0.0 to 32.6530612245
    """

In this example, the attribute-specific notification function is
_weight_kg_changed(), which is called only when the **weight_kg** attribute
changes. The class-specific notification handler is _anytrait_changed(), and
is called when **weight_kg**, **height_m**, or **bmi** changes. Thus, both
handlers are called when the **weight_kg** attribute changes. Also, the
_weight_kg_changed() function modifies the **bmi** attribute, which causes
_anytrait_changed() to be called for that attribute.

The arguments that are passed to the trait attribute change notification
method depend on the method signature and on which type of static notification
handler it is.

.. _attribute-specific-handler-signatures:

Attribute-specific Handler Signatures
`````````````````````````````````````

For an attribute specific notification handler, the method signatures supported
are:

.. method:: _name_changed()
.. method:: _name_changed(new)
   :noindex:
.. method:: _name_changed(old, new)
   :noindex:
.. method:: _name_changed(name, old, new)
   :noindex:

The method name can also be _\ *name*\ _fired(), with the same set of
signatures.

In these signatures:

* *new* is the new value assigned to the trait attribute.
* *old* is the old value assigned to the trait attribute.
* *name* is the name of the trait attribute.  The extended trait name syntax
  is not supported.

Note that these signatures follow a different pattern for argument
interpretation from dynamic handlers and decorated static handlers. Both of
the following methods define a handler for an object's **name** trait::

    def _name_changed( self, arg1, arg2, arg3):
        pass

    @on_trait_change('name')
    def some_method( self, arg1, arg2, arg3):
        pass

However, the interpretation of arguments to these methods differs, as shown in
the following table.

.. _handler-argument-interpretation-table:

.. rubric:: Handler argument interpretation

======== =================== ================
Argument _\ *name*\ _changed @on_trait_change
======== =================== ================
*arg1*   *name*              *object*
*arg2*   *old*               *name*
*arg3*   *new*               *new*
======== =================== ================

.. _general-static-handler-signatures:

General Static Handler Signatures
`````````````````````````````````

In the case of a non-attribute specific handler, the method signatures
supported are:

.. method:: _anytrait_changed()
.. method:: _anytrait_changed(name)
   :noindex:
.. method:: _anytrait_changed(name, new)
   :noindex:
.. method:: _anytrait_changed(name, old, new)
   :noindex:

The meanings for *name*, *new*, and *old* are the same as for
attribute-specific notification functions.

.. _trait-events:

Trait Events
------------
.. index:: events

The Traits package defines a special type of trait called an event. Events are
instances of (subclasses of) the Event class.

There are two major differences between a normal trait and an event:

* All notification handlers associated with an event are called whenever any
  value is assigned to the event. A normal trait attribute only calls its
  associated notification handlers when the previous value of the attribute
  is different from the new value being assigned to it.
* An event does not use any storage, and in fact does not store the values
  assigned to it. Any value assigned to an event is reported as the new value
  to all associated notification handlers, and then immediately discarded.
  Because events do not retain a value, the *old* argument to a notification
  handler associated with an event is always the special Undefined object (see
  :ref:`undefined-object`). Similarly, attempting to read the value of an event
  results in a TraitError exception, because an event has no value.

.. index::
   pair: events; examples

As an example of an event, consider::

    # event.py --- Example of trait event
    from traits.api import Event, HasTraits, List, Tuple

    point_2d = Tuple(0, 0)


    class Line2D(HasTraits):
        points = List(point_2d)
        line_color = RGBAColor('black')
        updated = Event

        def redraw(self):
            pass  # Not implemented for this example

        def _points_changed(self):
            self.updated = True

        def _updated_fired(self):
            self.redraw()

In support of the use of events, the Traits package understands
attribute-specific notification handlers with names of the form
_\ *name*\ _fired(), with signatures identical to the _\ *name*\ _changed() functions.
In fact, the Traits package does not check whether the trait attributes that
_\ *name*\ _fired() handlers are applied to are actually events. The function
names are simply synonyms for programmer convenience.

Similarly, a function named on_trait_event() can be used as a synonym for
on_trait_change() for dynamic notification.

.. index:: Undefined object

.. _undefined-object:

Undefined Object
````````````````

Python defines a special, singleton object called None. The Traits package
introduces an additional special, singleton object called Undefined.

The Undefined object is used to indicate that a trait attribute has not yet
had a value set (i.e., its value is undefined). Undefined is used instead of
None, because None is often used for other meanings, such as that the value
is not used. In particular, when a trait attribute is first assigned a value
and its associated trait notification handlers are called, Undefined is passed
as the value of the old parameter to each handler, to indicate that the
attribute previously had no value. Similarly, the value of a trait event is
always Undefined.

.. _trait-items-handlers:

Container Items Events
``````````````````````
.. index::
    pair: container items; event
    single: _name_items_changed()

For the container traits (List, Dict and Set) both static and dynamic handlers
for the trait are only called when the entire value of the trait is replaced
with another value; they do not get fired when the item itself is mutated
in-place.  To listen to internal changes, you need to either use a dynamic
handler with the ``[]`` suffix as noted in the Table
:ref:`semantics-of-extended-name-notation-table`, or you can define an
*name*\ _items event handler.

For these trait types, an auxilliary *name*\ _items Event trait is defined which
you can listen to either with a static handler _\ *name*\ _items_changed()
or a dynamic handler which matches *name*\ _items, and these handlers will be
called with notifications of changes to the contents of the list, set or
dictionary.

.. index:: TraitListEvent, TraitSetEvent, TraitDictEvent

For these handlers the *new* parameter is a :index:`TraitListEvent`,
:index:`TraitSetEvent` or :index:`TraitDictEvent` object whose attributes
indicate the nature of the change and, because they are Event handlers, the
*old* parameter is Undefined.

All of these event objects have **added** and **removed** attributes that
hold a list, set or dictionary of the items that were added and removed,
respectively.

The TraitListEvent has an additional **index** attribute that holds either
the index of the first item changed, or for changes involving slices with
steps other than 1, **index** holds the _slice_ that was changed.  For
slice values you can always recover the actual values which were changed or
removed via ``range(index.start, index.stop, index.end)``.

The TraitDictEvent has an additional **changed** attribute which holds the
keys that were modified and the _old_ values that those keys held.  The new
values can be queried from directly from the trait value, if needed.

Handlers for these events should not mutate the attributes of the event
objects, including avoiding in-place changes to **added**, **removed**, etc.

.. _on-trait-change-dos-n-donts:


Dos and Don’ts
--------------

Don't assume handlers are called in a specific order
````````````````````````````````````````````````````

Don't do this::

    @on_trait_change("name")
    def update_number(self):
        self.number += 1

    @on_trait_change("name")
    def update_orders(self):
        if self.number > 5:
          self.orders.clear()

Do this instead::

    @on_trait_change("name")
    def update(self):
        number = self.number + 1
        self.number = number
        if number > 5:
            self.orders.clear()

The first example is problematic because when ``name`` changes, calling
``update_orders`` after ``update_number``  produces a result that is different
from calling ``update_number`` after ``update_orders``.

Even if the change handlers appear to be called in a deterministic order,
this would be due to implementation details that may not hold true across
releases and platforms.

Don't raise exception from a change handler
```````````````````````````````````````````

Don't do this::

    name = String()

    @on_trait_change("name")
    def update_name(self, new):
        if len(new) == 0:
            raise ValueError("Name cannot be empty.")

What to do instead depends on the use case. For the above use case, ``String``
supports length checking::

    name = String(minlen=1)

Traits consider handlers for the same change event to be independent of each
other. Therefore, any uncaught exception from one change handler will be captured
and logged, so not to prevent other handlers to be called.
