from traits.api import HasTraits, PrefixList


class Person(HasTraits):
    atr1 = PrefixList(('yes', 'no'))
    atr2 = PrefixList(['yes', 'no'])


p = Person()
p.atr1 = 5  # E: assignment
