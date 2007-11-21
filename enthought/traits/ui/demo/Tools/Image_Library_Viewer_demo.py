"""
A demonstration of the <i>Image Library Viewer</i> tool, which is part of the 
<b>enthought.developer</b> package.

This demo is displayed as a popup window because it requires a fairly wide
screen area in order to display all of the viewer columns. However, it can be
embedded within any Traits UI view if desired.

The top portion of the Image Library Viewer is a <i>live filter</i>, meaning
the you can type information into any of the various fields to filter the
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

In order for this demo to run, you must have the enthought.developer package 
installed.
"""

try:
    from enthought.developer.tools.image_library_viewer \
         import ImageLibraryViewer
    
    # Create an instance of the Image Library Viewer as the demo to run:
    popup = ImageLibraryViewer()
except:
    raise Exception( 'This demo requires the enthought.developer package '
                     'to be installed.' )
        
# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

