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

from traits.testing.nose_tools import deprecated, performance, skip


class TestNoseTools(unittest.TestCase):
    def test_deprecated_deprecated(self):
        with self.assertWarns(DeprecationWarning) as cm:

            @deprecated
            def some_func():
                pass

        self.assertIn("test_nose_tools", cm.filename)

    def test_performance_deprecated(self):
        with self.assertWarns(DeprecationWarning) as cm:

            @performance
            def some_func():
                pass

        self.assertIn("test_nose_tools", cm.filename)

    def test_skip_deprecated(self):
        with self.assertWarns(DeprecationWarning) as cm:

            @skip
            def some_func():
                pass

        self.assertIn("test_nose_tools", cm.filename)
