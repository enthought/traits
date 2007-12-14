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
#  Date:   10/14/2004
#
#------------------------------------------------------------------------------

""" Defines common traits used within the traits.ui package.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import join
    
from enthought.traits.api \
    import HasStrictTraits, Trait, TraitPrefixList, Delegate, Str, Instance, \
           Float, List, Enum, Any, Range, Expression, TraitType, TraitError
           
from enthought.traits.trait_base \
    import get_resource_path

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Styles for user interface elements:
style_trait = Trait( 'simple',
                     TraitPrefixList( 'simple', 'custom', 'text', 'readonly' ),
                     cols = 4 )
                     
# Trait for the default object being edited:                     
object_trait = Expression( 'object' )                     

# The default dock style to use:
dock_style_trait = Enum( 'fixed', 'horizontal', 'vertical', 'tab',
                         desc = "the default docking style to use" )
                         
# The default notebook tab image to use:                      
image_trait = Instance( 'enthought.pyface.image_resource.ImageResource',
                        desc = 'the image to be displayed on notebook tabs' )
                     
# The category of elements dragged out of the view:
export_trait = Str( desc = 'the category of elements dragged out of the view' )

# Delegate a trait value to the object's **container** trait:                  
container_delegate = Delegate( 'container' )

# An identifier for the external help context:
help_id_trait = Str( desc = "the external help context identifier" )                     

# A button to add to a view:
a_button = Trait( '', Str, Instance( 'enthought.traits.ui.menu.Action' ) )

# The set of buttons to add to the view:
buttons_trait = List( a_button,
                      desc = 'the action buttons to add to the bottom of '
                             'the view' )

# View trait specified by name or instance:
AView = Any
#AView = Trait( '', Str, Instance( 'enthought.traits.ui.View' ) )

#-------------------------------------------------------------------------------
#  'StatusItem' class:
#-------------------------------------------------------------------------------

class StatusItem ( HasStrictTraits ):
    
    # The name of the trait the status information will be synched with:
    name = Str( 'status' )
    
    # The width of the status field. The possible values are:
    # - abs( width )  > 1.0: Width of the field in pixels = abs( width )
    # - abs( width ) <= 1.0: Relative width of the field when compared to other
    #   relative width fields.
    width = Float( 0.5 )
    
#-------------------------------------------------------------------------------
#  'ViewStatus' trait:
#-------------------------------------------------------------------------------

class ViewStatus ( TraitType ):
    """ Defines a trait whose value must be a single StatusItem instance or a
        list of StatusItem instances.
    """
    
    # Define the default value for the trait:
    default_value = None
    
    # A description of the type of value this trait accepts:
    info_text = ('None, a string, a single StatusItem instance, or a list or ' 
                 'tuple of strings and/or StatusItem instances')
    
    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        """
        if isinstance( value, basestring ):
            return [ StatusItem( name = value ) ]
            
        if isinstance( value, StatusItem ):
            return [ value ]
            
        if value is None:
            return value
            
        result = []
        if isinstance( value, SequenceTypes ):
            for item in value:
                if isinstance( item, basestring ):
                    result.append( StatusItem( name = item ) )
                elif isinstance( item, StatusItem ):
                    result.append( item )
                else:
                    break
            else:
                return result
            
        self.error( object, name, value )
    
#-------------------------------------------------------------------------------
#  'Image' trait:
#-------------------------------------------------------------------------------

image_resource_cache = {}
image_bitmap_cache   = {}

def convert_image ( value, level = 3 ):
    """ Converts a specified value to an ImageResource if possible.
    """
    global image_resource_cache
    
    from enthought.pyface.image_resource import ImageResource
    
    if not isinstance( value, basestring ):
        return value
        
    key             = value
    is_traits_image = (value[:1] == '@')
    if not is_traits_image:
        search_path = get_resource_path( level )
        key         = '%s[%s]' % ( value, search_path )
        
    result = image_resource_cache.get( key )
    if result is None:
        if is_traits_image:
            from image import ImageLibrary
            
            result = ImageLibrary.image_resource( value )
        else:
            result = ImageResource( value, search_path = [ search_path ] )
            
        image_resource_cache[ key ] = result
            
    return result
    
def convert_bitmap ( image_resource ):
    """ Converts an ImageResource to a bitmap using a cache.
    """
    global image_bitmap_cache
    
    bitmap = image_bitmap_cache.get( image_resource )
    if (bitmap is None) and (image_resource is not None):
        try:
            image_bitmap_cache[ image_resource ] = bitmap = \
                image_resource.create_bitmap()
        except:
            pass
            
    return bitmap
    
