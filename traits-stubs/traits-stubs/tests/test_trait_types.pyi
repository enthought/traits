import unittest
from traits.testing.optional_dependencies import requires_numpy as requires_numpy
from traits.trait_type import TraitType as TraitType
from traits.trait_types import Float as Float

class TraitTypesTest(unittest.TestCase):
    def test_traits_shared_transient(self): ...
    def test_numpy_validators_loaded_if_numpy_present(self) -> None: ...
