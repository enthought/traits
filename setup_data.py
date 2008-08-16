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
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.0')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.0.1')
TRAITSBACKENDQT = etsdep('TraitsBackendQt', '3.0.1')
TRAITSGUI = etsdep('TraitsGUI', '3.0.1')

# Notes:
# - enthought\traits\ui\handler.py and
#   enthought\traits\ui\dockable_view_element.py depend upon files in
#   TraitsGUI[dock]. But the dependencies are all due to calls made to those
#   modules from TraitsGUI[dock] or by features used by TraitsBackendWX. Since
#   TraitsBackendWX depends upon TraitsGUI[dock], and TraitsGUI[dock] depends
#   upon Traits, we opt to omit the TraitsGUI[dock] dependency, since in
#   practice it should not cause any  problems. Leaving the dependency in
#   pulls the TraitsBackendWX egg in, even if it is not needed.


INFO = {
    'extras_require' : {

        # Extra denoting that the standard ETS configuration package should be
        # used. If omitted, Traits will use its own package local configuration,
        # which is a subset of ETS Config containing just the parts used by
        # Traits.  Completely optional, not triggered by any imports.
        'etsconfig': [
            ENTHOUGHTBASE,
            ],

        # Extra denoting that the Traits UI backend for Qt 4.0 should be
        # installed.  Completely optional, not triggered by any imports
        'qt4': [
            TRAITSBACKENDQT,
            ],

        # The Traits UI package is always installed as part of the Traits core
        # egg. This is an extra denoting that the Traits UI should be functional
        # after installation (meaning that all Traits UI modules should load
        # without getting any import errors). Any actual UI's created will only
        # work with the default 'null' backend. You must also install one of
        # the 'real' backends (i.e. 'qt4' or 'wx') if you actually want to
        # create real user interfaces.
        'ui': [
            TRAITSGUI,
            ],

        # Extra denoting that the Traits UI backend for wxPython should be
        # installed.  Completely optional, not triggered by any imports.
        'wx': [
            TRAITSBACKENDWX,
            ],

        # All non-ETS dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'numpy >= 1.1.0',
            ],
        },
    'install_requires' : [
        ],
    'name': 'Traits',
    'version': '3.0.2',
    }
