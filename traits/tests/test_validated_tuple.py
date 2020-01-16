import unittest

from traits.api import HasStrictTraits, Int, TraitError
from traits.tests.tuple_test_mixin import TupleTestMixin
from traits.trait_types import ValidatedTuple


class Simple(HasStrictTraits):

    scalar_range = ValidatedTuple(
        Int(0), Int(1), fvalidate=lambda x: x[0] < x[1]
    )


class ValidatedTupleTestCase(TupleTestMixin, unittest.TestCase):
    def setUp(self):
        self.trait = ValidatedTuple

    def test_initialization(self):
        simple = Simple()
        self.assertEqual(simple.scalar_range, (0, 1))

    def test_custom_validation(self):
        simple = Simple()

        simple.scalar_range = (2, 5)
        self.assertEqual(simple.scalar_range, (2, 5))

        with self.assertRaises(TraitError):
            simple.scalar_range = (5, 2)

    def test_error_during_custom_validation(self):
        def fvalidate(x):
            if x == (5, 2):
                raise RuntimeError()
            return True

        class Simple(HasStrictTraits):

            scalar_range = ValidatedTuple(Int(0), Int(1), fvalidate=fvalidate)

        simple = Simple()

        with self.assertRaises(RuntimeError):
            simple.scalar_range = (5, 2)
