# traitdict.py --- Example of using TraitDict class
from enthought.traits.api import HasTraits, TraitDict, Trait

class WorkoutClass(HasTraits):
    member_weights = Trait({}, TraitDict(str, float))
    
