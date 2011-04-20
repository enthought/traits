"""This demo shows how to use Traits TreeEditors with PyTables to walk the
heirarchy of an HDF5 file.  This only picks out arrays and groups, but could
easily be extended to other structures, like tables.

In the demo, the path to the selected item is printed whenever the selection
changes.  In order to run, a path to an existing HDF5 database must be given
at the bottom of this file.
"""

from traits.api import HasTraits, Str, List, Instance
from traitsui.api import TreeEditor, TreeNode, View, Item, VSplit, HGroup, Handler, Group
from traitsui.menu import Menu, Action, Separator

import tables as tb


# View for objects that aren't edited
no_view = View()


# HDF5 Nodes in the tree
class Hdf5ArrayNode(HasTraits):
    name   = Str( '<unknown>' )
    path = Str( '<unknown>' )
    parent_path = Str( '<unknown>' )

class Hdf5GroupNode(HasTraits):
    name     = Str( '<unknown>' )
    path = Str( '<unknown>' )
    parent_path = Str( '<unknown>' )
    # Can't have recursive traits?  Really?
    #groups = List( Hdf5GroupNode )
    groups = List
    arrays = List( Hdf5ArrayNode )
    groups_and_arrays = List

class Hdf5FileNode(HasTraits):
    name   = Str( '<unknown>' )
    path   = Str( '/' )
    groups = List( Hdf5GroupNode )
    arrays = List( Hdf5ArrayNode )
    groups_and_arrays = List

# Recurssively build tree, there is probably a better way of doing this.
def _get_sub_arrays(group, h5file):
    """Return a list of all arrays immediately below a group in an HDF5 file."""
    l = []

    for array in h5file.iterNodes(group, classname='Array'):
        a = Hdf5ArrayNode(
            name = array._v_name,
            path = array._v_pathname,
            parent_path = array._v_parent._v_pathname,
            )
        l.append(a)

    return l

def _get_sub_groups(group, h5file):
    """Return a list of all groups and arrays immediately below a group in an HDF5 file."""
    l = []

    for subgroup in h5file.iterNodes(group, classname='Group'):
        g = Hdf5GroupNode(
                name = subgroup._v_name,
                path = subgroup._v_pathname,
                parent_path = subgroup._v_parent._v_pathname,
                )

        subarrays = _get_sub_arrays(subgroup, h5file)
        if subarrays != []:
            g.arrays = subarrays

        subgroups = _get_sub_groups(subgroup, h5file)
        if subgroups != []:
            g.groups = subgroups

        g.groups_and_arrays = []
        g.groups_and_arrays.extend(subgroups)
        g.groups_and_arrays.extend(subarrays)

        l.append(g)

    return l

def _hdf5_tree(filename):
    """Return a list of all groups and arrays below the root group of an HDF5 file."""

    h5file = tb.openFile(filename, 'r')

    file_tree = Hdf5FileNode(
            name = filename,
            groups = _get_sub_groups(h5file.root, h5file),
            arrays = _get_sub_arrays(h5file.root, h5file),
            )

    file_tree.groups_and_arrays = []
    file_tree.groups_and_arrays.extend(file_tree.groups)
    file_tree.groups_and_arrays.extend(file_tree.arrays)

    h5file.close()

    return file_tree

# Get a tree editor
def _hdf5_tree_editor(selected=''):
    """Return a TreeEditor specifically for HDF5 file trees."""
    return TreeEditor(
        nodes = [
            TreeNode(
                node_for  = [ Hdf5FileNode ],
                auto_open = True,
                children  = 'groups_and_arrays',
                label     = 'name',
                view      = no_view,
                ),
            TreeNode(
                node_for  = [ Hdf5GroupNode ],
                auto_open = False,
                children  = 'groups_and_arrays',
                label     = 'name',
                view      = no_view,
                ),
            TreeNode(
                node_for  = [ Hdf5ArrayNode ],
                auto_open = False,
                children  = '',
                label     = 'name',
                view      = no_view,
                ),
            ],
        editable = False,
        selected = selected,
        )


if __name__ == '__main__':
    from traits.api import Any

    class ATree(HasTraits):
        h5_tree = Instance(Hdf5FileNode)
        node = Any

        traits_view =View(
            Group(
                Item('h5_tree',
                    editor = _hdf5_tree_editor(selected='node'),
                    resizable =True
                    ),
                orientation = 'vertical',
                ),
            title = 'HDF5 Tree Example',
            buttons = [ 'Undo', 'OK', 'Cancel' ],
            resizable = True,
            width = .3,
            height = .3
            )

        def _node_changed(self):
            print self.node.path


    a_tree = ATree( h5_tree = _hdf5_tree('/path/to/file.h5')  )
    a_tree.configure_traits()
#    a_tree.edit_traits()
