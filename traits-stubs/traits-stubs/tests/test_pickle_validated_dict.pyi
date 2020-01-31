import unittest
from traits.api import Dict as Dict, HasTraits as HasTraits, Int as Int, List as List
from typing import Any

class C(HasTraits):
    a: Any = ...
    def __init__(self) -> None: ...

class PickleValidatedDictTestCase(unittest.TestCase):
    def test_pickle_validated_dict(self) -> None: ...
