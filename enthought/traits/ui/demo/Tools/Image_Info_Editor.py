try:
    from enthought.traits.api \
        import HasTraits, Instance
        
    from enthought.traits.ui.api \
        import View, VSplit, Item
        
    from enthought.developer.tools.image_library_viewer \
         import ImageLibraryViewer
         
    from enthought.developer.tools.image_info_editor \
         import ImageInfoEditor
         
    class ImageInfoEditor ( HasTraits ):
        
        # The image library viewer we are using:
        viewer = Instance( ImageLibraryViewer )
        
        # The image info editor we are using:
        editor = Instance( ImageInfoEditor, () )
        
        #-- Traits UI View Definitions -----------------------------------------
        
        view = View(
            VSplit(
                Item( 'viewer', style = 'custom', dock = 'horizontal' ),
                Item( 'editor', style = 'custom', dock = 'horizontal' ),
                id          = 'splitter',
                show_labels = False
            ),
            title     = 'Image Info Editor',
            id        = 'enthought.traits.ui.demo.tools.Image_Info_Editor',
            width     = 0.75,
            height    = 0.75,
            resizable = True
        )
        
        #-- Default Value Handlers ---------------------------------------------
        
        def _viewer_default ( self ):
            viewer = ImageLibraryViewer()
            viewer.sync_trait( 'image_names', self.editor )
            
            return viewer
    
    # Create an instance of the ImageInfoEditor as the demo to run:
    popup = ImageInfoEditor()
except:
    raise Exception( 'This demo requires the enthought.developer package '
                     'to be installed.' )
        
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

