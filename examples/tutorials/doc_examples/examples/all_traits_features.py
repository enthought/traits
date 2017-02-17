#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.


# all_traits_features.py --- Shows primary features of the Traits
#                            package

#--[Imports]-------------------------------------------------------------------
from traits.api import Delegate, HasTraits, Instance, Int, Str


#--[Code]----------------------------------------------------------------------
# Shows the five primary features of the Traits package.
class Parent(HasTraits):

    # INITIALIZATION: last_name' is initialized to '':
    last_name = Str('')


class Child(HasTraits):

    age = Int

    # VALIDATION: 'father' must be a Parent instance:
    father = Instance(Parent)

    # DELEGATION: 'last_name' is delegated to father's 'last_name':
    last_name = Delegate('father')

    # NOTIFICATION: This method is called when 'age' changes:
    def _age_changed(self, old, new):
        print 'Age changed from %s to %s ' % (old, new)

#--[Example*]------------------------------------------------------------------

# Set up the example:
joe = Parent()
joe.last_name = 'Johnson'
moe = Child()
moe.father = joe

# DELEGATION in action:
print "Moe's last name is %s " % moe.last_name
# Result:
# Moe's last name is Johnson

# NOTIFICATION in action
moe.age = 10
# Result:
# Age changed from 0 to 10

# VISUALIZATION: Displays a UI for editing moe's
# attributes (if a supported GUI toolkit is installed)
moe.configure_traits()
