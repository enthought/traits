from traits.api import HasTraits, PrefixMap


class Person(HasTraits):
    married = PrefixMap({'yes': 1, 'no': 0}, default_value="yes")
    married_2 = PrefixMap([], default_value="yes")  # E: arg-type


p = Person()

p.married = "y"
