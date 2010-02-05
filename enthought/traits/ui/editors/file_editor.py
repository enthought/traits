#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#  
#  Author: David C. Morrill
#
#------------------------------------------------------------------------------
""" Defines the file editor factory for all traits toolkit backends.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import List, Str, Bool, Int, Unicode
    
# CIRCULAR IMPORT FIXME: Importing from the source rather than traits.ui.api
# to avoid circular imports, as this EditorFactory will be part of 
# traits.ui.api as well.     
from ..view import View

from ..group import Group

from .text_editor import ToolkitEditorFactory as EditorFactory

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Wildcard filter:
filter_trait = List(Unicode)

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for file editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Wildcard filter to apply to the file dialog:
    filter = filter_trait

    # Optional extended trait name of the trait containing the list of filters:
    filter_name = Str

    # Should file extension be truncated?
    truncate_ext = Bool( False )

    # Can the user select directories as well as files?
    allow_dir = Bool( False )

    # Is user input set on every keystroke? (Overrides the default) ('simple' 
    # style only):
    auto_set = False      

    # Is user input set when the Enter key is pressed? (Overrides the default)
    # ('simple' style only):
    enter_set = True

    # The number of history entries to maintain:
    # FIXME: add support
    entries = Int( 10 )

    # Optional extended trait name used to notify the editor when the file 
    # system view should be reloaded ('custom' style only):
    reload_name = Str

    # Optional extended trait name used to notify when the user double-clicks
    # an entry in the file tree view:
    dclick_name = Str
    
    # The style of file dialog to use when the 'Browse...' button is clicked
    # Should be one of 'open' or 'save'
    dialog_style = Str('open')

    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------

    traits_view = View( [ [ '<options>',
                        'truncate_ext{Automatically truncate file extension?}',
                        '|options:[Options]>' ],
                          [ 'filter', '|[Wildcard filters]<>' ] ] )

    extras = Group()
    
# Define the FileEditor class.
FileEditor = ToolkitEditorFactory

## EOF ########################################################################
