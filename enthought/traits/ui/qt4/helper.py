#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines helper functions and classes used to define PyQt-based trait
    editors and trait editor factories.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from PyQt4 import QtCore, QtGui

from constants \
    import screen_dx, screen_dy
    
from enthought.traits.api \
    import Enum, Trait, CTrait, Instance, Str, BaseTraitHandler, TraitError
    
from enthought.traits.ui.api \
    import View
    
from enthought.traits.ui.ui_traits \
    import SequenceTypes
    
from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Trait definitions:  
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

#-------------------------------------------------------------------------------
#  Positions one window near another:
#-------------------------------------------------------------------------------

def position_near ( origin, target, offset_x = 0, offset_y = 0, 
                                    align_x  = 1, align_y  = 1 ):
    """ Positions one window near another.
    """
    # Calculate the target window position relative to the origin window:                                         
    gpos = origin.mapToGlobal( QtCore.QPoint() )
    x = gpos.x()
    y = gpos.y()
    dx = target.width()
    dy = target.height()
    odx = origin.width()
    ody = origin.height()
    if align_x < 0:
        x = x + odx - dx
    if align_y < 0:
        y = y + ody - dy
    x += offset_x
    y += offset_y
    
    # Position the target window (making sure it will fit on the screen):
    target.move( max( 0, min( x, screen_dx - dx ) ),
                 max( 0, min( y, screen_dy - dy ) ) )
    
#-------------------------------------------------------------------------------
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def restore_window ( ui ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        ui.control.setGeometry( *prefs )
    
#-------------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    geom = ui.control.geometry()
    ui.save_prefs( (geom.x(), geom.y(), geom.width(), geom.height()) ) 

#-------------------------------------------------------------------------------
#  Recomputes the mappings for a new set of enumeration values:
#-------------------------------------------------------------------------------
 
def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """
    
    if isinstance( values, dict ):
        data = [ ( str( v ), n ) for n, v in values.items() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
            col = data[0][0].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]
    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CTrait ):
            handler = handler.handler
        if not isinstance( handler, BaseTraitHandler ):
            raise TraitError, "Invalid value for 'values' specified"
        if handler.is_mapped:
            data = [ ( str( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
        else:
            data = [ ( str( v ), v ) for v in handler.values ]
    else:
        data = [ ( str( v ), v ) for v in values ]
    
    names           = [ x[0] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name
        
    return ( names, mapping, inverse_mapping )  

#-------------------------------------------------------------------------------
#  'GroupEditor' class:
#-------------------------------------------------------------------------------
        
class GroupEditor ( Editor ):
    
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, **traits ):
        """ Initializes the object.
        """
        self.set( **traits )
