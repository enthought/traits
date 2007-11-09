# compound.py --- Example of a compound trait
from enthought.traits.api import Range, Trait

compound = Trait(1, Range(1, 6), 'one', 'two', 
                 'three', 'four', 'five', 'six')
