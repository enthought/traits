.. _observe-notification:

==================================
Trait Notification with |@observe|
==================================

Requesting trait attribute change notifications can be done in these
ways:

* Via class defintion: By decorating methods on the class with the |@observe|
  decorator to indicate that they handle notification for specified attributes.
* Via instance method: By calling |HasTraits.observe| instance method to establish (or remove) change
  notification handlers.

Via class definition
--------------------

Observers can be defined for every instance of a |HasTraits| subclass by
applying the |@observe| decorator on an instance method. It has the following
signature:

.. py:decorator:: observe(expression[, post_init=False, dispatch="same"])

   Mark an instance method of |HasTraits| as the handler being called
   when the specified trait change occurs.

   :param expression: A description of the traits are being observed.
   :type expression: str or list of str or |Expression|
   :param bool post_init: Whether the change handler is added after the
    initial object state is set.
   :param str dispatch: A string dedicating how the handler should be run.

Example:

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_decorator.py
   :start-after: observe_decorator

Notice that a change event is emitted at instance construction time because
the initial value is different from the default value.

The *post_init* argument can be used to delay adding the change handler
until after the object state is set.

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_post_init.py
   :start-at: @observe
   :lines: 1-3

Via instance method
-------------------

The |HasTraits.observe| method is useful for adding or removing change handler on a per
instance basis. The method has the following signature:

.. py:method:: HasTraits.observe(handler, expression[, remove=False, dispatch="same"])

   Add or remove change handler to be fired when one or many traits change.

   :param handler: The callable to be called when a change occurs. It will receive an event object as its single argument and shoul not raise any exceptions.
   :type handler: callable(object)
   :param expression: A description of the traits are being observed.
   :type expression: str or list of str or |Expression|
   :param bool remove: If true, remove the change handler for the given expression.
   :param str dispatch: A string dedicating how the handler should be run.

Example:

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_method.py
   :start-after: observe_method

See :ref:`observer-expression` for further information on the ``expression``
parameter.
See :ref:`observe-handler-signatures` for further information on the signature
of the notification handler.

.. _observer-expression:

The *expression* Parameter
--------------------------
The *expression* parameter in |@observe| provides significant flexibility
in specifying not just attributes directly on the current object, but also
attributes on nested objects and containers.

There are two approaches for creating an expression:

* Expressions as objects
* Text using Traits domain specific language

Expressions as objects
``````````````````````

|Expression| objects can be composed programmatically and be given to
|@observe|. These objects allow more fine grained control on how traits are
observed than a text description can do. Users will typically use the following
functions for constructing an expression. These functions can be imported from
**traits.observers.api**:

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Function
     - Purpose
   * - |Expression.trait|
     - For observing a specific named trait.
   * - |Expression.metadata|
     - For observing multiple traits with a specific metadata. Support further
       filtering on the metadata value.
   * - |Expression.dict_items|
     - For observing items in a dict.
   * - |Expression.list_items|
     - For observing items in a list.
   * - |Expression.set_items|
     - For observing items in a set.
   * - |Expression.filter_|
     - For observing traits satisfying a user-defined filter.
   * - |Expression.parse|
     - For parsing a string written in Traits domain specific language into an
       expression object.

Users can combine complex expressions using the functions |Expression.then|,
|Expression.join_| or Python's bitwise-or (`|`) operation.

Most of these functions will have a ``notify`` argument for setting whether
notifications should be fired for changes.

.. rubric:: Example expressions

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Expression
     - Meaning
   * - *trait("attr1")*
     - Matches a trait named *attr1* on an object and notifies for changes.
   * - *trait("attr1", optional=True)*
     - Matches a trait named *attr1* if it is defined. Ignore if it is not
       defined.
   * - *trait("attr1", notify=False).trait("attr2")*
     - Matches a trait named *attr2* on an object referenced by a trait named
       *attr1* on the current object. Changes to *attr2* will trigger
       notifications, while changes to *attr1* do not.
   * - *trait("foo").list_items().list_items().trait("value")*
     - Matches the *value* trait on an item of a nested list in another list
       *foo*. Assignment changes to *foo*, mutations to the lists or changes
       to *value* will trigger notifications.
   * - *metadata("updated")*
     - Matches any trait on the current that has a metadata attribute named
       *updated*. Changes on those traits will trigger notifications.
   * - *trait("foo") | trait("bar")*
     - Matches trait named *foo* or *bar* on the current object. Changes on
       *foo* or *bar* will trigger notifications.
   * - *trait("foo").then(trait("bar") | trait("baz"))*
     - Matches *foo.bar* or *foo.baz* on the current object. Changes on *foo*,
       *foo.bar* or *foo.baz* will trigger notifications.
   * - *trait("foo").filter_(lambda n, t: True)*
     - Matches any traits on *foo* on the current object. Changes on *foo* or
       the nested attributes will trigger notifications.


