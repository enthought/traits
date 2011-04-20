#--(Internet Explorer HTML Editor (Windows Only))-------------------------------
"""
Internet Explorer HTML Editor (Windows Only)
============================================

In Traits 3.0, a new **IEHTMLEditor** has been added to the Traits UI package.
The editor allows displaying (but not editing) HTML pages using the Microsoft
Internet Explorer browser.

This editor is currently only available for the Windows platform and is
located in the wxPython version of the Traits UI in the
*traitsui.wx.extras.windows* package. The purpose of the
*extras.windows* package is to provide a location for editors which may be
toolkit and Windows platform specific, and not necessarily available in all
Traits UI toolkit packages or platforms.

The traits supported by the **IEHTMLEditor** editor are as follows:

home
    A string specifying the optional extended name of a trait event used to tell
    Internet Explorer to display the user's home page. Set the specified trait
    to **True** to cause the browser to display the user's home page.

back
    A string specifying the optional extended name of a trait event used to tell
    Internet Explorer to display the previous browser page. Set the specified
    trait to **True** to cause the browser to display the previous browser page.

forward
    A string specifying the optional extended name of a trait event used to tell
    Internet Explorer to display the next (i.e. forward) browser page. Set the
    specified trait to **True** to cause the browser to display the next browser
    page (if available).

stop
    A string specifying the optional extended name of a trait event used to tell
    Internet Explorer to stop loading the current page. Set the specified trait
    to **True** to cause the browser to stop loading the current page.

refresh
    A string specifying the optional extended name of a trait event used to tell
    Internet Explorer to refresh the current page. Set the specified trait to
    **True** to cause the browser to refresh the current page.

search
    A string specifying the optional extended name of a trait event used to tell
    Internet Explorer to initiate a search of the current page. Set the
    specified trait to **True** to cause the browser to start a search of the
    current page.

status
    A string specifying the optional extended name of a trait used contain the
    current Internet Explorer status. This trait is automatically updated by the
    browser as its internal status changes.

title
    A string specifying the optional extended name of a trait used contain the
    current Internet Explorer page title. This trait is automatically updated by
    the browser as the current page title is changed.

page_loaded
    A string specifying the optional extended name of a trait used contain the
    URL of the current Internet Explorer page. This trait is automatically
    updated by the browser as a page is loaded.

html
    A string specifying the optional extended name of a trait used to get or
    set the HTML page content of the current Internet Explorer page. This
    trait is automatically updated by the browser as a page is loaded, and can
    also be set by an application to cause the browser to display the content
    provided.

The value edited by an **IEHTMLEditor** should be a string containing either the
URL or file name of the file that Internet Explorer should display. This is a
*read only* value that is not modified by the editor. Changing the value causes
the browser to display the page defined by the new value of the trait.
"""

#--[Imports]--------------------------------------------------------------------

from traitsui.wx.extra.windows.ie_html_editor \
    import IEHTMLEditor

from traits.api \
    import HasTraits, Str, List, Button

from traitsui.api \
    import View, VGroup, HGroup, Item, TextEditor, ListEditor, spring

#--[WebPage Class]--------------------------------------------------------------

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

#--[InternetExplorerDemo Class]-------------------------------------------------

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

#--(Demo Notes)-----------------------------------------------------------------

"""
Demo Notes
==========

- Try dragging one of the browser tabs completely out of the tutorial window
  and see what happens...

- Then, just for fun, try dragging it back...
"""

#--<Example*>-------------------------------------------------------------------

demo = InternetExplorerDemo(
           pages = [ WebPage( url = 'http://code.enthought.com/traits/' ),
                     WebPage( url = 'http://dmorrill.com' ) ] )

