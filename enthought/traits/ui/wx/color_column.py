""" Table column object for Color traits. """

#-------------------------------------------------------------------------------
#  Imports:  
#-------------------------------------------------------------------------------

from wx \
    import Colour as WxColour

from enthought.traits.ui.table_column \
    import ObjectColumn
    
#-------------------------------------------------------------------------------
#  'ColorColumn' class:  
#-------------------------------------------------------------------------------
        
class ColorColumn ( ObjectColumn ):
    """ Table column object for Color traits. """
    
#-- ObjectColumn Overrides -----------------------------------------------------
    
    def get_cell_color ( self, object ):
        """ Returns the cell background color for the column for a specified 
            object.
        """
        color_values = getattr( object, self.name + '_' )
        if type( color_values ) is tuple:
            wxcolor = WxColour( *self._as_int_rgb_tuple( color_values ) )
        else:
            wxcolor = super( ColorObjectColumn, self ).get_cell_color( object )
        return wxcolor

    def get_value ( self, object ):
        """ Gets the value of the column for a specified object.
        """
        value = getattr( self.get_object( object ), self.name )
        if type( value ) is tuple:
            value = "(%3d, %3d, %3d)" % self._as_int_rgb_tuple( value[:-1] )
        elif type( value ) is not str:
            value = str( value )
        
        return value

#-- Private Methods ------------------------------------------------------------
    
    def _as_int_rgb_tuple ( self, color_values ):
        """ Returns object color as RGB integers. """
        return ( int( 255 * color_values[0] ), 
                 int( 255 * color_values[1] ),
                 int( 255 * color_values[2] ) )
                                
