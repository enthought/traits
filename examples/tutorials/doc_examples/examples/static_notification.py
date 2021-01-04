# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# static_notification.py --- Example of static attribute notification

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Float


# --[Code]---------------------------------------------------------------------
class Person(HasTraits):
    weight_kg = Float(0.0)
    height_m = Float(1.0)
    bmi = Float(0.0)

    def _weight_kg_changed(self, old, new):
        print("weight_kg changed from %s to %s " % (old, new))
        if self.height_m != 0.0:
            self.bmi = self.weight_kg / (self.height_m ** 2)

    def _anytrait_changed(self, name, old, new):
        print("The %s trait changed from %s to %s " % (name, old, new))


# --[Example*]-----------------------------------------------------------------
bob = Person()
bob.height_m = 1.75
# Output: The height_m trait changed from 1.0 to 1.75
bob.weight_kg = 100.0
# Output:
# The weight_kg trait changed from 0.0 to 100.0
# weight_kg changed from 0.0 to 100.0
# The bmi trait changed from 0.0 to 32.6530612245
