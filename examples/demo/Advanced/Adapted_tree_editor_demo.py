#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Demonstrates an alternative method of defining a <b>TreeEditor</b> by creating
<b>ITreeNodeAdapter</b> subclasses.

To run this demonstration successfully, you must have the <b>AppTools</b> egg
installed.

Using <b>ITreeNodeAdapters</b> can be useful in cases where the kind of content
of the tree is not always known ahead of time. For example, you might be
creating a reusable tool or component which can display its data in a tree
view, but you do not know what kind of data it will be asked to display when
you write the code. Therefore, it may be impossible for you to specify a
<b>TreeEditor</b> with a correct set of <b>TreeNode</b> objects that will work
in all possible future cases.

Using <b>ITreeNodeAdapter</b> subclasses, you can allow the clients of your code
to solve this problem by providing one of more <b>ITreeNodeAdapters</b> that
can be used to provide the correct tree node information for each type of data
that will appear in the <b>TreeEditor</b> view.

In this demo, we define an <b>ITreeNodeAdapter</b> subclass that adapts the
<i>apptools.io.file.File</i> class to be displayed in a file explorer style
tree view.
"""

#-- Imports --------------------------------------------------------------------

from os \
    import getcwd

from traits.api \
    import HasTraits, Property, Directory, adapts, property_depends_on

from traitsui.api \
    import View, VGroup, Item, TreeEditor, ITreeNode, ITreeNodeAdapter

from apptools.io.api \
    import File

#-- FileAdapter Class ----------------------------------------------------------

class FileAdapter ( ITreeNodeAdapter ):

    adapts( File, ITreeNode )

    #-- ITreeNodeAdapter Method Overrides --------------------------------------

    def allows_children ( self ):
        """ Returns whether this object can have children.
        """
        return self.adaptee.is_folder

    def has_children ( self ):
        """ Returns whether the object has children.
        """
        children = self.adaptee.children
        return ((children is not None) and (len( children ) > 0))

    def get_children ( self ):
        """ Gets the object's children.
        """
        return self.adaptee.children

    def get_label ( self ):
        """ Gets the label to display for a specified object.
        """
        return self.adaptee.name + self.adaptee.ext

    def get_tooltip ( self ):
        """ Gets the tooltip to display for a specified object.
        """
        return self.adaptee.absolute_path

    def get_icon ( self, is_expanded ):
        """ Returns the icon for a specified object.
        """
        if self.adaptee.is_file:
            return '<item>'

        if is_expanded:
            return '<open>'

        return '<open>'

    def can_auto_close ( self ):
        """ Returns whether the object's children should be automatically
            closed.
        """
        return True

#-- FileTreeDemo Class ---------------------------------------------------------

class FileTreeDemo ( HasTraits ):

    # The path to the file tree root:
    root_path = Directory( entries = 10 )

    # The root of the file tree:
    root = Property

    # The traits view to display:
    view = View(
        VGroup(
            Item( 'root_path' ),
            Item( 'root',
                  editor = TreeEditor( editable = False, auto_open = 1 )
            ),
            show_labels = False
        ),
        width     = 0.33,
        height    = 0.50,
        resizable = True
    )

    #-- Traits Default Value Methods -------------------------------------------

    def _root_path_default ( self ):
        return getcwd()

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'root_path' )
    def _get_root ( self ):
        return File( path = self.root_path )

#-- Create and run the demo ----------------------------------------------------

demo = FileTreeDemo()

# Run the demo (if invoked form the command line):
if __name__ == '__main__':
    demo.configure_traits()

