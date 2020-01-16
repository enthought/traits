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
