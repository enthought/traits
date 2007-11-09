# multiple_criteria.py -- Example of multiple criteria 
#                         in a trait definition
from enthought.traits.api import HasTraits, Trait
from types import TupleType

class Nonsense(HasTraits):
    rubbish = Trait(0.0, 0.0, 'stuff', TupleType)
