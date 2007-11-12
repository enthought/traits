"""
Another demonstration of the ListCanvasEditor using the ImageBrowser tool.

The ImageBrowser tool uses a ListCanvasEditor to display a collection of
Traits image library images specified by their image name. Each item on
the canvas is an ImageItem object, which represents a single image.

For more information about how this program works, refer to the source code
of the ImageBrowser tool (enthought.developer.tools.image_browser.py).

Note: This demo requires the enthought.developer package to be installed.
"""

#-- Imports --------------------------------------------------------------------

try:
    from enthought.developer.tools.image_browser \
         import ImageBrowser
         
    from enthought.traits.ui.image \
         import ImageLibrary
         
    # Get the image library volume called 'images':
    volume = ImageLibrary.catalog[ 'images' ]
    
    # Create the demo using a subset of the images available in the 'image'
    # volume:
    demo = ImageBrowser(
               image_names = [ image.image_name for image in volume.images
                               if image.image_name.find( 'O' ) >= 0 ] )
except:
    raise Exception( 'This demo requires the enthought.developer package '
                     'to be installed.' )
        
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
