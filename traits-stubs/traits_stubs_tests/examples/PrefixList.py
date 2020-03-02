from traits.api import HasTraits, PrefixList


class Person(HasTraits):
    atr = PrefixList('yes', 'no')
    atr2 = PrefixList(('yes', 'no'))
    atr3 = PrefixList(['yes', 'no'])


p = Person()
p.atr = 5  # E: assignment
