# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the String trait type.

"""
import unittest

from traits.api import HasTraits, String
from traits.testing.optional_dependencies import numpy, requires_numpy


class A(HasTraits):
    string = String


class TestString(unittest.TestCase):
    @requires_numpy
    def test_accepts_numpy_string(self):
        numpy_string = numpy.str_("this is a numpy string!")
        a = A()
        a.string = numpy_string
        self.assertEqual(a.string, numpy_string)
        self.assertIs(type(a.string), str)
