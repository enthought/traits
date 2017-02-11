#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# interface_implementation.py - Example of implementing an interface

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, implements, Str, Instance
from interface_definition import IName


#--[Code]----------------------------------------------------------------------
class Person(HasTraits):
    implements(IName)

    first_name = Str('John')
    last_name = Str('Doe')

    # Implementation of the 'IName' interface:
    def get_name(self):
        """ Returns the name of an object. """
        return ('%s %s' % (self.first_name, self.last_name))


#--[Example*]------------------------------------------------------------------
class Apartment(HasTraits):
    renter = Instance(IName)

william = Person(first_name='William', last_name='Adams')
apt1 = Apartment(renter=william)
print 'Renter is: ', apt1.renter.get_name()
# Result: Renter is: William Adams
