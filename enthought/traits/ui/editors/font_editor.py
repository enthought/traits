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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the font editor factory for all traits user interface toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.ui.editor_factory \
    import EditorFactory
    
#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------
class ToolkitEditorFactory ( EditorFactory ): 
    """ Editor factory for font editors.
    """
    pass

    
# Define the FontEditor class
FontEditor = ToolkitEditorFactory


## EOF ########################################################################