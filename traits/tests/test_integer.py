# ------------------------------------------------------------------------------
#
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# ------------------------------------------------------------------------------
"""
Tests for the Int trait type.

"""

from __future__ import absolute_import

import decimal
import sys
import unittest

import six

from traits.api import HasTraits, Int, TraitError
from traits.testing.optional_dependencies import numpy, requires_numpy


class A(HasTraits):
    integral = Int


class IntegerLike(object):
    def __index__(self):
        return 42


class Truncatable(object):
    def __int__(self):
        return 42


class TestInt(unittest.TestCase):
    def test_default(self):
        a = A()
        self.assertEqual(a.integral, 0)
        self.assertIn(type(a.integral), six.integer_types)

    def test_accepts_int(self):
        a = A()
        a.integral = 23
        self.assertEqual(a.integral, 23)
        self.assertIn(type(a.integral), six.integer_types)

    def test_accepts_large_integer(self):
        size_limit = sys.maxsize
        a = A()
        a.integral = size_limit
        self.assertEqual(a.integral, size_limit)
        self.assertIn(type(a.integral), six.integer_types)

        a.integral = size_limit + 1
        self.assertEqual(a.integral, size_limit + 1)
        self.assertIn(type(a.integral), six.integer_types)

        a.integral = 2**2048 + 1
        self.assertEqual(a.integral, 2**2048 + 1)
        self.assertIn(type(a.integral), six.integer_types)

    def test_accepts_bool(self):
        a = A()
        a.integral = True
        self.assertEqual(a.integral, 1)
        self.assertIn(type(a.integral), six.integer_types)

    def test_respects_dunder_index(self):
        a = A()
        a.integral = IntegerLike()
        self.assertEqual(a.integral, 42)
        self.assertIn(type(a.integral), six.integer_types)

    def test_rejects_dunder_int(self):
        a = A()
        with self.assertRaises(TraitError):
            a.integral = Truncatable()

    def test_rejects_floating_point_types(self):
        a = A()
        with self.assertRaises(TraitError):
            a.integral = 23.0
        with self.assertRaises(TraitError):
            a.integral = decimal.Decimal(23)

    def test_rejects_string(self):
        a = A()
        with self.assertRaises(TraitError):
            a.integral = "23"

    @requires_numpy
    def test_numpy_types(self):
        a = A()
        a.integral = numpy.int32(23)
        self.assertEqual(a.integral, 23)
        self.assertIn(type(a.integral), six.integer_types)

        a.integral = numpy.uint64(2 ** 63 + 2)
        self.assertEqual(a.integral, 2 ** 63 + 2)
        self.assertIn(type(a.integral), six.integer_types)

        with self.assertRaises(TraitError):
            a.integral = numpy.float32(4.0)
        with self.assertRaises(TraitError):
            a.integral = numpy.float64(4.0)
