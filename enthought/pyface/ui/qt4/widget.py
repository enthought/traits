#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
# 
# This software is provided without warranty under the terms of the GPL v2
# license.
# 
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------


# Enthought library imports.
from enthought.traits.api import Any, HasTraits, implements

# Local imports.
from enthought.pyface.i_widget import IWidget, MWidget


class Widget(MWidget, HasTraits):
    """ The toolkit specific implementation of a Widget.  See the IWidget
    interface for the API documentation.
    """

    implements(IWidget)

    #### 'IWidget' interface ##################################################

    control = Any

    parent = Any

    ###########################################################################
    # 'IWidget' interface.
    ###########################################################################

    def destroy(self):
        if self.control is not None:
            self.control.setParent(None)
            self.control = None

#### EOF ######################################################################
