# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Float, HasTraits, Interface, provides, Str, Tuple


class IHasName(Interface):
    name = Str()


@provides(IHasName)
class NamedColor(HasTraits):
    name = Str()

    rgb = Tuple(Float, Float, Float)


named_color = NamedColor(name="green", rgb=(0.0, 1.0, 0.0))
