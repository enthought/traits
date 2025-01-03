# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, Int


class HasIndex:
    """Class with __index__ method; instances should be assignable to Int."""
    def __index__(self):
        return 1729


class Test(HasTraits):
    i = Int()
    j = Int(default_value="234")  # E: arg-type
    k = Int(default_value=234, something="else")


o = Test()
o.i = 5
o.i = HasIndex()

o.i = "5"  # E: assignment
o.i = 5.5  # E: assignment
o.i = 5.5 + 5  # E: assignment
o.i = str(5)  # E: assignment
o.i = None  # E: assignment


# Test subclassing Int
class Digit(Int):
    def validate(self, object, name, value):
        if isinstance(value, int) and 0 <= value <= 9:
            return value

        self.error(object, name, value)


class TestClass2(HasTraits):
    i = Digit()


obj = TestClass2()
obj.i = 5
obj.i = "5"  # E: assignment
