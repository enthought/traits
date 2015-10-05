# -----------------------------------------------------------------------------
#
#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------
"""
Tests for the Float trait type.

"""
import sys

from traits.testing.unittest_tools import unittest

from ..api import BaseFloat, Float, HasTraits


class FloatModel(HasTraits):
    value = Float


class BaseFloatModel(HasTraits):
    value = BaseFloat


class CommonFloatTests(object):
    """ Common tests for Float and BaseFloat """
    def test_default(self):
        a = self.test_class()
        self.assertEqual(a.value, 0.0)

    def test_accepts_float(self):
        a = self.test_class()
        a.value = 5.6
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 5.6)

    def test_accepts_int(self):
        a = self.test_class()
        a.value = 2
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2.0)

    @unittest.skipUnless(sys.version_info < (3,), "Not applicable to Python 3")
    def test_accepts_small_long(self):
        a = self.test_class()
        a.value = long(2)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2.0)

    @unittest.skipUnless(sys.version_info < (3,), "Not applicable to Python 3")
    def test_accepts_large_long(self):
        a = self.test_class()
        # Value large enough to be a long on Python 2.
        a.value = 2**64
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2**64)


class TestFloat(unittest.TestCase, CommonFloatTests):
    def setUp(self):
        self.test_class = FloatModel


class TestBaseFloat(unittest.TestCase, CommonFloatTests):
    def setUp(self):
        self.test_class = BaseFloatModel
