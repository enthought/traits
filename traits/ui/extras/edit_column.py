#------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Bryce Hendrix
#  Date:   09/13/2007
#
#------------------------------------------------------------------------------

""" Defines the table column descriptor used for editing the object represented
    by the row
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ....etsconfig.api import ETSConfig
from ..table_column import ObjectColumn

if ETSConfig.toolkit == 'wx':
    from ....pyface.ui.wx.grid.edit_renderer import EditRenderer
else:
    raise NotImplementedError, "No EditColumn implementation for backend"

#-------------------------------------------------------------------------------
#  'EditColumn' class:
#-------------------------------------------------------------------------------

class EditColumn ( ObjectColumn ):

    def __init__ ( self, **traits ):
        """ Initializes the object.
        """
        super( EditColumn, self ).__init__( **traits )

        # force the renderer to be a edit renderer
        self.renderer = EditRenderer()

        self.label = ''

    def get_cell_color ( self, object ):
        """ Returns the cell background color for the column for a specified
            object.
        """

        # Override the parent class to ALWAYS provide the standard color:
        return self.cell_color_

    def is_editable ( self, object ):
        """ Returns whether the column is editable for a specified object.
        """
        return False

