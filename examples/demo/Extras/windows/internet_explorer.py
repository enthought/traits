#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

""" Demo showing how to use the Windows specific Internet Explorer editor.
"""

# Imports:
from traitsui.wx.extra.windows.ie_html_editor \
    import IEHTMLEditor

from traits.api \
    import Str, List, Button, HasTraits

from traitsui.api \
    import View, VGroup, HGroup, Item, TextEditor, ListEditor

# The web page class:
class WebPage ( HasTraits ):

    # The URL to display:
    url = Str( 'http://code.enthought.com' )

    # The page title:
    title = Str

    # The page status:
    status = Str

    # The browser navigation buttons:
    back    = Button( '<--' )
    forward = Button( '-->' )
    home    = Button( 'Home' )
    stop    = Button( 'Stop' )
    refresh = Button( 'Refresh' )
    search  = Button( 'Search' )

    # The view to display:
    view = View(
        HGroup( 'back', 'forward', 'home', 'stop', 'refresh', 'search', '_',
                Item( 'status', style = 'readonly' ),
                show_labels = False
        ),
        Item( 'url',
              show_label = False,
              editor     = IEHTMLEditor(
                               home    = 'home',    back   = 'back',
                               forward = 'forward', stop   = 'stop',
                               refresh = 'refresh', search = 'search',
                               title   = 'title',   status = 'status' )
        )
    )

# The demo class:
class InternetExplorerDemo ( HasTraits ):

    # A URL to display:
    url = Str( 'http://' )

    # The list of web pages being browsed:
    pages = List( WebPage )

    # The view to display:
    view = View(
        VGroup(
            Item( 'url',
                  label  = 'Location',
                  editor = TextEditor( auto_set = False, enter_set = True )
            )
        ),
        Item( 'pages',
              show_label = False,
              style      = 'custom',
              editor     = ListEditor( use_notebook = True,
                                       deletable    = True,
                                       dock_style   = 'tab',
                                       export       = 'DockWindowShell',
                                       page_name    = '.title' )
        )
    )

    # Event handlers:
    def _url_changed ( self, url ):
        self.pages.append( WebPage( url = url.strip() ) )

# Create the demo:
demo = InternetExplorerDemo(
           pages = [ WebPage(url='http://code.enthought.com/projects/traits/'),
                     WebPage(url='http://dmorrill.com') ] )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
