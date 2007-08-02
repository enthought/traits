#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------
""" Defines the various editors and the editor factory for single-selection
enumerations, for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from editor_factory \
    import EditorFactory

from enthought.traits.api \
    import Any, Bool, Enum, Event, Range, Str

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Supported display modes for a custom style editor
Mode = Enum( 'radio', 'list' )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for enumeration editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Values to enumerate (can be a list, tuple, dict, or a CTrait or
    # TraitHandler that is "mapped"):
    values = Any

    # Extended name of the trait on **object** containing the enumeration data:
    name = Str

    # (Optional) Function used to evaluate text input:
    evaluate = Any

    # Is user input set on every keystroke (when text input is allowed)?
    auto_set = Bool( True )

    # Number of columns to use when displayed as a grid:
    cols = Range( 1, 20 )

    # Display modes supported for a custom style editor:
    mode = Mode

    # Fired when the **values** trait has been updated:
    values_modified = Event
