# NOTE: EnthoughtBase should *never* depend on another ETS project!  We need
# to fix the below ASAP!

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
ENVISAGECORE = etsdep('EnvisageCore', '3.1.1')  # -- all from logger.(plugin|agent|widget)
ENVISAGEPLUGINS = etsdep('EnvisagePlugins', '3.1.1')  # -- all from logger.plugin
TRAITS = etsdep('Traits', '3.2.0')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.2.0')  # -- only from e.util.traits.editor.parameter_choice_editor.py
TRAITSGUI = etsdep('TraitsGUI', '3.1.0')  # -- from logger.(agent|plugin|widget)
TRAITS_UI = etsdep('Traits[ui]', '3.2.0')

# The following "soft dependencies" are wrapped in try..except blocks
#APPTOOLS -- util/wx/drag_and_drop
#SCIMATH -- util/wx/spreadsheet/unit_renderer.py


# A dictionary of the setup data information.
INFO = {
    'extras_require' : {
        'agent': [
            ENVISAGECORE,
            TRAITS,
            TRAITSGUI,
            ],
        'distribution': [
            TRAITS_UI,
            ],
        'envisage': [
            ENVISAGECORE,
            ENVISAGEPLUGINS,
            TRAITSGUI,
            TRAITS_UI,
            ],
        'traits': [
            TRAITS,
            TRAITSBACKENDWX,
            ],
        'ui': [    # -- this includes util.ui.* and util.wx.* (see extras.map)
            TRAITSGUI,
            TRAITS_UI,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            ],
        },
    'install_requires' : [
        ],
    'name': 'EnthoughtBase',
    'version': '3.0.3',
    }

