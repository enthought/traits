import unittest
from traits.tests.tuple_test_mixin import TupleTestMixin as TupleTestMixin
from traits.trait_types import Tuple as Tuple
from typing import Any

class TupleTestCase(TupleTestMixin, unittest.TestCase):
    trait: Any = ...
    def setUp(self) -> None: ...
