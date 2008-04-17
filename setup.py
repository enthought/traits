from setuptools import setup, Extension, find_packages


ctraits = Extension(
    'enthought.traits.ctraits',
    sources = [ 'enthought/traits/ctraits.c' ],
)

speedups = Extension(
    'enthought.traits.protocols._speedups',
    # fixme: Use the generated sources until Pyrex 0.9.6 and setuptools can play
    # with each other. See #1364
    sources = [ 'enthought/traits/protocols/_speedups.c' ],
)


# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies:
APPTOOLS        = etsdep( 'AppTools',        '3.0.0b1' )  
ENTHOUGHTBASE   = etsdep( 'EnthoughtBase',   '3.0.0b1' )
TRAITSBACKENDWX = etsdep( 'TraitsBackendWX', '3.0.0b1' )
TRAITSBACKENDQT = etsdep( 'TraitsBackendQt', '3.0.0b1' )
TRAITSGUI_DOCK  = etsdep( 'TraitsGUI[dock]', '3.0.0b1' )


setup(
    author       = 'David C. Morrill',
    author_email = 'dmorrill@enthought.com',
    description  = 'Explicitly typed Python attributes package',
    
    extras_require = {
    
        # Extra denoting that the standard ETS configuration package should be 
        # used. If omitted, Traits will use its own package local configuration, 
        # which is a subset of ETS Config containing just the parts used by 
        # Traits.
        
        # Completely optional, not triggered by imports:
        'etsconfig': [
            ENTHOUGHTBASE,
        ],
            
        # Extra denoting that the Traits UI backend for Qt 4.0 should be 
        # installed.

        # Completely optional, not triggered by imports:
        'qt4': [
            TRAITSBACKENDQT,
        ],
            
        # The Traits UI package is always installed as part of the Traits core
        # egg. This is an extra denoting that the Traits UI should be functional 
        # after installation (meaning that all Traits UI modules should load 
        # without getting any import errors). Any actual UI's created will only 
        # work with the default 'null' backend. You must also install one of 
        # the 'real' backends (i.e. 'qt4' or 'wx') if you actually want to 
        # create real user interfaces:
        'ui': [
            TRAITSGUI_DOCK
        ],
            
        # Extra denoting that the Traits UI backend for wxPython should be 
        # installed.

        # Completely optional, not triggered by imports:
        'wx': [
            TRAITSBACKENDWX,
        ],
        
        # Extra denoting that all packages needed to run the Traits unit tests
        # should be installed:
        'test': [
            APPTOOLS,
        ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not:
        'nonets': [
            'numpy >= 1.0.0',
        ],
    },
        
    install_requires = [
    ],
        
    ext_modules          = [ ctraits, speedups ],
    include_package_data = True,
    license              = 'BSD',
    name                 = 'Traits',
    namespace_packages = [
        'enthought',
        'enthought.traits',
        'enthought.traits.ui',
    ],
    packages = find_packages( exclude = [
        'docs',
        'docs.*',
        'integrationtests',
        'integrationtests.*',
    ] ),
    tests_require = [
        'nose >= 0.9',
    ],
    test_suite = 'nose.collector',
    url        = 'http://code.enthought.com/traits',
    version    = '3.0.0b1',
    zip_safe   = False,
)

