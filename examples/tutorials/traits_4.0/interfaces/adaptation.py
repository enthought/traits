#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Adaptation)----------------------------------------------------------------
"""
Adaptation
==========

*Adaptation* is the process of transforming an object that does not implement
a specific interface, or set of interfaces, into one that does.

Defining Adapters
-----------------

In traits, an *adapter* is a special type of class whose role is to *transform*
some type of object which does not implement a specific interface, or set of
interfaces, into one that does.

Traits provides several different ways of writing adapters. We'll begin with
the simplest way, which is to create a subclass of **Adapter**.

Subclassing Adapter
-------------------

The **Adapter** base class is designed specifically for creating adapter
classes. It is actually a very simple class which streamlines the process of
creating new adapter classes by:

- Providing a standard constructor which normally does not need to be
  overridden by subclasses.

- Only requiring use of the **adapts** function to define the adapter.

The standard constructor for the **Adapter** class has the form::

    adapter_subclass_name(object_to_be_adapted)

where *adapter_subclass_name* is the name of the **Adapter** subclass.

The only thing the constructor does is::

    self.adaptee = object_to_be_adapted

which assigns the object being adapted to the *adaptee* trait.

As an adapter writer, the only things you need to add to the subclass
definition are:

- An **adapts** function call declaring which interfaces the adapter class
  implements on behalf of the object it is adapting.

  The form of the **adapts** function is as follows::

    adapts(client_class, interface [, interface2, ..., interfacen])

- A declaration for the *adaptee* trait (usually as an **Instance** of a
  particular class).

- The actual implementations of the interfaces declared in the **adapts**
  call. Usually the implementation code will be written in terms of the
  adapter class's *adaptee* trait assigned by the class constructor.

The following shows the definition of a simple adapter class::

  from traits.api import Adapter, Instance, implements

  class PersonINameAdapter (Adapter):

      # Declare what interfaces this adapter implements for its client:
      adapts(Person, IName)

      # Declare the type of client it supports:
      adaptee = Instance(Person)

      # Implement the 'IName' interface on behalf of its client:
      def get_name (self):
          return ('%s %s' % (self.adaptee.first_name, self.adaptee.last_name))

Rolling You Own Adapter Classes
-------------------------------

Note that using the **Adapter** base class is simply a convenience. It is not
necessary for an adapter class to derive from **Adapter**. However, if you do
not derive your adapter class from **Adapter**, then it is your responsibility
to provide all of the same information and setup implicitly provided by
**Adapter**.

In particular, in addition to using the *adapts* function to declare the set of
interfaces the class implements for its client object, you must also define the
constructor, or whatever means you define for binding the object to be adapted
to the adapter.

Creating an adapter class from scratch, we can re-write the previous adapter
example as follows::

  from traits.api import HasTraits, Instance, adapts

  class PersonINameAdapter(HasTraits):

      # Declare what interfaces this adapter implements, and for who:
      adapts(Person, IName)

      # Declare the type of client it supports:
      client = Instance(Person)

      # Implement the adapter's constructor:
      def __init__ (self, client):
          self.client = client

      # Implement the 'IName' interface on behalf of its client:
      def get_name (self):
          return ('%s %s' % (self.client.first_name, self.client.last_name))

As you can see, the main difference between this example and the last is:

- Explicit implementation of the adapter constructor.

Yet Another Way To Define Adapters
----------------------------------

It is also possible to declare a class to be an adapter class external to the
class definition itself, as shown in the following example::

    class AnotherPersonAdapter (object):

        # Implement the adapter's constructor:
        def __init__ (self, person):
            self.person = person

        # Implement the 'IName' interface on behalf of its client:
        def get_name (self):
            return ('%s %s' % (self.person.first_name, self.person.last_name))

    ...

    adapts(AnotherPersonAdapter, Person, IName)

When used in this way, the form of the **adapts** function is::

    adapts(adapter_class, client_class, interface [, interface2, ...,
           interfacen])

This form simply inserts the adapter class as the first argument (when
**adapts** is used inside of a class definition, this information is implicitly
available from the class itself).

Using Adapters
--------------

Now for the good part... how do you use adapters?

And the answer is... you don't. At least not explicitly.

In traits, adapters are created automatically whenever you assign an object to
an *interface* **AdaptsTo** or **AdaptedTo** trait and the object being
assigned does not implement the required interface. In this case, if an
adapter class exists that can adapt the specified object to the required
interface, an instance of the adapter class will be created for the object,
and the resulting adapter object is what ends up being assigned to the trait,
along with the original object. When using the **AdaptedTo** trait, the
adapter is assigned as the value of the trait, and the original object is
assigned as its *mapped* value. For the **AdaptsTo** trait, the original
object is assigned as the trait value, and the adapter is assigned as its
*mapped* value. In the case where the object does not require an adapter, the
object and adapted value are the same.

Note that it might happen that no adapter class exists that will adapt the
object to the required interface, but a pair, or series, of adapter classes
exist that will together adapt the object to the needed interface. In this
case, the required set of adapters will automatically be created for the
object and the final link in the chain adapter object (the one that actually
implements the required interface for some object class) will be used.

Whenever a situation like this arises, the adapted object used will always
contain the smallest set of available adapter objects needed to adapt the
original object.

The following code shows a simple example of using adaptation::

    # Create a Person object (which does not implement the 'IName' interface):
    william = Person(first_name = 'William', last_name = 'Adams')

    # Create an apartment, and assign 'renter' the previous object. Since
    # the value of 'renter' must implement 'IName', a 'PersonINameAdapter'
    # object is automatically created and assigned:
    apt = Apartment(renter = william)

    # Verify that the resulting value implements 'IName' correctly:
    print 'Renter is: ', apt.renter.get_name()

    # Check the type of object actually assigned to 'renter':
    print apt.renter

Refer to the **Output** tab for the actual result of running this example.

Controlling Adaptation
----------------------

The **AdaptedTo** and **AdaptsTo** traits are actually subclasses of the
**Instance** trait. Normally, adaptation occurs automatically when values are
assigned to an **AdaptedTo** or **AdaptsTo** trait. However, any of the
**Instance**, **AdaptedTo** and **AdaptsTo** traits allow you to control how
adaptation is performed by means of the *adapt* metadata, which can have one of
the following values:

no
    Adaptation is not allowed (This is the default for the **Instance** trait).

yes
    Adaptation is allowed. If adaptation fails, an exception is raised (This is
    the default for both the **AdaptedTo** and **AdaptsTo** traits).

default
    Adapation is allowed. If adaptation fails, the default value for the trait
    is assigned instead.

As an example of modifying the adaptation behavior of an **AdaptedTo** trait,
we could rewrite the example **Apartment** class as follows::

    class Apartment(HasTraits):

        renter = AdaptedTo(IName, adapt = 'no')

Using this definition, any value assigned to *renter* must itself implement
the **IName** interface, otherwise an exception is raised. Try modifying and
re-running the example code to verify that this is indeed the case.
"""

