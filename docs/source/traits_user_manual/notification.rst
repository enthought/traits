.. _observe-notification:

Trait Notification
==================

When the value of an attribute changes, other parts of the program might need
to be notified that the change has occurred. The Traits package makes this
possible for trait attributes. This functionality lets you write programs
using the same, powerful event-driven model that is used in writing user
interfaces and for other problem domains.

Traits 6.1 introduces a new API for configuring traits notifications:
**observe**, which is intended to fully replace an older API
(**on_trait_change**) in order to overcome some of its limitations and flaws.
While **on_trait_change** is still supported, it may be removed in the future.
See :ref:`on-trait-change-notification` for details on this older API.

Requesting trait attribute change notifications can be done in these
ways:

* Via class definition: By decorating methods on the class with the |@observe|
  decorator to indicate that they handle notification for specified attributes.
* Via instance method: By calling |HasTraits.observe| instance method to establish (or remove) change
  notification handlers.

Via class definition
--------------------

Observers can be defined for every instance of a |HasTraits| subclass by
applying the |@observe| decorator on an instance method. For example, to
observe changes to a specific trait on an object:

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_decorator.py
   :start-at: from traits.api

The decorated function *notify_age_change* is called a **change handler**.
Section :ref:`observe-handler` explains the signature and behaviour expected
for these functions. The value *"age"* is called an **expression**. Section
:ref:`observe-expression` explains how to write an expression for
observing traits and containers following different patterns.

Notice that a change event is emitted at instance construction time because the
initial value is different from the default value. The *post_init* argument can
be used to delay adding the change handler until after the object state is set.

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_post_init.py
   :start-at: @observe
   :lines: 1-3

Via instance method
-------------------

The |HasTraits.observe| method on |HasTraits| is useful for adding or removing
change handlers on a per instance basis. The example above can be rewritten like
this:

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_method.py
   :start-at: from traits.api

The behaviors of the |@observe| decorator and the |HasTraits.observe| instance
are very similar. The only differences are:

* |@observe| decorator does not support removing change handlers.
* |@observe| decorator supports setting up change handlers prior to setting
  object state at instantiation.
* |@observe| decorator sets up change handlers for all instances of a class
  and those change handlers can be inherited by subclasses.

Unless otherwise stated, the following sections apply to both methods for
setting up change notifications.

.. _observe-expression:

The *expression* Parameter
--------------------------
The *expression* parameter in |@observe| provides significant flexibility
in specifying not just attributes directly on the current object, but also
attributes on nested objects and containers.

There are two approaches for creating an expression:

* :ref:`observe-mini-language`
* :ref:`observe-expression-object`

.. _observe-mini-language:

Traits Mini Language
````````````````````
Traits Mini Language is a domain specific language which provides a convenient
and concise way to specify observation rules via a single text. It supports
most of the use cases commonly encountered by users.

.. rubric:: Semantics of Traits DSL

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Pattern
     - Meaning
   * - *attr1\.attr2*
     - Matches a trait named *attr2* on an object referenced by a trait named
       *attr1* on the current object. Changes to *attr1* or *attr2* will
       trigger notifications.
   * - *attr1\:attr2*
     - Matches a trait named *attr2* on an object referenced by a trait named
       *attr1* on the current object. Changes to *attr2* will trigger
       notifications. Changes to *attr1* will not.
   * - *attr1\, attr2*
     - Matches trait named *attr1* or trait named *attr2*.
   * - *items*
     - Matching items in a list or dict or set, or a trait named "items".
   * - [*item1*, *item2*, ..., *itemN*]
     - Matches any of the specified expressions.
   * - *+metadata_name*
     - Matches any trait on the object that has metadata *metadata_name*

