#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the HTML editor factory. HTML editors interpret and display 
    HTML-formatted text, but do not modify it.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import true
    
from enthought.traits.ui.basic_editor_factory \
    import BasicEditorFactory
    
from enthought.traits.ui.toolkit \
    import toolkit_object
                    
# Callable that returns the editor to use in the UI.
def html_editor(*args, **traits):
    return toolkit_object('html_editor:SimpleEditor')(*args, **traits)

#------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#------------------------------------------------------------------------------

class ToolkitEditorFactory ( BasicEditorFactory ):
    """ Editor factory for HTML editors.
    """
    #--------------------------------------------------------------------------
    #  Trait definitions:  
    #--------------------------------------------------------------------------
    
    # Should implicit text formatting be converted to HTML?
    format_text = true
    
HTMLEditor = ToolkitEditorFactory(klass = html_editor)

#-EOF--------------------------------------------------------------------------
