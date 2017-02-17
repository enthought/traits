#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Interfaces)----------------------------------------------------------------
"""
Interfaces
==========

In Traits 3.0, the ability to define, implement and use *interfaces* has been
added to the package.

Defining Interfaces
-------------------

Interfaces are defined by subclassing from the **Interface** class, as shown
in the example below::

    from traits.api import Interface

    class IName(Interface):

        def get_name(self):
            " Returns the name of an object. "

This same code is shown in the **IName Interface** tab of the code.

Interface classes are intended mainly as documentation of the methods and
traits that the interface defines, and should not contain any actual
implementation code, although no check is performed to enforce this currently.

Implementing Interfaces
-----------------------

A class declares that it implements one or more interfaces using the
**implements** function, which has the form::

    implements(interface [, interface2, ..., interfacen])

The semantics of this function is that the class declares that it implements
each of the *interfaces* specified as an argument to **implements**.

Also, the call to **implements** must occur at class scope within the class
definition, as shown in the following example::

    from traits.api import HasTraits, implements

    class Person(HasTraits):

        implements(IName)

        ...

Only a single call to **implements** should occur within a class definition.

Refer to the **Person Class** tab in the code for a complete example of using
**implements**.

Note that in the current version, traits does not check to ensure that the
class containing the **implements** function actually implements the interfaces
it says it does.

Using Interfaces
----------------

Being able to define and implement interfaces would be of little use without
the ability to *use* interfaces in your code. In traits, using an interface is
accomplished using the **Instance** trait, as shown in the following example::

    from traits.api import HasTraits, Instance

    class Apartment(HasTraits):

        renter = Instance(IName)

Using an interface class in an **Instance** trait definition declares that the
trait only accepts values which are objects that either:

- Implement the specified interface.
- Can be adapted to an object that implements the specified interface.

Additional information on what it means to *adapt* an object to implement an
interface is presented in the next section of the tutorial.

As before, the **Instance** trait can also be used with classes that are not
interfaces, such as::

    from traits.api import HasTraits, Instance

    class Apartment(HasTraits):

        renter = Instance(Person)

In this case, the value of the trait must be an object which is an instance of
the specified class or one of its subclasses.
"""
#--<Imports>-------------------------------------------------------------------

from traits.api import *


#--[IName Interface]-----------------------------------------------------------
# Define the 'IName' interface:
class IName(Interface):

    def get_name(self):
        """ Returns the name of an object. """


#--[Person Class]--------------------------------------------------------------
class Person(HasTraits):

    implements(IName)

    first_name = Str('John')
    last_name = Str('Doe')

    # Implementation of the 'IName' interface:
    def get_name(self):
        """ Returns the name of an object. """
        return ('%s %s' % (self.first_name, self.last_name))


#--[Apartment Class]-----------------------------------------------------------
# Define a class using an object that implements the 'IName' interface:
class Apartment(HasTraits):

    renter = Instance(IName)


#--[Example*]------------------------------------------------------------------
# Create an object implementing the 'IName' interface:
william = Person(first_name='William', last_name='Adams')

# Create an apartment, and assign 'renter' an object implementing 'IName':
apt = Apartment(renter=william)

# Verify that the object works correctly:
print 'Renter is:', apt.renter.get_name()
