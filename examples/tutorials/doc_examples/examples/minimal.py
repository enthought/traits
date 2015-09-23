#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# minimal.py --- Minimal example of using traits.

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Float, TraitError


#--[Code]----------------------------------------------------------------------
class Person(HasTraits):
    weight = Float(150.0)


#--[Example*]------------------------------------------------------------------
# instantiate the class
joe = Person()

# Show the default value
print joe.weight

# Assign new values
joe.weight = 161.9     # OK to assign a float
print joe.weight

joe.weight = 162       # OK to assign an int
print joe.weight

# The following line causes a traceback:
try:
    joe.weight = 'average'  # Error to assign a string
    print "You should not see this message."
except TraitError:
    print "You can't assign a string to the 'weight' trait."
