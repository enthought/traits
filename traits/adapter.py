#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Martin Chilvers
#  Date:   07/18/2007
#
#-------------------------------------------------------------------------------

""" An extension to PyProtocols to simplify the declaration of adapters.
"""


from __future__ import absolute_import


import traits.adaptation.adapter
from .util.deprecated import deprecated


class Adapter(traits.adaptation.adapter.Adapter):

    @deprecated("use 'Adapter' in 'traits.api' instead")
    def __init__(self, adaptee, **traits):
        super(Adapter, self).__init__(adaptee, **traits)


adapts = deprecated("use 'adapts' in 'traits.api' instead")(
    traits.adaptation.adapter.adapts
)

#### EOF ######################################################################
