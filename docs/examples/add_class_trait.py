# add_class_trait.py --- Example of mutually-referring 
#                        classes using add_class_trait()
from enthought.traits.api import HasTraits, Trait

class Chicken(HasTraits):
    pass

class Egg(HasTraits):
    created_by = Trait(Chicken)

Chicken.add_class_trait('hatched_from', Egg)

