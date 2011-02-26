#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/07/2004
#
#------------------------------------------------------------------------------

""" Defines the text editor factory for all traits toolkit backends.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Dict, Str, Any, Bool

# CIRCULAR IMPORT FIXME: Importing from the source rather than traits.ui.api
# to avoid circular imports, as this EditorFactory will be part of
# traits.ui.api as well.
from ..view import View

from ..group import Group

from ..ui_traits import AView

from ..editor_factory import EditorFactory

#-------------------------------------------------------------------------------
#  Define a simple identity mapping:
#-------------------------------------------------------------------------------

class _Identity ( object ):
    """ A simple identity mapping.
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
    """ Editor factory for text editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Dictionary that maps user input to other values
    mapping = mapping_trait

    # Is user input set on every keystroke?
    auto_set = Bool( True )

    # Is user input set when the Enter key is pressed?
    enter_set = Bool( False )

    # Is multi-line text allowed?
    multi_line = Bool( True )

    # Is user input unreadable? (e.g., for a password)
    password = Bool( False )

    # Function to evaluate textual user input
    evaluate = evaluate_trait

    # The object trait containing the function used to evaluate user input
    evaluate_name = Str

    # The optional view to display when a read-only text editor is clicked:
    view = AView

    #---------------------------------------------------------------------------
    #  Traits view definition:
    #---------------------------------------------------------------------------

    traits_view = View( [ 'auto_set{Set value when text is typed}',
                          'enter_set{Set value when enter is pressed}',
                          'multi_line{Allow multiple lines of text}',
                          '<extras>',
                          '|options:[Options]>' ] )

    extras = Group( 'password{Is this a password field?}' )

# Define the TextEditor class.
TextEditor = ToolkitEditorFactory

### EOF #######################################################################