#--<Imports>-------------------------------------------------------------------

from traits.api import *


#--[IName Interface]-----------------------------------------------------------
# Define the 'IName' interface:
class IName (Interface):

    def get_name(self):
        """ Returns the name of an object. """


#--[Person Class]--------------------------------------------------------------
class Person(HasTraits):

    first_name = Str('John')
    last_name = Str('Doe')


#--[PersonINameAdapter Class]--------------------------------------------------
class PersonINameAdapter(Adapter):

    # Declare what interfaces this adapter implements for its client:
    adapts(Person, IName)

    # Declare the type of client it supports:
    adaptee = Instance(Person)

    # Implementation of the 'IName' interface on behalf of its client:
    def get_name(self):
        """ Returns the name of an object. """
        return ('%s %s' % (self.adaptee.first_name, self.adaptee.last_name))


#--[Apartment Class]-----------------------------------------------------------
# Define a class using an object that implements the 'IName' interface:
class Apartment(HasTraits):

    renter = AdaptedTo(IName)


#--[Example*]------------------------------------------------------------------
# Create an object implementing the 'IName' interface:
william = Person(first_name='William', last_name='Adams')

# Create an apartment, and assign 'renter' an object implementing 'IName':
apt = Apartment(renter=william)

# Verify that the object works correctly:
print 'Renter is:', apt.renter.get_name()

# Check the type of object actually assigned to 'renter':
print apt.renter
