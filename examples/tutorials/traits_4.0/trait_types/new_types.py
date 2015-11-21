#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Creating New Trait Types)--------------------------------------------------
"""
Creating New Trait Types
========================

You create a *new style* trait type by subclassing the **TraitType** class or
one of its subclasses, such as **Float** or **Str**. **TraitType** provides
the infrastructure for creating a trait type and allows subclasses to define
specific methods and class constants used to create either a new trait *type*
or *property*.

In the next section, we'll cover the methods and class constants used to define
a new trait *type*, and in the section following that we'll show how to define
a new trait *property*.

Defining a New Trait Type
-------------------------

The thing that distinguishes a trait *type* from a *property* is the existence
of a *validate* method in the subclass. The *validate* method should have the
following signature:

validate(self, object, name, value)
    This method validates, coerces, or adapts the specified *value* as the
    value of the *name* trait of the *object* object. This method is called
    when a value is assigned to an object trait that is based on this subclass
    of *TraitType* and the class does not  contain a definition for either the
    *get()* or *set()* methods.

    The method must return the original *value* or any suitably coerced or
    adapted value that is a legal value for the trait. If *value* is  not a
    legal value for the trait, and cannot be coerced or adapted to a legal
    value, the method should either raise a **TraitError** or  call the
    *error()* method to raise a **TraitError** on its behalf.

In addition to *validate*, the subclass can also define the *post_setattr*
method, which should have the following signature:

post_setattr(self, object, name, value)
    This method allows the trait to do additional processing after *value* has
    been successfully assigned to the *name* trait of the *object* object. For
    most traits there is no additional processing that needs to be done, and
    this method need not be defined. It is normally used for creating *shadow*
    (i.e., *mapped* traits), but other uses may arise as well. This method does
    not need to return a value, and should normally not raise any exceptions.

The subclass can also define a constant default value by setting the class-
level *default_value* attribute to the desired constant value. For example::

    class OddInt(Int):

        default_value = 1

        ...

If a non-constant default value is desired, you should override the
**TraitType** class's *get_default_value* method. Refer to the documentation
for the **TraitType** class for more information on what this method does.

If you have a constant string that can be used as the type's *info* value, you
can provide it by simple setting the string as the value of the class-level
*info_text* attribute::

    class OddInt(Int):

        info_text = 'an odd integer'

        ...

If you have a type info string which depends upon the internal state of the
trait, then you should override the **TraitType's** *info* method. This method
has no arguments, and should return a string describing the values accepted by
the trait type (e.g. 'an integer in the range from 1 to 5').

If you also have some type specific initialization that needs to be performed
when the trait type is created, you can also override the **TraitType** class's
*init* method. This method has no arguments and is automatically called from
the **TraitType** class constructor.

If you would like to specify a default Traits UI editor for your new trait
type, you can also override the **TraitType** class's *create_editor* method,
which has no arguments and should return the default **TraitEditor** for any
instances of the type to use.

This provides a basic overview of the basic methods and class constants needed
to define a new trait type. Refer to the complete documentation for the
**TraitType** and **BaseTraitHandler** classes for more information on other
methods that can be overridden if necessary.

Defining a New Trait Property
-----------------------------

You can also define new trait *properties* by subclassing from **TraitType** or
one of its subclasses. A *property* is distinguished from a *type* by the
existence of a *get* and/or *set* method in the **TraitType** subclass. The
signature for these two methods is as follows:

get(self, object, name)
    This is the *getter* method of a trait that behaves like a property. It has
    the following arguments:

    object
        The object that the property applies to.
    name
        The name of the *object* property.

    If this method is not defined, but the *set* method is defined, the trait
    behaves like a *write-only* property. This method should return the value
    of the *name* property for the *object* object.

set(self, object, name, value)
    This is the *setter* method of a trait that behaves like a property. It has
    the following arguments:

    object
        The object the property applies to.
    name
        The name of the property on *object*.
    value
        The value being assigned as the value of the property.

    If this method is not defined, but the *get* method is defined, the trait
    behaves like a *read-only* property. This method does not need to return a
    value, but it should raise a **TraitError** exception if the specified
    *value* is not valid and cannot be  coerced or adapted to a valid value.

Because the value of a *property* is determined by the *get* method, the
*default_value* class constant and *get_default_value* method are not used.

However, all other values and methods, such as the *info_text* class attribute
and *info* method apply to a *property* as well as a normal type. Please refer
to the preceding section on defining a trait type for additional information
that applies to properties as well.
"""

#--<Imports>-------------------------------------------------------------------

from traits.api import *


#--[DiceRoll Type]-------------------------------------------------------------
# Define a type whose value represents the roll of a pair of dice:
class DiceRoll(TraitType):

    # Set default value to 'snake-eyes':
    default_value = (1, 1)

    # Describe the type:
    info_text = ('a tuple of the form (n,m), where both n and m are integers '
                 'in the range from 1 to 6 representing a roll of a pair of '
                 'dice')

    # Validate any value assigned to the trait to make sure it is a valid
    # dice roll:
    def validate(self, object, name, value):
        if (isinstance(value, tuple) and (len(value) == 2) and
                (1 <= value[0] <= 6) and (1 <= value[1] <= 6)):
            return value

        self.error(object, name, value)

#--[RandInt Property]----------------------------------------------------------

from random import randint


# Define a read-only property whose value is a random integer in a specified
# range:
class RandInt(TraitType):

    # Define the type's constructor:
    def __init__(self, low=1, high=10, **metadata):
        super(RandInt, self).__init__(**metadata)
        self.low = int(low)
        self.high = int(high)

    # Define the property's getter:
    def get(self):
        return randint(self.low, self.high)

    # Define the type's type information:
    def info(self):
        return ('a random integer in the range from %d to %d' %
               (self.low, self.high))

#--[Craps Class]---------------------------------------------------------------


# Define a test class containing both new trait types/properties:
class Craps(HasTraits):

    rolls = List(DiceRoll)
    die = RandInt(1, 6)

#--[Example*]------------------------------------------------------------------

# Create a test object:
craps = Craps()

# Add a number of test dice rolls:
for i in range(10):
    craps.rolls.append((craps.die, craps.die))

# Display the results:
print craps.rolls

# Try to assign an invalid dice roll:
try:
    craps.rolls.append((0, 0))
except TraitError:
    print 'Assigning an invalid dice roll failed.'
