# circular_definition.py --- Non-working example of 
#                            mutually-referring classes
from enthought.traits.api import HasTraits, Trait

class Chicken(HasTraits):
    hatched_from = Trait(Egg)

class Egg(HasTraits):
    created_by = Trait(Chicken)
