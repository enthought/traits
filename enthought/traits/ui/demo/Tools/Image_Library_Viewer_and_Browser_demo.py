"""
A demonstration of how tools in the <b>enthought.developer</b> package can be
easily connected together to form other tools. In this case we are connecting
the <i>ImageLibraryViewer</i> to an <i>ImageBrowser</i> to form a new
<i>ImageTool</i>.

This demo is displayed as a popup window because it requires a fairly large
screen area in order to display all of the tool data. However, it can just as
easily be embedded within a Traits UI view if desired.

Note also that in this example, we are <i>programmatically</i> connecting
the two tools together (see the <i>_viewer_default</i> method). However,
because both of these tools support the <i>feature</i> architecture, they
can just as easily be connected together by the end user using the <i>feature
user interface</i>.

All of the tools in the <b>enthought.developer</b> package follow the <i>small,
sharp, visual tools</i> design model, which is intended to allow developers 
and end users to create new tools by the interconnection of the other tools, 
similar to the shell command line tool model, but oriented toward visual tools.

The top portion of the Image Library Viewer is a <i>live filter</i>, meaning
that you can type information into any of the various fields to filter the
set of image library image shown.

For fields such as <i>volume<i>, the information you type can appear anywhere in
the volume name to produce a match. The match is case insensitive.

For numeric fields, such as <i>height</i> and <i>width</i>, you can type a
number or a numeric relation (e.g. <=32). If you do not specify a relation,
<i>less than or equal</i> is assumed. The valud relations are: '=', '!=', '<',
'<=', '>' or '>='.

If an image in the view is 32x32 or smaller, it will appear in the first column
of the viewer. If it is larger than 32x32, then the value for that cell will
be blank. However, you can click on the cell to display a pop-up view of the
complete image.

Similarly, you can click on any <i>Copyright</i> or <i>License</i> column cell
to display a pop-up view of the complete copyright or license information.

You can also double-click on a <i>Volume</i> or <i>Name</i> column cell to
copy the fully-qualified image library name to the system clipboard, which you
can then paste into your Python source code to use the selected image in a
Traits UI-based application.

If you select one or more images in the image library viewer, you will see a 
full size version of the image appear in the browser view.

In order for this demo to run, you must have the enthought.developer package 
installed.
"""

try:
    from enthought.traits.api \
        import HasTraits, Instance
        
    from enthought.traits.ui.api \
        import View, VSplit, Item
        
    from enthought.developer.tools.image_library_viewer \
         import ImageLibraryViewer
         
    from enthought.developer.tools.image_browser \
         import ImageBrowser
         
    class ImageTool ( HasTraits ):
        
        # The image library viewer we are using:
        viewer = Instance( ImageLibraryViewer )
        
        # The image browser we are using:
        browser = Instance( ImageBrowser, () )
        
        #-- Traits UI View Definitions -----------------------------------------
        
        view = View(
            VSplit(
                Item( 'viewer',  style = 'custom', dock = 'horizontal' ),
                Item( 'browser', style = 'custom', dock = 'horizontal' ),
                id          = 'splitter',
                show_labels = False
            ),
            title     = 'Image Tool',
            id        = 'enthought.traits.ui.demo.tools.Image_Library_Viewer_'
                        'and_Browser_demo',
            width     = 0.75,
            height    = 0.75,
            resizable = True
        )
        
        #-- Default Value Handlers ---------------------------------------------
        
        def _viewer_default ( self ):
            viewer = ImageLibraryViewer()
            viewer.sync_trait( 'image_names', self.browser )
            
            return viewer
    
    # Create an instance of the ImageTool as the demo to run:
    popup = ImageTool()
except:
    raise Exception( 'This demo requires the enthought.developer package '
                     'to be installed.' )
        
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