class Image ( TraitType ):
    """ Defines a trait whose value must be a PyFace ImageResource or a string
        that can be converted to one.
    """
    
    # Define the default value for the trait:
    default_value = None
    
    # A description of the type of value this trait accepts:
    info_text = 'an ImageResource or string that can be used to define one'
    
    def __init__ ( self, value = None, **metadata ):
        """ Creates an Image trait.

        Parameters
        ----------
        value : string or ImageResource
            The default value for the Image, either an ImageResource object,
            or a string from which an ImageResource object can be derived.
        """
        super( Image, self ).__init__( convert_image( value ), **metadata )

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        """
        from enthought.pyface.image_resource import ImageResource
        
        value = convert_image( value, 4 )
        if (value is None) or isinstance( value, ImageResource ):
            return value
            
        self.error( object, name, value )
        
#-------------------------------------------------------------------------------
#  'ATheme' trait:
#-------------------------------------------------------------------------------

def convert_theme ( value, level = 3 ):
    """ Converts a specified value to a Theme if possible.
    """
    if not isinstance( value, basestring ):
        return value
        
    if (value[:1] == '@') and (value.find( ':' ) >= 2):
        from image import ImageLibrary
        
        info = ImageLibrary.image_info( value )
        if info is not None:
            return info.theme
        
    from theme import Theme
    return Theme( image = convert_image( value, level + 1 ) )
    
class ATheme ( TraitType ):
    """ Defines a trait whose value must be a traits UI Theme or a string that
        can be converted to one.
    """
    
    # Define the default value for the trait:
    default_value = None
    
    # A description of the type of value this trait accepts:
    info_text = 'a Theme or string that can be used to define one'
    
    def __init__ ( self, value = None, **metadata ):
        """ Creates an ATheme trait.

        Parameters
        ----------
        value : string or Theme
            The default value for the ATheme, either a Theme object, or a 
            string from which a Theme object can be derived.
        """
        super( ATheme, self ).__init__( convert_theme( value ), **metadata )

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        """
        from theme import Theme
        
        value = convert_theme( value, 4 )
        if (value is None) or isinstance( value, Theme ):
            return value
            
        self.error( object, name, value )

#-------------------------------------------------------------------------------
#  'BasePMB' class:  
#-------------------------------------------------------------------------------
                
class BaseMB ( HasStrictTraits ):
    
    def __init__ ( self, *args, **traits ):
        """ Initializes the object.
        """
        n = len( args )
        if n > 0:
            if n == 1:
                left = right = top = bottom = args[0]
            elif n == 2:
                left = right  = args[0]
                top  = bottom = args[1]
            elif n == 4:
                left, right, top, bottom = args
            else:
                raise TraitError( '0, 1, 2 or 4 arguments expected, but %d '
                                  'specified' % n )
            self.set( left = left, right = right, top = top, bottom = bottom )
             
        super( BaseMB, self ).__init__( **traits )

#-------------------------------------------------------------------------------
#  'Margin' class:  
#-------------------------------------------------------------------------------
                
class Margin ( BaseMB ):
    
    # The amount of padding/margin at the top:
    top = Range( -32, 32, 0 )
    
    # The amount of padding/margin at the bottom:
    bottom = Range( -32, 32, 0 )
    
    # The amount of padding/margin on the left:
    left = Range( -32, 32, 0 )
    
    # The amount of padding/margin on the right:
    right = Range( -32, 32, 0 )

#-------------------------------------------------------------------------------
#  'Border' class:  
#-------------------------------------------------------------------------------
                
class Border ( BaseMB ):
    
    # The amount of border at the top:
    top = Range( 0, 32, 0 )
    
    # The amount of border at the bottom:
    bottom = Range( 0, 32, 0 )
    
    # The amount of border on the left:
    left = Range( 0, 32, 0 )
    
    # The amount of border on the right:
    right = Range( 0, 32, 0 )

#-------------------------------------------------------------------------------
#  'HasMargin' trait:
#-------------------------------------------------------------------------------

class HasMargin ( TraitType ):
    """ Defines a trait whose value must be a Margin object or an integer or
        tuple value that can be converted to one.
    """
    
    # The desired value class:
    klass = Margin
    
    # Define the default value for the trait:
    default_value = Margin( 0 )
    
    # A description of the type of value this trait accepts:
    info_text = ('a Margin instance, or an integer in the range from -32 to 32 '
                 'or a tuple with 1, 2 or 4 integers in that range that can be '
                 'used to define one')

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        """
        if isinstance( value, int ):
            try:
                value = self.klass( value )
            except:
                self.error( object, name, value )
        elif isinstance( value, tuple ):
            try:
                value = self.klass( *value )
            except:
                self.error( object, name, value )
            
        if isinstance( value, self.klass ):
            return value
            
        self.error( object, name, value )
        
    def get_default_value ( self ):
        """ Returns a tuple of the form: ( default_value_type, default_value )
            which describes the default value for this trait.
        """
        dv  = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            if isinstance( dv, int ):
                dv = self.klass( dv )
            elif isinstance( dv, tuple ):
                dv = self.klass( *dv )
                
            if not isinstance( dv, self.klass ):
                return super( HasMargin, self ).get_default_value()
                
            self.default_value_type = dvt = 7
            dv = ( self.klass, (), dv.get() )
        
        return ( dvt, dv )

#-------------------------------------------------------------------------------
#  'HasBorder' trait:
#-------------------------------------------------------------------------------

class HasBorder ( HasMargin ):
    """ Defines a trait whose value must be a Border object or an integer
        or tuple value that can be converted to one.
    """
    
    # The desired value class:
    klass = Border
    
    # Define the default value for the trait:
    default_value = Border( 0 )
    
    # A description of the type of value this trait accepts:
    info_text = ('a Border instance, or an integer in the range from 0 to 32 '
                 'or a tuple with 1, 2 or 4 integers in that range that can be '
                 'used to define one')

#-------------------------------------------------------------------------------
#  Other trait definitions:
#-------------------------------------------------------------------------------

# The position of an image relative to its associated text:
Position = Enum( 'left', 'right', 'above', 'below' )
    
# The alignment of text within a control:
Alignment = Enum( 'default', 'left', 'center', 'right' )

# The spacing between two items:
Spacing = Range( -32, 32, 3 )

#-------------------------------------------------------------------------------
#  Other definitions:
#-------------------------------------------------------------------------------

# Types that represent sequences:
SequenceTypes = ( tuple, list )