.. rubric:: Examples of Traits DSL

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Example
     - Meaning
   * - ``"foo.+updated"``
     - Matches any trait on the *foo* that has a metadata attribute named
       *updated*. Changes on those traits and changes on *foo* will trigger
       notifications.
   * - ``"foo,bar"``
     - Matches traits named *foo* or *bar* on the current object. Changes on
       *foo* or *bar* will trigger notifications.
   * - ``"foo:[bar,baz]"``
     - Matches *foo.bar* or *foo.baz* on the current object. Changes on
       *foo.bar* or *foo.baz* will trigger notifications, but changes on *foo*
       will not trigger notifications.
   * - ``"container.items.value"``
     - If *container* is a list or dict or set, matches the *value* trait on an
       object that is an item of the container. If *container* is an instance
       of *HasTraits*, matches attribute *container.items.value* on the current
       object. Changes to any of these will trigger notifications.
   * - ``"container:items:value"``
     - If *container* is a list or dict or set, matches the *value* trait on an
       object that is an item of the container. If *container* is an instance
       of *HasTraits*, matches attribute *container.items.value* on the current
       object. Only changes to *value* will trigger notifications, assignments
       or mutations on *container* will not trigger notifications.

.. _observe-expression-object:

Expressions as objects
``````````````````````

|ObserverExpression| supports all the use cases supported by the Traits Mini Language
and beyond. Users can compose these objects programmatically and supply
them to |@observe|. These objects are typically constructed using the following
functions from the |observation.api| module.

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Function
     - Purpose
   * - |trait|
     - For observing a specific named trait.
   * - |metadata|
     - For observing multiple traits with specific metadata.
   * - |dict_items|
     - For observing items in a dict.
   * - |list_items|
     - For observing items in a list.
   * - |set_items|
     - For observing items in a set.
   * - |match|
     - For observing traits satisfying a user-defined filter.
   * - |parse|
     - For parsing a string written in Traits domain specific language into an
       expression object.

Users can combine complex expressions using |ObserverExpression.then| or
Python's bitwise-or (`|`) operation.

Most of these functions will have a **notify** argument for setting whether
notifications should be fired for changes.

.. rubric:: Example expressions

* ``trait("attr1")``
   Matches a trait named *attr1* on an object and notifies for changes.

* ``trait("attr1", optional=True)``
   Matches a trait named *attr1* if it is defined. Ignore if it is not defined.

* ``trait("attr1", notify=False).trait("attr2")``
   Matches a trait named *attr2* on an object referenced by a trait named
   *attr1* on the current object. Changes to *attr2* will trigger
   notifications, while changes to *attr1* do not.

* ``trait("foo").list_items().list_items().trait("value")``
   Matches the *value* trait on an item of a nested list in another list
   *foo*. Assignment changes to *foo*, mutations to the lists or changes
   to *value* will trigger notifications.

* ``metadata("updated")``
   Matches any trait on the current that has a metadata attribute named
   *updated*. Changes on those traits will trigger notifications.

* ``trait("foo") | trait("bar")``
   Matches traits named *foo* or *bar* on the current object. Changes on
   *foo* or *bar* will trigger notifications.

* ``trait("foo").then(trait("bar") | trait("baz"))``
   Matches *foo.bar* or *foo.baz* on the current object. Changes on *foo*,
   *foo.bar* or *foo.baz* will trigger notifications.

* ``trait("foo").match(lambda n, t: True)``
   Matches all traits on *foo* on the current object. Changes on *foo* or
   the nested attributes will trigger notifications.

.. rubric:: Extend an expression in text

Using the |parse| function, one can extend an expression in text
with additional features supported by |ObserverExpression|. For example::

    parse("foo.bar").match(lambda name, trait: name.startswith("my_"))

will observe traits with a prefix "my\_" on *foo.bar* on the current object.


.. _observe-handler:

Notification Handler
--------------------

By default, the **handler** is invoked immediately after the change has
occurred. The **dispatch** parameter in |@observe| can be set such that the
handler is dispatched elsewhere to be invoked later (e.g. on a GUI event loop).

The following expectations apply to any change handler:

* It must accept one argument: the **event** parameter (see below)
* It is called **after** a change has occurred
* No assumptions should be made about the order of which handlers are called
  for a given change event. A change event can have many change handlers.
* No exceptions should be raised from a change handler. Any unexpected
  exceptions will be captured and logged.

When the handler is invoked, it is given an **event** object which provides
information about the change observed. The type and signature of *event*
depend on the context of the change. However they all include a parameter
*object* referring to the object being modified:

.. rubric:: Change event types

