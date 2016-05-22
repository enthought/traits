#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# deferring_notification.py -- Example of notification with deferring

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Instance, PrototypedFrom, Str


#--[Code]----------------------------------------------------------------------
class Parent(HasTraits):

    first_name = Str
    last_name = Str

    def _last_name_changed(self, new):
        print "Parent's last name changed to %s." % new


class Child(HasTraits):

    father = Instance(Parent)
    first_name = Str
    last_name = PrototypedFrom('father')

    def _last_name_changed(self, new):
        print "Child's last name changed to %s." % new


#--[Example*]------------------------------------------------------------------
dad = Parent(first_name='William', last_name='Chase')
# Output: Parent's last name changed to Chase.

son = Child(first_name='John', father=dad)
# Output: Child's last name changed to Chase.

# Change Parent's last_name
dad.last_name = 'Jones'
# Output: Parent's last name changed to Jones.
#         Child's last name changed to Jones.

# Override Child's last_name
son.last_name = 'Thomas'
# Output Child's last name changed to Thomas.

# Change Parent's last_name; Child's is not affected.
dad.last_name = 'Riley'
# Output: Parent's last name changed to Riley.

# Reset Child's last_name
del son.last_name
# Output: Child's last name changed to Riley.

# Change to Parent now affects Child.
dad.last_name = 'Simmons'
# Output: Parent's last name changed to Simmons.
#         Child's last name changed to Simmons.
