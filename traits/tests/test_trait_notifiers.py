# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from traits.api import HasTraits, Int, observe

class TestTraitNotifiers(unittest.TestCase):
    def test_ui_dispatch(self):
        # Given
        class DispatchTest(HasTraits):
            test_param = Int()
        t = DispatchTest()
        def test_handler(event):
            print(event)

        # When
        t.observe(test_handler, 'test_param', dispatch='ui')

        # Then
        try:
            t.test_param = 1
        except Exception:
            self.fail("test_ui_dispatch raised an Exception unexpectedly!")
