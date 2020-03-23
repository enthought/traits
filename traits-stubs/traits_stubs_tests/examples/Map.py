from traits.api import HasTraits, Map


class Person(HasTraits):
    married = Map({'yes': 1, 'no': 0}, default_value="yes")
    married_2 = Map([], default_value="yes")  # E: arg-type


p = Person()

p.married = "yes"
