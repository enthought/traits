from setuptools import setup, find_packages


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


# Declare our ETS project dependencies.
APPTOOLS = etsdep('AppTools', '3.0.0b1')  # -- pyface/ui/qt4/resource_manager.py import enthought.resource
#DEVTOOLS -- import of e.debug.fbi and e.developer.helper.fbi only in try..except
MAYAVI = etsdep('Mayavi', '3.0.0a1')  # imports in pyface/ui/qt4/tvtk/*
TRAITS_UI = etsdep('Traits[ui]', '3.0.0b1')
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')
TRAITSGUI_TVTK = etsdep('TraitsGUI[tvtk]', '3.0.0b1') # imports in pyface/ui/qt4/tvtk/*


setup(
    author = 'Phil Thompson',
    author_email = 'phil@riverbankcomputing.co.uk',
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = 'PyQt backend for Traits and Pyface.',
    extras_require = {
        'tvtk': [
            MAYAVI,
            TRAITSGUI_TVTK,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            ],
        },
    include_package_data = True,
    install_requires = [
        APPTOOLS,
        TRAITS_UI,
        TRAITSGUI,
        ],
    license = 'GPL',
    name = 'TraitsBackendQt',
    namespace_packages = [
        "enthought",
        "enthought.pyface",
        "enthought.pyface.ui",
        "enthought.traits",
        "enthought.traits.ui",
        ],
    packages = find_packages(),
    tests_require = [
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = '3.0.0b1',
    zip_safe = False,
    )
