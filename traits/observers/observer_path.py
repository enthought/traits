# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


class ObserverPath:
    """ Path to describe what traits are being observed on an
    instance of HasTraits.
    """

    def __init__(self, node, nexts=None):
        self.node = node
        self.nexts = nexts if nexts is not None else []

    def __eq__(self, other):
        if other is self:
            return True
        if type(self) is not type(other):
            return False
        if self.node != other.node:
            return False

        if all(n1 == n2 for n1, n2 in zip(self.nexts, other.nexts)):
            return True
