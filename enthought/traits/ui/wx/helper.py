#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#  
#  Author: David C. Morrill
#  Date:   10/25/2004
#
#------------------------------------------------------------------------------

""" Defines helper functions used to define wxPython-based trait editors and
trait editor factories.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
import sys

from os.path \
    import join, dirname, abspath
    
from constants \
    import standard_bitmap_width, screen_dx, screen_dy
    
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
#  Data:
#-------------------------------------------------------------------------------

# Bitmap cache dictionary (indexed by filename)
_bitmap_cache = {}

### NOTE: This needs major improvements:

app_path    = None
traits_path = None

#-------------------------------------------------------------------------------
#  Convert an image file name to a cached bitmap:
#-------------------------------------------------------------------------------

def bitmap_cache ( name, standard_size, path = None ):
    """ Converts an image file name to a cached bitmap.
    """
    global app_path, traits_path
    if path is None:
        if traits_path is None:
           import  enthought.traits.ui.wx
           traits_path = join( dirname( enthought.traits.ui.wx.__file__ ), 
                               'images' )
        path = traits_path
    elif path == '':
        if app_path is None:
            app_path = join( dirname( sys.argv[0] ), '..', 'images' )
        path = app_path
    filename = abspath( join( path, name.replace( ' ', '_' ).lower() + '.gif' ))
    bitmap   = _bitmap_cache.get( filename + ('*'[ not standard_size: ]) )
    if bitmap is not None:
        return bitmap
    std_bitmap = bitmap = wx.BitmapFromImage( wx.Image( filename ) )
    _bitmap_cache[ filename ] = bitmap
    dx = bitmap.GetWidth()
    if dx < standard_bitmap_width:
        dy = bitmap.GetHeight()
        std_bitmap = wx.EmptyBitmap( standard_bitmap_width, dy )
        dc1 = wx.MemoryDC()
        dc2 = wx.MemoryDC()
        dc1.SelectObject( std_bitmap )
        dc2.SelectObject( bitmap )
        dc1.SetPen( wx.TRANSPARENT_PEN )
        dc1.SetBrush( wx.WHITE_BRUSH )
        dc1.DrawRectangle( 0, 0, standard_bitmap_width, dy )
        dc1.Blit( (standard_bitmap_width - dx) / 2, 0, dx, dy, dc2, 0, 0 ) 
    _bitmap_cache[ filename + '*' ] = std_bitmap
    if standard_size:
        return std_bitmap
    return bitmap

#-------------------------------------------------------------------------------
#  Positions one window near another:
#-------------------------------------------------------------------------------

def position_near ( origin, target, offset_x = 0, offset_y = 0, 
                                    align_x  = 1, align_y  = 1 ):
    """ Positions one window near another.
    """
    # Calculate the target window position relative to the origin window:                                         
    x, y     = origin.ClientToScreenXY( 0, 0 )
    dx, dy   = target.GetSizeTuple()
    odx, ody = origin.GetSizeTuple()
    if align_x < 0:
        x = x + odx - dx
    if align_y < 0:
        y = y + ody - dy
    x += offset_x
    y += offset_y
    
    # Position the target window (making sure it will fit on the screen):
    target.SetPosition( wx.Point( max( 0, min( x, screen_dx - dx ) ),
                                  max( 0, min( y, screen_dy - dy ) ) ) )
    
#-------------------------------------------------------------------------------
#  Returns an appropriate width for a wxChoice widget based upon the list of
#  values it contains:
#-------------------------------------------------------------------------------
    
def choice_width ( values ):
    """ Returns an appropriate width for a wxChoice widget based upon the list 
        of values it contains:
    """
    return max( [ len( x ) for x in values ] ) * 6
    
#-------------------------------------------------------------------------------
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def restore_window ( ui ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        ui.control.SetDimensions( *prefs )
    
#-------------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    control = ui.control
    ui.save_prefs( control.GetPositionTuple() + control.GetSizeTuple() ) 

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

