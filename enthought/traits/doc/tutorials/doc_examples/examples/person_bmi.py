from enthought.traits.api import HasTraits, Trait
class Person(HasTraits):
    weight_kg = Trait(0.0)
    height_m =  Trait(1.0)
    bmi = Trait(0.0)

    def _weight_kg_changed(self, old, new):
         print 'weight_kg changed from %s to %s ' % (old, new)
         self.bmi = self.weight_kg / (self.height_m**2)

    def anytrait_changed(self, name, old, new):
         print 'The %s trait changed from %s to %s ' % (name, old, new)


