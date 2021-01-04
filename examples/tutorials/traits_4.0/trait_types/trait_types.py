# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# --(New Trait Definition Style)-----------------------------------------------
"""
New Trait Definition Style
==========================

The Traits package comes with a number of predefined traits, such as **Str**,
**Int**, **Float**, **Range** and so on. While these core traits suffice for
most common programming situations, quite often the need arises to create a
new *custom* trait.

Traits has always supported creating new traits, but in the past this has
typically involved creating a new **TraitHandler** subclass and invoking the
**Trait** function to define a new trait based on that subclass, as shown in
the following example::

    class OddIntHandler(TraitHandler):

        def validate(self, object, name, value):
            if isinstance(value, int) and ((value % 2) == 1):
                return value

            self.error(object, name, value)

        def info(self):
            return 'an odd integer'

    OddInt = Trait(1, OddIntHandler)

    OddInt = TraitFactory(OddInt)

While not overly complex, nevertheless several developers have complained that
that:

- The process of creating a new trait is not overly intuitive.
- The resulting trait cannot be subclassed to derive a new trait with slightly
  different behavior.

As a result, in Traits 3.0 a new method of defining traits has been added that
hopefully addresses both of these issues. Note that this new style of creating
traits does not replace the old style of creating traits, but is simply a new
technique that can be used instead of the original method. Both old and new
style traits can be defined, used and interoperate in the same program without
any adverse side effects.

OddInt Redux
------------

Using the new style of defining traits, we can rewrite our previous **OddInt**
example as follows::

    class OddInt(BaseInt):

        # Define the default value:
        default_value = 1

        # Describe the trait type:
        info_text = 'an odd integer'

        def validate(self, object, name, value):
            value = super().validate(object, name, value)
            if (value % 2) == 1:
                return value

            self.error(object, name, value)

This provides the exact same functionality as the previous definition of
**OddInt**. There are several points to make about the new definition however:

- The **OddInt** class derives from **BaseInt** (not **TraitHandler**). This
  has several important side effects:

  * **OddInt** can re-use and change any part of the **BaseInt** class behavior
    that it needs to. Note in this case the re-use of the **BaseInt** class's
    *validate* method via the *super* call in **OddInt's** *validate* method.

  * As a subclass of **BaseInt**, it is related to **BaseInt**, which can be
    important both from a documentation and programming point of view. The
    original definition of **OddInt** was related to **BaseInt** only in that
    their names were similar.

- The default value and trait description information are declared as class
  constants. Although there are more dynamic techniques that allow computing
  these values (which will be described in another tutorials), this provides
  a very simple means of defining these values.

- No use of **TraitHandler**, **Trait** or **TraitFactory** is required, just
  good old OO programming techniques. Hopefully this will make the process of
  creating a new trait type a little more understandable to a wider group of
  developers.
"""
# --<Imports>------------------------------------------------------------------
from traits.api import BaseInt, HasTraits


# --[OddInt Definition]--------------------------------------------------------
class OddInt(BaseInt):

    # Define the default value:
    default_value = 1

    # Describe the trait type:
    info_text = "an odd integer"

    def validate(self, object, name, value):
        value = super().validate(object, name, value)
        if (value % 2) == 1:
            return value

        self.error(object, name, value)


# --[Test Class]---------------------------------------------------------------
class Test(HasTraits):

    any_int = BaseInt
    odd_int = OddInt


# --[Example*]-----------------------------------------------------------------

# Create a test object:
t = Test()

# Set both traits to an odd integer value:
t.any_int = 1
print("t.any_int:", t.any_int)

t.odd_int = 1
print("t.odd_int:", t.odd_int)

# Now set them both to an even value (and see what happens):
t.any_int = 2
print("t.any_int:", t.any_int)

t.odd_int = 2
print("t.odd_int:", t.odd_int)  # Should never get here!
