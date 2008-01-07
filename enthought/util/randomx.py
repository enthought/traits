"""
randomx imports either Numeric, numarray or numpy based
random modules. See numerix for more information on selectors.
"""
from numerix import which
if which[0]=='numpy':
    from numpy.random import *
    _numpy_random_seed = seed
    def seed(*args):
        if len(args)>1:
            return _numpy_random_seed(args)
        return _numpy_random_seed(*args)
elif which[0]=='numarray':
    from numarray.random_array import *
elif which[0]=='numeric':
    from RandomArray import *