.. list-table::
   :widths: 15 25
   :header-rows: 1

   * - Change
     - Event Object Type
   * - Attribute value
     - |TraitChangeEvent|
   * - Dict membership
     - |DictChangeEvent|
   * - List membership
     - |ListChangeEvent|
   * - Set membership
     - |SetChangeEvent|


This means if the handler needs to act on the specific details of the change
event, |@observe| should be configured to only notify for that specific type of
changes, or the handler will need to check the type of the event parameter when
it is invoked. The following example shows the first option:

.. literalinclude:: /../../examples/tutorials/doc_examples/examples/observe_different_events.py
   :start-at: from traits.api


Features and fixes provided by |@observe|
-----------------------------------------

In addition to the new flexibility provided by the |ObserverExpression|
object, |@observe| aims at overcoming a number of design flaws and
limitations in the older API. The following sections highlight the differences
and new features supported by |@observe|.

Existence of observed items is checked by default
`````````````````````````````````````````````````

The existence of a trait is checked when the handler is being added to the
instance::

    class Foo(HasTraits):
        name = Str()

        @observe("nam")   # typo, or an omission in renaming
        def _name_updated(self, event):
            print("name changed")

    foo = Foo()   # Error here: Trait named 'nam' not found

There are situations where it is desirable to add the change handler before
a trait is defined.

In that case, the *optional* argument on |trait| can be used:

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


|@observe| decorator can be stacked
```````````````````````````````````

The same handler can be used against different changes and with different
parameters. With |@observe|, one can stack the decorator on the same method::

    @observe("attr1", post_init=True)
    @observe("attr2", post_init=False)
    def _update_plots(self, event):
        ...


Duplicated objects are now monitored
````````````````````````````````````

Consider this example::

    class Apple(HasTraits):
        count = Int(0)

    class Bowl(HasTraits):
        apples = List(Instance(Apple))

        @observe('apples:items:count')
        def print_status(self, event):
            print("Count changed to {event.new}".format(event))

    granny_smith = Apple()
    bowl = Bowl(apples=[granny_smith, granny_smith])
    granny_smith.count += 1    # print: 'Count changed to 1'

The **granny_smith** object is repeated in the **apples** list. When one of the
items is removed from the list, the **granny_smith** object is still there and
we expect a change notification::

    bowl.apples.pop()          # granny_smith is still in the list.
    granny_smith.count += 1    # print: 'Count changed to 2'

In the older API, this situation was not accounted for. With |@observe|, this
situation is handled by keeping a reference count on the observed objects.

This means |HasTraits.observe| cannot be idempotent.


|HasTraits.observe| is not idempotent
`````````````````````````````````````

For most use cases, change handlers can be put up in a fire-and-forget
fashion and they are never removed. However for some use cases, it is important
to remove change handlers when they are no longer needed.

Calling |HasTraits.observe| to add an existing change handler will increment
an internal reference count. The change handler can only be completely removed
by calling |HasTraits.observe| the same number of times with *remove* set to
True.

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


Migration from |@on_trait_change|
---------------------------------

|@observe| can be used alongside |@on_trait_change|. Therefore it is possible
for projects to add new code using |@observe| while slowly migrating existing
code from |@on_trait_change| to |@observe|.

The following sections provide some guide to help migrations.

Observe extended trait names
````````````````````````````

The expression syntax has not changed for extended trait names excluding
containers.

For example, given these classes::

    class Bar(HasTraits):
        value = Int()

    class Foo(HasTraits):
        bar = Instance(Bar)

To observe *bar.value* on an instance of *Foo*, this::

    @on_trait_change("bar.value")

will be changed to this::

    @observe("bar.value")


Observe nested attributes in a container
````````````````````````````````````````

Suppose we have these classes::

    class Bar(HasTraits):
        value = Int()

    class Foo(HasTraits):
        container = List(Instance(Bar))

To notify for changes on *Bar.value* for an item in *Foo.container*,
with |@on_trait_change|, one may do::

    @on_trait_change("container.value")

Where the container nature is deduced at runtime (see
:ref:`trait-items-handlers`).

With |@observe|, one will explicitly specify when items of a container are
being observed, like this::

    @observe("container.items.value")

or::

    @observe(trait("container").list_items().trait("value"))

Similarly, this::

    @on_trait_change("container_items.value")

will be changed to this::

    @observe("container:items.value")

or this::

    @observe(trait("container", notify=False).list_items().trait("value"))

The specially named *name*\_items for listening to container changes is still
defined for supporting |@on_trait_change|. Monitoring this *name*\_items trait
with |@observe| is discouraged as this special trait may be removed when
|@on_trait_change| is removed.


Change handler signature is different
`````````````````````````````````````

