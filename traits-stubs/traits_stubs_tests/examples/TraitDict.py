from traits.api import HasTraits, Trait, TraitDict


class WorkoutClass(HasTraits):
    member_weights = Trait({}, TraitDict(str, float))
