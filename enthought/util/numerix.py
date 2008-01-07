"""Copied and modified this script from the SciPy sources version for
the purposes of TVTK.

numerix imports either Numeric, numarray or numpy based on various
selectors.

0.  If the value "--numarray" or "--numeric" or "--numpy" is specified
on the command line, then numerix imports the specified array package.

1. If the environment variable NUMERIX exists,  it's value is used to
choose Numeric, numarray or numpy.

2. If none of the above is done, the default array package is numpy.
"""

import sys, os

which = None, None

# First, see if --numarray or --Numeric was specified on the command
# line:
if hasattr(sys, 'argv'):        #Once again, Apache mod_python has no argv
    for a in sys.argv:
        if a in ["--Numeric", "--numeric", "--NUMERIC",
                 "--Numarray", "--numarray", "--NUMARRAY",
                 "--NumPy", "--numpy", "--NUMPY", "--Numpy",
                 ]:
            which = a[2:], "command line"
            break
        del a

if os.getenv("NUMERIX"):
    which = os.getenv("NUMERIX"), "environment var"

# If all the above fail, default to numpy.
if which[0] is None:
    which = "numpy", "defaulted"
    try:
        import numpy
        which = "numpy", "defaulted"
    except ImportError,msg1:
        try:
            import Numeric
            which = "numeric", "defaulted"
        except ImportError,msg2:
            try:
                import numarray
                which = "numarray", "defaulted"
            except ImportError,msg3:
                print msg1
                print msg2
                print msg3

which = which[0].strip().lower(), which[1]
if which[0] not in ["numeric", "numarray", "numpy"]:
    raise ValueError("numerix selector must be either 'Numeric' or 'numarray' or 'numpy' but the value obtained from the %s was '%s'." % (which[1], which[0]))

if which[0] == "numarray":
    from numarray import *
    import numarray
    Character = 'c'
    UnsignedInt8 = UInt8
    Int0 = Int8
    Float0 = Float8 = Float16 = Float32
    Complex0 = Complex8 = Complex16 = Complex32
    PyObject = ObjectType
    type2charmap = numarray.typecode
    type2charmap['c'] = 'c'
    version = 'numarray %s'%numarray.__version__
    def typecode(x):
        return x.typecode()
    def iscontiguous(x):
        return x.iscontiguous()
    import cPickle
    def dumps(x):
        return cPickle.dumps(x)
    def loads(s):
        return cPickle.loads(s)
elif which[0] == "numeric":
    from Numeric import *
    from nan_ops_for_numeric import *
    
    import Numeric
    version = 'Numeric %s'%Numeric.__version__
    def typecode(x):
        try:
            return x.typecode()
        except AttributeError:
            return x.dtype.char
    def iscontiguous(x):
        try:
            return x.iscontiguous()
        except AttributeError:
            return x.flags['CONTIGUOUS']

elif which[0] == "numpy":
    from nan_ops_for_numpy import *
    from numpy import *
    try:
        from numpy.oldnumeric import *
    except ImportError:
        pass
    import numpy
    Float8 = Float16 = Float32
    Complex8 = Complex16 = Complex32
    version = 'numpy %s'%numpy.__version__
    def typecode(x):
        try:
            return x.dtype.char
        except AttributeError:
            return x.typecode()        
    def iscontiguous(x):
        try:
            return x.flags['CONTIGUOUS']
        except AttributeError:
            return x.iscontiguous()

    def nonzero(a):
        """ Return the indices of the elements of a which are not zero.
        """

        # fixme: this provides a compatibility layer over a recent change in
        # numpy that makes nonzero() always return tuples.

        ret = numpy.nonzero(a)
        if type(ret) is tuple and len(ret) == 1:
            return ret[0]
        else:
            return ret

    # Determine if we are on a endianness of the current architecture.
    import sys
    little_endian = (sys.byteorder == 'little')
    del sys

    def numeric_array_upgrade(shape, typecode, thestr, 
        Endian=little_endian):
        """ A constructor to upgrade Numeric pickles to numpy arrays without
        needing Numeric to be installed.

        You can use this with sweet_pickle like so:

            from enthought.sweet_pickle import get_global_registry
            get_global_registry().add_mapping('Numeric', 'array_constructor',
                'enthought.util.numerix', 'numeric_array_upgrade')
        """

        # fixme: As of numpy r2610, a similar function is already in numpy as
        # numpy.oldnumeric.compat.array_constructor().

        if typecode == 'O':
            x = numpy.array(thestr, object)
        else:
            x = numpy.fromstring(thestr, typecode)

        x.shape = shape
        if Endian != little_endian:
            return x.byteswap(True)
        else:
            return x
        
    
else:
    raise RuntimeError("invalid numerix selector")

#print 'numerix %s'%version

# ---------------------------------------------------------------
# Common imports and fixes
# ---------------------------------------------------------------

# a bug fix for blas numeric suggested by Fernando Perez
matrixmultiply=dot