.. rubric:: Describe an expression

Expression can be defined as a standalone object without being attached
to an instance of |HasTraits|. To understand what an expression means, its
|Expression.print| method can be used::

    >>> from traits.observers.api import trait
    >>> trait("children").list_items().trait("age").print()
    Observes trait named 'children' with notifications,
        then observes items in a list with notifications,
            then observes trait named 'age' with notifications.


Traits domain specific language
```````````````````````````````
Traits domain specific language (Traits DSL) provides a convenient and concise
way to specify observation rules via a single text. It supports a subset of
features in |Expression|.

.. rubric:: Syntax

.. productionList::
    group: item (',' item)*
    item: term (connector term)*
    connector: '.' | ':'
    term: (union_group | simple_term | items_term)
    union_group: '[' group ']'
    simple_term: NAME | '+' NAME
    items_term: 'items'

.. rubric:: Sementics of Traits DSL

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Pattern
     - Meaning
   * - *attr1\.attr2*
     - Matches a trait named *attr2* on an object referenced by a trait named
       *item1* on the current object. Changes to *attr1* or *attr2* will
       trigger notifications.
   * - *attr1\:attr2*
     - Matches a trait named *attr2* on an object referenced by a trait named
       *attr1* on the current object. Changes to *attr2* will trigger
       notifications. Changes to *attr1* will not.
   * - *attr1\, attr2*
     - Matches trait named *attr1* or trait named *attr2*.
   * - *items*
     - "items" is a special keyword for matching items in a list or dict or
       set, or a trait named "items".
   * - [*attr1*, *attr2*, ..., *attrN*]
     - Matches any of the specified items.
   * - *+metadata_name*
     - Matches any trait on the object that has metadata *metadata_name*

.. rubric:: Examples of Traits DSL

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Example
     - Meaning
   * - ``"attr1"``
     - Matches a trait named *attr1* on an object and notifies for changes.
   * - ``"attr1:attr2"``
     - Matches a trait named *attr2* on an object referenced by a trait named
       *attr1* on the current object. Changes to *attr2* will trigger
       notifications, while changes to *attr1* do not.
   * - ``"container.items.value"``
     - Matches the *value* trait on an object which could be an element
       of a container (list/dict/set) referenced via the *container* trait on
       the current object; or the *value* trait on an object referenced via
       *container.items* on the current object. Assignment change to
       *container*, mutation on the container or changes on the *items* trait
       on *container*, or changes to the *value* trait on the nested object,
       will trigger notifications.
   * - ``"+updated"``
     - Matches any trait on the current that has a metadata attribute named
       *updated*. Changes on those traits will trigger notifications.
   * - ``"foo, bar"``
     - Matches trait named *foo* or *bar* on the current object. Changes on
       *foo* or *bar* will trigger notifications.
   * - ``"foo.[bar,baz]"``
     - Matches *foo.bar* or *foo.baz* on the current object. Changes on *foo*,
       *foo.bar* or *foo.baz* will trigger notifications.

.. rubric:: Parsing the text

Using the |Expression.parse| function, one can extend an expression in text
with additional features supported by |Expression|. For example::

    parse("foo.bar").filter_(lambda name, trait: name.startswith("my_"))

will observe traits with a prefix "my\_" on *foo.bar* on the current object.

.. rubric:: Describe an expression

Since |Expression.parse| returns an instance of |Expression|. One can
use |Expression.print| to inspect the meaning of the text::

    >>> from traits.observers.api import parse
    >>> parse("container.items.value").print()
    Observes a trait named 'container' with notifications,
        then optionally observes a trait named 'items' with notifications,
            then observes a trait named 'value' with notifications.
        then optionally observes items in a list with notifications,
            then observes a trait named 'value' with notifications.
        then optionally observes items in a dict with notifications,
            then observes a trait named 'value' with notifications.
        then optionally observes items in a set with notifications,
            then observes a trait named 'value' with notifications.


.. _observe-handler-signatures:

Notification Handler Signature
------------------------------

The handler passed to |@observe| must have the following signature:

- handler(*event*)

where the *event* parameter is an object representing the change observed.
The type of *event* depends on the context of the change. The handler should
not raise exceptions. Any unexpected exceptions will be captured and logged.

.. rubric:: Change event types

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Change
     - Event Object Type
   * - Attribute value
     - |TraitObserverEvent|
   * - Dict membership
     - |DictObserverEvent|
   * - List membership
     - |ListObserverEvent|
   * - Set membership
     - |SetObserverEvent|


The signature of *event* depends on the change type. This means if the handler
needs to act on the specific details of the change event, |@observe| should be
configured to only notify for that specific type of changes, or the
handler will need to check the type of the event parameter when it is invoked.
The following example shows the first option:

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_different_events.py
   :start-after: observe_different_events


Differences from |@on_trait_change|
-----------------------------------

Observe nested attributes in a container
````````````````````````````````````````

Suppose we have these classes::

    class Bar(HasTraits):
        value = Int()

    class Foo(HasTraits):
        container = List(Instance(Bar))

To notify for changes on *Bar.value* for an item in *Foo.container*,
with |@on_trait_change|, one may do::

    def handler():
        print("changed")

    foo = Foo()
    foo.on_trait_change(handler, "container.value")

Where the container nature is deduced at runtime (see
:ref:`trait-items-handlers`).

With |@observe|, one will explicitly specify when items of a list are
being observed.

Using text as the expression::

    def handler(event):
        print("changed")

    foo = Foo()
    foo.observe(handler, "container.items.value")

Or using expression objects::

    foo.observe(handler, trait("container").list_items().trait("value"))

The specially named *name*\_items is not used by |@observe|, but is still
defined for supporting |@on_trait_change|.

Syntax "[]" is not supported
````````````````````````````

Support we have this class::

    class Foo(HasTraits):
        container = List(Instance(Bar))

To notify for both reassignment of *Foo.container* and mutation on the list,
one may do::

    @on_trait_change("container[]")

or::

    @on_trait_change(["container", "container_items"])

With |@observe|, the syntax will be changed to::

    @observe("container.items")

or::

    @observe(trait("container").list_items())

Note that assignment changes to *container* and mutations to the container will
emit different event types for the change handler. See
:ref:`observe-handler-signatures` for details.


Syntax "-" is not supported
```````````````````````````