|@on_trait_change| supports a range of call
:ref:`signatures <notification-handler-signatures>` for the change handler.
|@observe| supports only one. The single argument contains different content
based on the type of changes being handled (see
:ref:`observe-handler`).

For example, for this handler::

    name = Str()

    @on_trait_change("name")
    def name_updated(self, object, name, old, new):
        print(object, name, old, new)

It will have to be changed to::

    @observe("name")
    def name_updated(self, event):
        print(event.object, event.name, event.old, event.new)


For mutations to container, e.g.::

    container = List()

    @on_trait_change("container_items")
    def name_updated(self, object, name, old, new):
        print("Index: {new.index}")
        print("Added: {new.added}")
        print("Removed: {new.removed}")

It will have to be changed to::

    container = List(comparison_mode=ComparisonMode.identity)

    @observe("container:items")
    def name_updated(self, event):
        print("Index: {event.index}")
        print("Added: {event.added}")
        print("Removed: {event.removed}")


Syntax "[]" is not supported
````````````````````````````

Suppose we have this class::

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
:ref:`observe-handler` for details.


Syntax "-" is not supported
```````````````````````````

With |@on_trait_change|, the syntax *"-metadata_name"* is used to notify
for changes on traits that do NOT have a metadata attribute with the given
name. This usage can be replaced by |match|::

  match(lambda name, trait: trait.metadata_name is None)


Dispatch parameter differentiates observers
```````````````````````````````````````````

In the following example with |@on_trait_change|, the second call is an no-op
because a handler for *"name"* has already been added::

    instance.on_trait_change(handler, "name", dispatch="same")
    instance.on_trait_change(handler, "name", dispatch="ui")    # does nothing

With |@observe|, the **dispatch** parameter is taken into account for
distinguishing observers. The following example will result in the change
handler being called twice, via different dispatching routes::

    instance.observe(handler, "name", dispatch="same")
    instance.observe(handler, "name", dispatch="ui")

Likewise, when removing change handlers, **dispatch** must match the value
used for putting up the observer::

    instance.observe(handler, "name", dispatch="ui")
    instance.observe(handler, "name", dispatch="ui", remove=True)

..
   # substitutions

.. |ObserverExpression| replace:: :class:`~traits.observation.expression.ObserverExpression`
.. |observation.api| replace:: :mod:`~traits.observation.api`
.. |trait| replace:: :func:`~traits.observation.expression.trait`
.. |metadata| replace:: :func:`~traits.observation.expression.metadata`
.. |dict_items| replace:: :func:`~traits.observation.expression.dict_items`
.. |list_items| replace:: :func:`~traits.observation.expression.list_items`
.. |set_items| replace:: :func:`~traits.observation.expression.set_items`
.. |match| replace:: :func:`~traits.observation.expression.match`
.. |parse| replace:: :func:`~traits.observation.parsing.parse`
.. |print| replace:: :func:`~traits.observation.expression.print`
.. |ObserverExpression.then| replace:: :func:`~traits.observation.expression.ObserverExpression.then`

.. |TraitChangeEvent| replace:: :class:`~traits.observation.events.TraitChangeEvent`
.. |ListChangeEvent| replace:: :class:`~traits.observation.events.ListChangeEvent`
.. |DictChangeEvent| replace:: :class:`~traits.observation.events.DictChangeEvent`
.. |SetChangeEvent| replace:: :class:`~traits.observation.events.SetChangeEvent`

.. |HasTraits| replace:: :class:`~traits.has_traits.HasTraits`
.. |@observe| replace:: :func:`~traits.has_traits.observe`
.. |HasTraits.observe| replace:: :func:`~traits.has_traits.HasTraits.observe`

.. |@on_trait_change| replace:: :func:`~traits.has_traits.on_trait_change`
.. |HasTraits.on_trait_change| replace:: :func:`~traits.has_traits.HasTraits.on_trait_change`
