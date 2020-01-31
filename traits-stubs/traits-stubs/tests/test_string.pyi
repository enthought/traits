import unittest
from traits.api import HasTraits as HasTraits, String as String
from traits.testing.optional_dependencies import numpy as numpy, requires_numpy as requires_numpy
from typing import Any

class A(HasTraits):
    string: Any = ...

class TestString(unittest.TestCase):
    def test_accepts_numpy_string(self) -> None: ...
