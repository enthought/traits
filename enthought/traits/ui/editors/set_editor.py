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
""" Defines the set editor factory for all traits user interface toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..editor_factory import EditorWithListFactory
    
from ...api import Bool, Str

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorWithListFactory ):
    """ Editor factory for editors for sets.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Are the items in the set ordered (vs. unordered)?
    ordered = Bool( False )
    
    # Can the user add and delete all items in the set at once?
    can_move_all = Bool( True )
    
    # Title of left column:
    left_column_title = Str
    
    # Title of right column:
    right_column_title = Str

# Define the SetEditor class
SetEditor = ToolkitEditorFactory

### EOF ---------------------------------------------------------------------

