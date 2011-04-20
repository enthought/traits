#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a HTMLEditor demo plugin for the Traits UI demo program.
"""

# Imports:
from traits.api import HasTraits, HTML

from traitsui.api import Item, Group, View

# Define the demo class:
class HTMLEditorDemo ( HasTraits ):
    """ Defines the main HTMLEditor demo class. """

    # Define a HTML trait to view
    html_trait = HTML("""<html><body><p>A HTMLEditor displaying</p>
<p>two paragraphs of text.</p></body></html>""")

    # Demo view
    view = View(Group(Item('html_trait',
                           style = 'simple',
                           label = 'Simple'),
                      show_labels = False),
                title     = 'HTMLEditor',
                buttons   = ['OK'],
                width     = 800,
                height    = 600,
                resizable = True)

# Create the demo:
demo = HTMLEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
