#-------------------------------------------------------------------------------
#
#  Minimal setup.py which only builds the C extensions for Traits and
#  only requires the basic distutils.
# 
#  To build for use with a minimal PYTHONPATH setting, call like this:
#  python setup_minimal.py build_ext --inplace
# 
#  Rick Ratzel - 2006-08-31
#
#-------------------------------------------------------------------------------

from distutils.core \
    import setup, Extension

setup(
    name        = "traits",
    version     = "2.1.0",
    ext_modules = [
        Extension( "ctraits", [ "ctraits.c" ] ),
        Extension( "protocols._speedups", [ "protocols/_speedups.c" ] )
    ],
)
