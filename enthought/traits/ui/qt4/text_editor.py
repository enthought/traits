#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various text editors and the text editor factory, for the
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Any, Dict, false, Str, true

from editor_factory \
    import EditorFactory

#-------------------------------------------------------------------------------
#  Define a simple identity mapping:
#-------------------------------------------------------------------------------

class _Identity ( object ):
    """ A simple indentity mapping.
    """
    def __call__ ( self, value ):
        return value

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Mapping from user input text to other value
mapping_trait = Dict( Str, Any )

# Function used to evaluate textual user input
evaluate_trait = Any( _Identity() )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for text editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Dictionary that maps user input to other values
    mapping = mapping_trait

    # Is user input set on every keystroke?
    auto_set = true

    # Is user input set when the Enter key is pressed?
    enter_set = false

    # Is multi-line text allowed?
    multi_line = true

    # Is user input unreadable? (e.g., for a password)
    password = false

    # Function to evaluate textual user input
    evaluate = evaluate_trait

    # The object trait containing the function used to evaluate user input
    evaluate_name = Str
