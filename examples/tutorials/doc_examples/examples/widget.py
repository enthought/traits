#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

from traits.api import Float, HasTraits, Trait


class Part(HasTraits):
    cost = Trait(0.0)


class Widget(HasTraits):
    part1 = Trait(Part)
    part2 = Trait(Part)
    cost = Float(0.0)

    def __init__(self):
        self.part1 = Part()
        self.part2 = Part()
        self.part1.on_trait_change(self.update_cost, 'cost')
        self.part2.on_trait_change(self.update_cost, 'cost')

    def update_cost(self):
        self.cost = self.part1.cost + self.part2.cost