With |@on_trait_change|, the syntax *"-metadata_name"* is used to notify
for changes on traits that do NOT have a metadata with the give name. This
usage can be replaced by |Expression.filter_|::

  filter_(lambda name, trait: "metadata_name" not in trait.__dict__)


Existence of observed items is checked by default
`````````````````````````````````````````````````

With |@on_trait_change|, one can specify whether a trait name is optional using
the "?" syntax. This is meant to be used for allowing trait to be defined after
|@on_trait_change| is called. In practice, |@on_trait_change| does not always
complain about missing attributes.

This could lead to human errors being overlooked::

    class Foo(HasTraits):
        name = Str()

        @on_trait_change("nam")   # typo, or an omission in renaming
        def _name_updated(self):
            print("name changed")

    foo = Foo()         # does not fail.
    foo.name = "Name"   # nothing fires :(

With |@observe|, the existence of a trait is checked when the handler is
being added to the instance::

    class Foo(HasTraits):
        name = Str()

        @observe("nam")   # typo, or an omission in renaming
        def _name_updated(self, event):
            print("name changed")

    foo = Foo()   # Error here: Trait named 'nam' not found

There are situations where it is desirable to add the change handler before
a trait is defined.

In that case, the *optional* argument on |Expression.trait| can be used:

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_optional.py
   :start-at: class


Arbitrarily nested containers are supported
```````````````````````````````````````````

