# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# --(on_trait_change Decorator)------------------------------------------------
"""
on_trait_change Decorator
=========================

Until Traits 3.0, the only way to define a static trait notification handler
as part of a class definition was to define the method following a certain
naming convention::

    def _name_changed(self, ...):
        ...

    or

    def _name_fired(self, ...):
        ...

where *name* is the name of the trait to which the notification handler method
applies.

Starting with Traits 3.0, there is now an alternate method for declaring
notification handlers using the **on_trait_change** decorator. The syntax
for the decorator is::

    @on_trait_change('extended_trait_name')
    def any_method_name(self, ...):
        ...

where *extended_trait_name* is the name of the trait for which the following
method is the notification handler, and *any_method_name* is an arbitrary
method name, which does not need to follow any particular naming convention.

Although the new syntax is more verbose than the original syntax, it has
several advantages:

- It does not require using special method names.
- It allows using the extended trait naming support added to the
  **on_trait_change** method in Traits 3.0.

The last item is especially important since it allows you to statically
declare notification handlers for many more cases than were previously
possible.

For example::

    @on_trait_change('foo,bar,baz')
    def _update(self):
        ...perform update logic...

defines an *_update* method that is called whenever the class's *foo*, *bar*
or *baz* traits change. Previously, this would have required writing three
separate notification handlers (one each for the *foo*, *bar* and *baz*
traits), or adding *event* metadata to each of the trait declarations for
*foo*, *bar* and *baz*.

Similarly, the previous technique of writing methods such as::

    def _bar_changed_for_foo(self, ...):
        ...

which statically defines a notification handler for changes to the *bar* trait
of the object's *foo* trait can now be written as::

    @on_trait_change('foo.bar')
    def any_method_name(self, ...):
        ...

Perhaps even more importantly, this technique can be applied in even more
complex situations, such as::

    @on_trait_change('foo.bar.baz')
    def any_method_name(self, ...):
        ...

    or

    @on_trait_change('foo.+dirty,foo2.[bar,baz,foogle]')
    def any_method_name(self, ...):
        ...

The first case is a simple extension of the previous example, while the
second is a somewhat far-fetched example which can be interpreted as
defining a method that handles:

- Changes to any trait on the object's *foo* trait which has *dirty* metadata
  defined, or
- Changes to the *bar*, *baz* or *foogle* trait of the object's *foo2* trait.

Note that there is one important semantic difference between writing::

    def _name_changed(self, ...):
        ...

and::

    @on_trait_change('name')
    def any_method_name(self, ...):
        ...

While both are recognized as being notification handlers for the object's
*name* trait, the interpretation of the argument signature for the first case
follows the static trait change handler pattern, while the second case follows
the dynamic **on_trait_change** method pattern. While this might seem obvious,
given the fact that the decorator is called *on_trait_change*, it is an
important enough difference to note explicitly.

A Complete Example
------------------

Refer to the code tabs of this lesson for a complete example using the
*on_trait_change* decorator. In particular, look at the definition of the
*sick_again* method in the **Corporation Class** tab.
"""

# --<Imports>------------------------------------------------------------------
from traits.api import HasTraits, Int, List, on_trait_change, Str


# --[Employee Class]-----------------------------------------------------------
class Employee(HasTraits):

    # The name of the employee:
    name = Str

    # The number of sick days they have taken this year:
    sick_days = Int


# --[Department Class]---------------------------------------------------------
class Department(HasTraits):

    # The name of the department:
    name = Str

    # The employees in the department:
    employees = List(Employee)


# --[Corporation Class]--------------------------------------------------------
class Corporation(HasTraits):

    # The name of the corporation:
    name = Str

    # The departments within the corporation:
    departments = List(Department)

    # Define a corporate 'whistle blower' method:
    @on_trait_change("departments:employees.sick_days")
    def sick_again(self, object, name, old, new):
        print(
            "%s just took sick day number %d for this year!"
            % (object.name, new)
        )


# --[Example*]-----------------------------------------------------------------
# Create some sample employees:
millie = Employee(name="Millie", sick_days=2)
ralph = Employee(name="Ralph", sick_days=3)
tom = Employee(name="Tom", sick_days=1)
slick = Employee(name="Slick", sick_days=16)
marcelle = Employee(name="Marcelle", sick_days=7)
reggie = Employee(name="Reggie", sick_days=11)
dave = Employee(name="Dave", sick_days=0)
bob = Employee(name="Bob", sick_days=1)
alphonse = Employee(name="Alphonse", sick_days=5)

# Create some sample departments:
accounting = Department(name="accounting", employees=[millie, ralph, tom])

sales = Department(name="Sales", employees=[slick, marcelle, reggie])

development = Department(name="Development", employees=[dave, bob, alphonse])

# Create a sample corporation:
acme = Corporation(
    name="Acme, Inc.", departments=[accounting, sales, development]
)

# Now let's try out our 'reporting' system:
slick.sick_days += 1
reggie.sick_days += 1
