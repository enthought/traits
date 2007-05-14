# static_notification.py --- Example of static 
#                            attribute notification
from enthought.traits.api import HasTraits, Trait

class Person(HasTraits):
    weight_kg = Trait(0.0)
    height_m =  Trait(1.0)
    bmi = Trait(0.0)

    def _weight_kg_changed(self, old, new):
         print 'weight_kg changed from %s to %s ' \
                % (old, new)
         if self.weight.kg != 0.0:
             self.bmi = self.weight_kg / (self.height_m**2)

    def anytrait_changed(self, name, old, new):
         print 'The %s trait changed from %s to %s ' \
                % (name, old, new)
"""
>>> bob = Person()
>>> bob.height_m = 1.75
The height_m trait changed from 1.0 to 1.75
>>> bob.weight_kg = 100.0
The weight_kg trait changed from 0.0 to 100.0
weight_kg changed from 0.0 to 100.0
The bmi trait changed from 0.0 to 32.6530612245
"""
