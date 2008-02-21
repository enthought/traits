#-------------------------------------------------------------------------------
#  
#  Defines the theme style information for a DockWindow and its components.
#
#  Written by: David C. Morrill  
#  
#  Date: 07/14/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines the theme style information for a DockWindow and its components.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits, Bool
    
from ui_traits \
    import Image, ATheme
    
from theme \
    import Theme

#-------------------------------------------------------------------------------
#  'DockWindowTheme' class:
#-------------------------------------------------------------------------------
                                                                    
class DockWindowTheme ( HasPrivateTraits ):
    """ Defines the theme style information for a DockWindow and its components.
    """
    
    #-- Public Trait Definitions -----------------------------------------------
    
    # Use the theme background color as the DockWindow background color?
    use_theme_color = Bool( True )
    
    # Draw notebook tabs at the top (True) or the bottom (False)?
    tabs_at_top = Bool( True )
    
    # Active tab theme:
    tab_active = ATheme( Theme( 'tab_active', label = ( 0, -2 ) ) )
    
    # Inactive tab theme:
    tab_inactive = ATheme( Theme( 'tab_inactive', label = ( 0, -2 ) ) ) 
                          
    # Optional image to use for right edge of rightmost inactive tab:                                
    tab_inactive_edge = Image                                
    
    # Tab hover theme (used for inactive tabs):
    tab_hover = ATheme( Theme( 'tab_hover', label = ( 0, -2 ) ) )
                          
    # Optional image to use for right edge of rightmost hover tab:                                
    tab_hover_edge = Image                                
    
    # Tab background theme:
    tab_background = ATheme( Theme( 'tab_background' ) )
    
    # Tab theme:
    tab = ATheme( Theme( 'tab', content = ( -3, 1, 1, 1 ), 
                                label   = ( -5, 0 ) ) )
    
    # Vertical splitter bar theme:
    vertical_splitter = ATheme( Theme( 'vertical_splitter', 
                                     alignment = 'center', label = ( -1, 0 ) ) )
    
    # Horizontal splitter bar theme:
    horizontal_splitter = ATheme( Theme( 'horizontal_splitter', 
                                         alignment = 'center' ) )
    
    # Vertical drag bar theme:
    vertical_drag = ATheme( Theme( 'vertical_drag', content = ( 0, 10 ) ) )
    
    # Horizontal drag bar theme:
    horizontal_drag = ATheme( Theme( 'horizontal_drag', content = ( 10, 0 ) ) )

#-------------------------------------------------------------------------------
#  Define the default theme:
#-------------------------------------------------------------------------------
       
# Original DockWindows UI redone as a theme:
default_dock_window_theme = DockWindowTheme(
    use_theme_color     = False,
    tab_active          = Theme( 'std_tab_active',   label   = ( 0, -3 ), 
                                                     content = ( 7, 6, 0, 0 ) ),
    tab_inactive        = Theme( 'std_tab_inactive', label   = ( 0, -1 ),
                                                     content = ( 5, 0 ) ),
    tab_hover           = Theme( 'std_tab_hover',    label   = ( 0, -2 ),
                                                     content = ( 5, 0 ) ),
    tab_background      = Theme( 'std_tab_background' ),
    tab                 = Theme( 'std_tab', content = 0, 
                                            label   = ( -4, 0 ) ),
    vertical_splitter   = Theme( 'std_vertical_splitter', content = 0, 
                                                          label  = ( 0, -25 ) ), 
    horizontal_splitter = Theme( 'std_horizontal_splitter', content = 0, 
                                                          label  = ( -24, 0 ) ), 
    vertical_drag       = Theme( 'std_vertical_drag',   content = ( 0, 10 ) ),
    horizontal_drag     = Theme( 'std_horizontal_drag', content = ( 10, 0 ) )
)

# Set the default DockWindow theme:
def dock_window_theme ( theme = None ):
    global default_dock_window_theme
    
    old_theme = default_dock_window_theme
    if theme is not None:
        default_dock_window_theme = theme
        
    return old_theme
    
