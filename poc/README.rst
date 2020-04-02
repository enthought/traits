Warning: All words "listener" will be renamed to "observer" in
the production code following this PoC.

What this PoC focuses on
------------------------
- What components are needed and what do they do
- How these components interact and relate to each other
- Confirm that the features we need **can** be achieved

What this PoC does not focus on
-------------------------------
- Naming
- Module locations
- Performance
- End-user experience
- Achieving all the features and catching every corner case

Overview
--------

Inside this ``poc`` package:

``observe.observe`` is the top-level function that integrates
all components in order to fulfill the same purpose as the existing
``on_trait_change``.

``observe.observe`` is given:
(1) the user's change handler
(2) the target ``HasTraits`` object to observe
(3) a description on how and what traits are observed

On the item (3), this description is provided via an object called
``ListenerPath``. This replaces the string ``name`` one used to
provide to ``on_trait_change``, e.g. ``"obj1.obj2:value"``.
A ``ListenerPath`` is typically a tree.

As ``observe.observe`` walks down a ``ListenerPath``, it
retrieves the notifiable objects at each node and adds/removes notifiers
to/from these objects. There are three types of notifiers so far:
(1) Notifier for wrapping the user's change handler
(2) Notifier for maintaining downstream listeners when an upstream object
    changes.
(3) Notifier for maintaining downstream listeners when a new trait is
    added to an instance of ``HasTraits`` via ``add_trait``.

Each node on the ``ListenerPath`` is an instance of ``BaseListener``.
These instances only keep information about what traits are being
listened to and whether notifications are required for those changes.
No states should be mutated on these objects as ``observe.observe``
add notifiers onto notifiable objects.

These ``BaseListener`` support ``observe.observe`` with pure query methods.
They report the notifiable objects being listened to at that node, as well
as objects on which the next listener on the path should deal with. These
listeners are context specific (e.g. a listener for listening to items inside
a list), hence they also provide the context specific notifiers for
``observe.observe``.

Next we define ``INotifiableObject`` interface. An object implementing
this interface must have a list of callables to be called
when the object wants to report changes. The list is expected to be
mutated for the purpose of adding or removing callables. For example,
an instance of ``CTrait`` is an notifiable object. An instance of
``TraitListObject`` is also a notifiable object.

These callables in ``INotifiableObject`` are called "notifiers".
In the observer framework, we define a ``INotifier`` interface for
these notifiers. Hence the first requirement of a ``INotifier`` is
that ``__call__`` must be implemented. Note that all
``INotifiableObject`` care is that they have a list of callables they
can call. The ``INotifiableObject`` will define their call signatures
which are expected to be different. It is up to an instance of
``INotifier`` to handle the call arguments.

In order to be able to remove notifiers, it is necessary to keep track
of what notifiers have been added to a notifiable object under what
condition. These states are kept in individual notifiers. Hence notifiers
need to be able to cooperate with one another. The other methods defined
on ``INotifier`` are motivated by this.

Currently there are two concrete implementation of ``INotifier``:
- ``TraitObserverNotifier``
    This wraps the user change handler. It keeps a reference count in order
    to address situations where a same object is repeated inside a container
    and one would not want to fire the same change handler multiple times
    (see enthought/traits#538)
- ``ListenerChangeNotifier``
    This serves the purpose of maintaining downstream listener when a
    container object is changed. For example, it removes downstream notifiers
    when an item is removed from a list, and adds notifiers when an item is
    added to a list.

Both of these concrete notifiers defer the varying notifier call signatures
to an ``event_factory``, which is a callable that adapts the input arguments
to an event object to be sent to the user's change handler.
As an example, one can use an instance of ``mock.Mock`` as an event factory.
