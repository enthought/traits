#------------------------------------------------------------------------------
# Copyright (c) 2005-2013, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#------------------------------------------------------------------------------
from traits.testing.unittest_tools import unittest, expected_failure


class TestExpectedFailure(unittest.TestCase):

    def test_expected_failure(self):
        with self.assertRaises(unittest.case._ExpectedFailure):
            with expected_failure():
                raise AssertionError

    def test_unexpected_success(self):
        with self.assertRaises(unittest.case._ExpectedFailure):
            with expected_failure():
                pass

    def test_other_errors(self):
        with self.assertRaises(RuntimeError):
            with expected_failure():
                raise RuntimeError

if __name__ == '__main__':
    unittest.main()
