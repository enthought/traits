# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# deferring_notification.py -- Example of notification with deferring

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Instance, PrototypedFrom, Str


# --[Code]---------------------------------------------------------------------
class Parent(HasTraits):

    first_name = Str
    last_name = Str

    def _last_name_changed(self, new):
        print("Parent's last name changed to %s." % new)


class Child(HasTraits):

    father = Instance(Parent)
    first_name = Str
    last_name = PrototypedFrom("father")

    def _last_name_changed(self, new):
        print("Child's last name changed to %s." % new)


# --[Example*]-----------------------------------------------------------------
dad = Parent(first_name="William", last_name="Chase")
# Output: Parent's last name changed to Chase.

son = Child(first_name="John", father=dad)
# Output: Child's last name changed to Chase.

# Change Parent's last_name
dad.last_name = "Jones"
# Output: Parent's last name changed to Jones.
#         Child's last name changed to Jones.

# Override Child's last_name
son.last_name = "Thomas"
# Output Child's last name changed to Thomas.

# Change Parent's last_name; Child's is not affected.
dad.last_name = "Riley"
# Output: Parent's last name changed to Riley.

# Reset Child's last_name
del son.last_name
# Output: Child's last name changed to Riley.

# Change to Parent now affects Child.
dad.last_name = "Simmons"
# Output: Parent's last name changed to Simmons.
#         Child's last name changed to Simmons.
