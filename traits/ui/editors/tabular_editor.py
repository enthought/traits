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
#  Date:   05/20/2007
#
#-------------------------------------------------------------------------------

""" A traits UI editor for editing tabular data (arrays, list of tuples, lists
    of objects, etc).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Str, Bool, Property, List, Enum, Instance

from ..ui_traits import Image

from ..basic_editor_factory import BasicEditorFactory

from ..toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  'TabularEditor' editor factory class:
#-------------------------------------------------------------------------------

class TabularEditor ( BasicEditorFactory ):
    """ Editor factory for tabular editors.
    """

    #-- Trait Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = Property

    # Should column headers (i.e. titles) be displayed?
    show_titles = Bool( True )

    # The optional extended name of the trait used to indicate that a complete
    # table update is needed:
    update = Str

    # Should the table update automatically when the table item's contents
    # change? Note that in order for this feature to work correctly, the editor
    # trait should be a list of objects derived from HasTraits. Also,
    # performance can be affected when very long lists are used, since enabling
    # this feature adds and removed Traits listeners to each item in the list.
    auto_update = Bool( False )

    # The optional extended name of the trait to synchronize the selection
    # values with:
    selected = Str

    # The optional extended name of the trait to synchronize the selection rows
    # with:
    selected_row = Str

    # The optional extended name of the trait to synchronize the activated value
    # with:
    activated = Str

    # The optional extended name of the trait to synchronize the activated
    # value's row with:
    activated_row = Str

    # The optional extended name of the trait to synchronize left click data
    # with. The data is a TabularEditorEvent:
    clicked = Str

    # The optional extended name of the trait to synchronize left double click
    # data with. The data is a TabularEditorEvent:
    dclicked = Str

    # The optional extended name of the trait to synchronize right click data
    # with. The data is a TabularEditorEvent:
    right_clicked = Str

    # The optional extended name of the trait to synchronize right double
    # clicked data with. The data is a TabularEditorEvent:
    right_dclicked = Str

    # The optional extended name of the trait to synchronize column
    # clicked data with. The data is a TabularEditorEvent:
    column_clicked = Str

    # Can the user edit the values?
    editable = Bool( True )

    # Can the user edit the labels (i.e. the first column)
    editable_labels = Bool( False )

    # Are multiple selected items allowed?
    multi_select = Bool( False )

    # Should horizontal lines be drawn between items?
    horizontal_lines = Bool( True )

    # Should vertical lines be drawn between items?
    vertical_lines = Bool( True )

    # The adapter from trait values to editor values:
    adapter = Instance( 'enthought.traits.ui.tabular_adapter.TabularAdapter', () )

    # What type of operations are allowed on the list:
    operations = List( Enum( 'delete', 'insert', 'append', 'edit', 'move' ),
                       [ 'delete', 'insert', 'append', 'edit', 'move' ] )

    # Are 'drag_move' operations allowed (i.e. True), or should they always be
    # treated as 'drag_copy' operations (i.e. False):
    drag_move = Bool( False )

    # The set of images that can be used:
    images = List( Image )

    def _get_klass(self):
        """ Returns the toolkit-specific editor class to be instantiated.
        """
        return toolkit_object('tabular_editor:TabularEditor')

### EOF #######################################################################
