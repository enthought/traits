# explicit.py --- Example of difference between explicit
#                 trait attributes and wildcard or added ones.

from enthought.traits.api import Any, HasTraits, Int, Str

class Person(HasTraits):
    name  = Str
    age   = Int
    temp_ = Any

"""
>>> bob = Person()
>>> bob.temp_lunch = 'sandwich'
>>> bob.add_trait('favorite_sport', Str('football'))
>>> print bob.trait_names()
['trait_added', 'age', 'name']
"""