It is now possible to notify for changes on an object in a very nested
container. Suppose we have these classes::

    class Bar(HasTraits):
        value = Int()

    class Foo(HasTraits):
        bars = Dict(Str(), List(Instance(Bar)))

To observe *Bar.value*, one can do::

    foo = Foo()
    foo.observe(handler, "bars.items.items.value")

Or::

    foo.observe(handler, trait("bars").dict_items().list_items().trait("value")

The change handler signature is fixed to one argument
`````````````````````````````````````````````````````

|@on_trait_change| supports a range of call signatures for the change handler.
|@observe| supports only one. The single argument contains different content
based on the type of changes being handled. See
:ref:`observe-handler-signatures` for details.

|@observe| decorator can be stacked
```````````````````````````````````

With |@on_trait_change|, in order to reuse the same handler with different
parameters, one needs to create separate methods::

    @on_trait_change("attr1", post_init=True)
    def _handle_attr1_changed(self):
        self._update_plots()

    @on_trait_change("attr2", post_init=False)
    def _handle_attr2_changed(self):
        self._update_plots()

With |@observe|, one can stack the decorator on the same method::

    @observe("attr1", post_init=True)
    @observe("attr2", post_init=False)
    def _update_plots(self, event):
        ...

|HasTraits.observe| is not idempotent
`````````````````````````````````````

For most use cases, change handlers can be put up in a fire-and-forget
fashion and they are never removed. However for some use cases, it is important
to remove change handlers when they are no longer needed.

For |HasTraits.on_trait_change|, multiple calls to add a change handler is
equivalent to calling it once and can be undone by one single call with
*remove* set to True. Multiple calls to remove a change handler would not
fail even if the handler no longer exists.

For |HasTraits.observe|, this is no longer true. Calling |HasTraits.observe|
to add an existing change handler will increment an internal reference count.
The change handler can only be completely removed by calling
|HasTraits.observe| the same number of times with *remove* set to True.

In other words::

    foo.observe(handler, "number")
    foo.observe(handler, "number")
    foo.observe(handler, "number")

    foo.number += 1  # handler is called once

    foo.observe(handler, "number", remove=True)
    foo.observe(handler, "number", remove=True)

    foo.number += 1  # handler is still called once

    foo.observe(handler, "number", remove=True)

    foo.number += 1  # handler is not called.

Attempts to remove change handlers that do not exist will also lead to an
exception.

This change in idempotency is introduced in order to support notifications
on an item that appears multiple times in a container.

..
   # substitutions

.. |Expression| replace:: :class:`~traits.observers.expressions.Expression`
.. |Expression.trait| replace:: :func:`~traits.observers.expressions.trait`
.. |Expression.metadata| replace:: :func:`~traits.observers.expressions.metadata`
.. |Expression.dict_items| replace:: :func:`~traits.observers.expressions.dict_items`
.. |Expression.list_items| replace:: :func:`~traits.observers.expressions.list_items`
.. |Expression.set_items| replace:: :func:`~traits.observers.expressions.set_items`
.. |Expression.filter_| replace:: :func:`~traits.observers.expressions.filter_`
.. |Expression.parse| replace:: :func:`~traits.observers.parsing.parse`
.. |Expression.print| replace:: :func:`~traits.observers.expressions.Expression.print`
.. |Expression.then| replace:: :func:`~traits.observers.expressions.Expression.then`
.. |Expression.join_| replace:: :func:`~traits.observers.expressions.join_`

.. |TraitObserverEvent| replace:: :class:`~traits.observers.events.TraitObserverEvent`
.. |ListObserverEvent| replace:: :class:`~traits.observers.events.ListObserverEvent`
.. |DictObserverEvent| replace:: :class:`~traits.observers.events.DictObserverEvent`
.. |SetObserverEvent| replace:: :class:`~traits.observers.events.SetObserverEvent`

.. |HasTraits| replace:: :class:`~traits.has_traits.HasTraits`
.. |@observe| replace:: :func:`~traits.has_traits.observe`
.. |HasTraits.observe| replace:: :func:`~traits.has_traits.HasTraits.observe`

.. |@on_trait_change| replace:: :func:`~traits.has_traits.on_trait_change`
.. |HasTraits.on_trait_change| replace:: :func:`~traits.has_traits.HasTraits.on_trait_change`