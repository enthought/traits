"""
scipyx imports either numpy or Numeric based scipy_base from old scipy.
"""
from numerix import which
_nx,_vx = which
if _nx=='numeric':
    try:
        import sys
        from scipy_base import *
        sys.modules['enthought.util.scipyx.fastumath'] = fastumath
        sys.modules['enthought.util.scipyx.limits'] = limits
        from scipy import polynomial
        from scipy.stats import get_seed
        import scipy
        def set_seed(seed):
            scipy.stats.seed(seed[0], seed[1])
        
    except ImportError:
        print 'No scipy_base. Will assume numpy.'
        _nx='numpy'

elif _nx=='numpy':
    import sys
    from numpy import *
    try:
        from numpy.oldnumeric import *
    except ImportError:
        pass
    from numpy.core import umath as fastumath
    from scipy.misc import limits
    sys.modules['enthought.util.scipyx.fastumath'] = fastumath
    sys.modules['enthought.util.scipyx.limits'] = limits
    from numpy.lib import polynomial
    from numpy.random import get_state as get_seed
    from numpy.random import set_state as set_seed
else:
    print 'Nothing imported to scipyx'
