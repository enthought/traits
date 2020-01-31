import unittest
from traits.api import Array as Array, Bool as Bool, HasTraits as HasTraits
from traits.testing.optional_dependencies import numpy as numpy, requires_numpy as requires_numpy
from typing import Any

class Foo(HasTraits):
    a: Any = ...
    event_fired: Any = ...

class ArrayTestCase(unittest.TestCase):
    def test_zero_to_one_element(self) -> None: ...
