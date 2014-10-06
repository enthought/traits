#
# Enthought product code
#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import unittest
from traits.api import HasStrictTraits, Int, TraitError

from geophysics.util.validated_tuple import ValidatedTuple


class Simple(HasStrictTraits):

    scalar_range = ValidatedTuple(
        Int(0), Int(1), validation=lambda x: x[0] < x[1])


class TestValidatedTuple(unittest.TestCase):

    def test_initialization(self):
        simple = Simple()
        self.assertEqual(simple.scalar_range, (0, 1))

    def test_invalid_definition(self):
        with self.assertRaises(TraitError):
            class InValidSimple(HasStrictTraits):
                scalar_range = ValidatedTuple(
                    Int(1), Int(0), validation=lambda x: x[0] < x[1])

    def test_normal_validation(self):
        simple = Simple()

        simple.scalar_range = (2, 5)
        self.assertEqual(simple.scalar_range, (2, 5))

        with self.assertRaises(TraitError):
            simple.scalar_range = (2.0, 5)

    def test_custom_validation(self):
        simple = Simple()

        with self.assertRaises(TraitError):
            simple.scalar_range = (5, 2)
