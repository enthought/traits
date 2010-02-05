#-------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   06/25/09
#
#-------------------------------------------------------------------------------

""" A single line text widget that supports functionality common to native
    search widgets.
"""

from __future__ import absolute_import

from ...api import Bool, Property, Str
from ..toolkit import toolkit_object
from ..basic_editor_factory import BasicEditorFactory


class SearchEditor(BasicEditorFactory):
    """ A single line text widget that supports functionality common to native
        search widgets.
    """

    # The editor class to be created:
    klass = Property

    # The descriptive text for the widget
    text = Str("Search")

    # Is user input set on every keystroke?
    auto_set = Bool(True)

    # Is user input set when the Enter key is pressed?
    enter_set = Bool(False)

    # Whether to show a search button on the widget
    search_button = Bool(True)

    # Whether to show a cancel button on the widget
    cancel_button = Bool(False)

    # Fire this event on the object whenever a search should be triggered,
    # regardless of whether the search term changed
    search_event_trait = Str

    def _get_klass(self):
        """ Returns the toolkit-specific editor class to be instantiated.
        """
        return toolkit_object('search_editor:SearchEditor')
