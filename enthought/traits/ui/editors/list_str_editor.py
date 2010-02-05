#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   05/08/2007
#
#-------------------------------------------------------------------------------

""" Traits UI editor factory for editing lists of strings.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Str, Enum, List, Bool, Instance, Property
    
from ..basic_editor_factory import BasicEditorFactory

from ..toolkit import toolkit_object

from ....pyface.image_resource import ImageResource

#-------------------------------------------------------------------------------
#  'ListStrEditor' editor factory class:
#-------------------------------------------------------------------------------

class ListStrEditor ( BasicEditorFactory ):
    """ Editor factory for list of string editors.
    """
  
    #-- Trait Definitions ------------------------------------------------------
    
    # The editor class to be created:
    klass = Property
    
    # The optional extended name of the trait to synchronize the selection 
    # values with:
    selected = Str
    
    # The optional extended name of the trait to synchronize the selection 
    # indices with:
    selected_index = Str
    
    # The optional extended name of the trait to synchronize the activated value
    # with:
    activated = Str
    
    # The optional extended name of the trait to synchronize the activated 
    # value's index with:
    activated_index = Str
    
    # The optional extended name of the trait to synchronize the right clicked
    # value with:
    right_clicked = Str
    
    # The optional extended name of the trait to synchronize the right clicked
    # value's index with:
    right_clicked_index = Str
    
    # Can the user edit the values?
    editable = Bool( True )
                 
    # Are multiple selected items allowed?
    multi_select = Bool( False )
    
    # Should horizontal lines be drawn between items?
    horizontal_lines = Bool( False )
    
    # The title for the editor:
    title = Str
    
    # The optional extended name of the trait containing the editor title:
    title_name = Str

    # Should a new item automatically be added to the end of the list to allow
    # the user to create new entries?
    auto_add = Bool( False )
           
    # The adapter from list items to editor values:                       
    adapter = Instance( 'enthought.traits.ui.list_str_adapter.ListStrAdapter', 
                        () )
    
    # The optional extended name of the trait containing the adapter:
    adapter_name = Str
    
    # What type of operations are allowed on the list:
    operations = List( Enum( 'delete', 'insert', 'append', 'edit', 'move' ),
                       [ 'delete', 'insert', 'append', 'edit', 'move' ] )
                       
    # Are 'drag_move' operations allowed (i.e. True), or should they always be 
    # treated as 'drag_copy' operations (i.e. False):
    drag_move = Bool( False )
                       
    # The set of images that can be used:                       
    images = List( ImageResource )  
    
    def _get_klass(self):
        """ Returns the editor class to be created.
        """
        return toolkit_object('list_str_editor:_ListStrEditor')
##EOF #########################################################################
