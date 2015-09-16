#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
"""
Tests for the String trait type.

"""
try:
    import numpy
except ImportError:
    numpy_available = False
else:
    numpy_available = True

from traits.testing.unittest_tools import unittest

from ..api import HasTraits, String


class A(HasTraits):
    string = String


class TestString(unittest.TestCase):
    @unittest.skipUnless(numpy_available, "numpy not available")
    def test_accepts_numpy_string(self):
        numpy_string = numpy.str_("this is a numpy string!")
        a = A()
        a.string = numpy_string
        self.assertEqual(a.string, numpy_string)
        self.assertIs(type(a.string), str)
