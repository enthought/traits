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
#  Date: 01/14/2005
#
#------------------------------------------------------------------------------

""" Defines the plot editor and the plot editor factory, for the wxPython user 
interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import List, Str, Bool, Range, Tuple, RGBAColor
    
from enthought.traits.ui.api \
    import View, Item, EnableRGBAColorEditor
    
from editor_factory \
    import EditorFactory
    
from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------

WindowColor = ( 236.0 / 255.0, 233.0 / 255.0, 216.0 / 255.0, 1.0 )

#-------------------------------------------------------------------------------
#  Trait definitions:  
#-------------------------------------------------------------------------------

# Range of values for an axis
AxisRange =  Tuple( ( 0.0, 1.0, 0.01 ), 
                    labels = [ 'Low', 'High', 'Step' ],
                    cols   = 3 )
                    
# Minimum and maximum axis bounds                    
AxisBounds = Tuple( ( 0.0, 1.0 ),
                    labels = [ 'Min', 'Max' ],
                    cols   = 2 )

# Height and width range for the plot widget                   
PlotSize = Range( 50, 1000, 180 )

# Range of plot line weights
LineWeight = Range( 1, 9, 3 )

# Defines the color editor to use for various color traits
color_editor = EnableRGBAColorEditor( auto_set = False )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for plot editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # List of traits the plot is associated with:
    traits = List( Str )  
    
    # Plot title:
    title = Str
    
    # X-axis label:
    x_label = Str 
    
    # Y-axis label:
    y_label = Str 
    
    # X-axis range:
    x_range = AxisRange
    
    # Name of handler method to compute x values:
    x_values = Str          
    
    # Name of handler method to compute y values:
    y_values = Str          
    
    # Should the X-axis bounds be automatically computed?
    x_auto = Bool( True )
    
    # X-axis bounds (i.e., minimum and maximum values):
    x_bounds = AxisBounds
    
    # Should the Y-axis bounds be automatically computed?
    y_auto = Bool( True )
    
    # Y-axis bounds (i.e., minimum and maximum values):
    y_bounds = AxisBounds   
    
    # Width of the plot editor:
    width = PlotSize     
    
    # Height of the plot editor:
    height = PlotSize     
    
    # Weight of plot line (i.e. line thickness):
    weight = LineWeight   
    
    # Line color: 
    color = RGBAColor( 'blue',  editor = color_editor )
    
    # Background color:
    bg_color = RGBAColor( 'white', editor = color_editor )
    
    #---------------------------------------------------------------------------
    #  Traits view definition:    
    #---------------------------------------------------------------------------
        
    traits_view = View( [ [ 'traits',
                            '|[Trait Names]<>' ],
                          [ 'title', 'x_label', 'y_label', 
                            '|[Labels]' ],
                          [ 'y_values', '_', 'x_values',
                            Item( 'x_range', 
                                  enabled_when = "object.x_values == ''" ),
                            '|[Plot Values]' ],
                          [ [ 'x_auto',
                              Item( 'x_bounds',
                                    enabled_when = "not object.x_auto" ),
                              '-' ],
                            [ 'y_auto',
                              Item( 'y_bounds',
                                    enabled_when = "not object.y_auto" ),
                              '-' ],
                            '|[Plot bounds]' ],
                          [ 'width', 'height',
                            '-[Plot Size]' ],
                          [ 'weight{Line Weight}', '_', 
                            'color{Line Color}', 
                            'bg_color{Background color}',
                            '|[Plot Attributes]' ]
                        ] )
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return PlotEditor( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description )
    
    def text_editor ( self, ui, object, name, description, parent ):
        return PlotEditor( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description )
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return PlotEditor( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description )

#-------------------------------------------------------------------------------
#  'PlotEditor' class  
#-------------------------------------------------------------------------------
                     
class PlotEditor ( Editor ):
    """ Editor for displaying trait values in a Chaco plot.
    """
    
    # Indicate that the plot can use extra space in the view:
    scrollable = True
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        from enthought.chaco.wx.plot \
            import PlotAxis, PlotComponent, PlotTitle, PlotValue

        from enthought.enable.wx \
            import Window
            
        factory = self.factory
        x_axis  = PlotAxis()
        if not factory.x_auto:
            x_axis.bound_low  = min( *factory.x_bounds )
            x_axis.bound_high = max( *factory.x_bounds )
        if factory.x_label != '':
            x_axis.title = factory.x_label
        y_axis = PlotAxis()
        if not factory.y_auto:
            y_axis.bound_low  = min( *factory.y_bounds )
            y_axis.bound_high = max( *factory.y_bounds )
        if factory.y_label != '':
            y_axis.title = factory.y_label
        self._pv = pv = PlotValue( line_color    = factory.color,
                                   line_weight   = factory.weight,
                                   bg_color      = WindowColor,
                                   plot_bg_color = factory.bg_color,
                                   axis_index    = x_axis,
                                   axis          = y_axis )
                                   
        if factory.title != '':
            pv.add( PlotTitle( text = factory.title ) )
            
        window = Window( parent, component = PlotComponent( component = pv ) )
        self.control = control = window.control
        control.SetSize( ( factory.width, factory.height ) )
        
        for name in factory.traits:
            object, name, value = self.parse_extended_name( name )
            object.on_trait_change( self._update_editor, name,
                                    dispatch = 'ui' ) 
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( PlotEditor, self ).dispose()
        
        for name in self.factory.traits:
            object, name, value = self.parse_extended_name( name )
            object.on_trait_change( self._update_editor, name, 
                                    remove = True )
            
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        from enthought.chaco.wx.plot import PlotValue
        from numpy import arange
        
        factory  = self.factory
        
        x_values = None
        if factory.x_values != '':
            try:
                x_values = getattr( self.ui.handler, factory.x_values )(
                                    self.ui.info )
            except:
                try:
                    x_values = getattr( self.object, factory.x_values )
                except:
                    pass
                    
        if x_values is None:
            try:
                low, high, step = factory.x_range
                x_values = arange( low, high + (step / 2.0), step )
            except:
                x_values = arange( 0.0, 1.005, 0.01 )
                
        try:
            y_values = getattr( self.ui.handler, factory.y_values )( 
                                self.ui.info, x_values )
        except:
            try:
                y_values = getattr( self.object, factory.y_values )
            except:
                t = x_values - 0.5
                y_values = t * t
                
        self._pv.set( data = y_values, index = PlotValue( x_values ) )
        self._pv.update()
