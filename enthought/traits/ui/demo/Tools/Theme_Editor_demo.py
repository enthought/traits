"""
Yet another demonstration of how tools in the <b>enthought.developer</b>
package can be easily connected together to form other tools. In this case we
are connecting the <i>ImageLibraryViewer</i> to an <i>ImageThemeEditor</i> to 
form a new <i>ThemeEditor</i> for editing Traits UI ImageLibrary themes.

As with most of the other tools, this demo is displayed as a popup window 
because it requires a fairly large screen area in order to display all of the 
tool data. However, it can just as easily be embedded within a Traits UI view 
if desired.

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

Now, the <b>ImageThemeEditor</b> is an editor for Traits UI <i>themes</i>,
which are images used to provide a more graphical framework for constructing 
Traits Views. Any Traits UI <b>Group</b> or <b>Item</b> can have a theme
applied to it. In fact, the <b>ImageThemeEditor</b> itself is an example of
a <i>themed</i> Traits UI View. You might wish to study its code to see how
themes can be applied when creating a view.

Themes tend to be larger than icons, so you might want to set the <i>height</i>
filter in the <b>ImageLibraryViewer</b> to something like <i>>100</i> to filter
out most of the icons in the library. Most of what remains in the view should
be images that can be used as themes.

Since the viewer only shows images <= 32 pixels high, you can click on the 
left-most column of the viewer to get a drop-down view of a particular image.

Selecting an image will also display it for editing in the 
<b>ImageThemeBrowser</b> view (initially) at the bottom of the window. If you
select more than one image in the viewer, then the editor will create a 
separate tab for each image being edited.

The main portion of the editor (initially on the right side) is divided into an
upper and lower half. The upper half contains all of the editing controls, and 
the bottom half shows the effect of editing changes on several Traits UI Views
themed with the image being edited.

The theme for an image has four sets of parameters that can be edited:
    
 * <b>Content</b>: Defines the boundaries of the portion of the image that will
   contain the main theme content (such as the scrolling list seen in the 
   bottom part of the editor).
 * <b>Label</b>: Defines the boundaries of the portion of the image that will
   contain the label or title information (such as the <i>A Shopping List</> 
   title seen in the bottom half of the editor).
 * <b>Border</b>: Defines the boundaries of the portion of the image that will
   be used as the <i>sizing handles</i>. Note that only the outermost part of
   the boundary is defined. The innermost part of the boundary is implicitly
   set by the editor.
 * <b>Alignment</b>: Defines how the label or title information should be
   aligned within the <b>Label</b> boundaries. The possible values are:
     * <b>Default</b>: Use the default alignment defined by the Traits UI
       component using the theme.
     * <b>Left</b>: Left align the label within the label area.
     * <b>Center</b>: Center the label within the label area.
     * <b>Right</b>: Right align the label within the label area.
     
The boundaries defined by the <b>Content</b>, <b>Label</b> and <b>Border</b>
parameters consists of four elements: <b>Left</b>, <b>Right</b>, <b>Top</b>
and <b>Bottom</b>. Each element is a relative distance from some image
<i>landmark</i>. For example, the <b>Border</b> elements are displacements from
the outermost edges of the image.

Positive values are always <i>inward</i> displacements, while negative values
are always <i>outward</i> displacements.

You edit the various elements by using the slider widgets next to each element
name. You can either use the mouse to drag the slider, or click in the slider
to enter a value using the keyboard. If using the keyboard, you can also use
the <i>Tab</i> key to quickly move from one slider to the next and remain in
text entry mode.

As you adjust the element values you will see the effect of the theme 
definition on the live <i>widgets</i> in the bottom half of the editor. In 
addition, one of the <i>widgets</i> displays a red overlay of the various
theme areas, so you can see the actual areas being defined. This is especially 
useful when adjusting the <b>Border</b> parameter, since it has no visual
effect on any of the widgets (except when you mouse over the widget's <i>sizing
border</i>.

If desired, you can also interact with the live widgets by dragging the
sizing border defined by the <b>Border</b> parameter to resize the widget, or
dragging the <b>Label</b> area to move the widget.

On the left side of the theme editor is the <i>Library Manager</i>, which shows
which images are being edited, organized by <i>image volume</i>. Each image
volume that has images currently being edited has a section of the library
manager devoted to it. Clicking on the displayed volume title will open that
section, displaying each of the images currently being edited. If you have
made changes to the image's theme, the image name will have a red icon 
displayed next to it indicating that you have made unsaved changes. To save
your changes, simply click on the <b>Save</b> button located at the bottom of
the section. Note that depending upon the size of the image volume, saving
the volume can sometimes be very time consuming. You can tell when the library
has been successfully saved by the <b>Save</b> button become disabled again, 
and the red icons next to each modified theme being removed.

If you close an umodified theme (or unselect it in the image viewer), the
image will be removed from the theme editor and the library manager. If the
removed image was also the last image in a image volume, the image volume
section will also be removed from the library manager.

However, if you close (or unselect) a modified image theme, the library manager
will continue to display the modified image as a reminder that you have 
unsaved changes.

This should give you enough information to start experimenting with the theme
editor tool.

Also, please note that in order for this demo to run, you must have the 
enthought.developer package installed.
"""

try:
    from enthought.traits.api \
        import HasTraits, Instance
        
    from enthought.traits.ui.api \
        import View, VSplit, Item
        
    from enthought.developer.tools.image_library_viewer \
         import ImageLibraryViewer
         
    from enthought.developer.tools.image_theme_editor \
         import ImageThemeEditor
         
    class ThemeEditor ( HasTraits ):
        
        # The image library viewer we are using:
        viewer = Instance( ImageLibraryViewer )
        
        # The image theme editor we are using:
        editor = Instance( ImageThemeEditor, () )
        
        #-- Traits UI View Definitions -----------------------------------------
        
        view = View(
            VSplit(
                Item( 'viewer', style = 'custom', dock = 'horizontal' ),
                Item( 'editor', style = 'custom', dock = 'horizontal' ),
                id          = 'splitter',
                show_labels = False
            ),
            title     = 'Theme Editor',
            id        = 'enthought.traits.ui.demo.tools.Theme_Editor_demo',
            width     = 0.75,
            height    = 0.75,
            resizable = True
        )
        
        #-- Default Value Handlers ---------------------------------------------
        
        def _viewer_default ( self ):
            viewer = ImageLibraryViewer()
            viewer.sync_trait( 'image_names', self.editor )
            
            return viewer
    
    # Create an instance of the ThemeEditor as the demo to run:
    popup = ThemeEditor()
except:
    raise Exception( 'This demo requires the enthought.developer package '
                     'to be installed.' )
        
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

