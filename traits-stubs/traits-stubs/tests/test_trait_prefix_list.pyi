import unittest
from traits.api import HasTraits as HasTraits, Trait as Trait, TraitError as TraitError, TraitPrefixList as TraitPrefixList
from typing import Any

class A(HasTraits):
    foo: Any = ...

class TestTraitPrefixList(unittest.TestCase):
    def test_pickle_roundtrip(self) -> None: ...
