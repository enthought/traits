"""
testingx imports either Numeric or numpy based
testing modules. See numerix for more information on selectors.
"""
from numerix import which
if which[0]=='numpy':
    from numpy.testing import *
else:
    from scipy_test.testing import *
