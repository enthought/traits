# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import os
import unittest

from traits.examples._etsdemo_info import introduction
from traits.testing.optional_dependencies import requires_pkg_resources


class TestETSDemoInfo(unittest.TestCase):
    @requires_pkg_resources
    def test_introduction(self):
        # input to introduction is currently just a placeholder
        response = introduction({})
        self.assertTrue(os.path.exists(response['root']))
