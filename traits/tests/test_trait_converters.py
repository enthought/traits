from contextlib import contextmanager
import unittest

from traits.ctrait import CTrait
from traits.trait_converters import (
    check_trait,
    mapped_trait_for,
    trait_cast,
    trait_for,
    trait_from,
)
from traits.trait_factory import TraitFactory
from traits.trait_handlers import TraitCastType, TraitInstance
from traits.api import Any, Int


@contextmanager
def reset_trait_factory():
    from traits import trait_factory
    old_tfi = trait_factory._trait_factory_instances.copy()
    try:
        yield
    finally:
        trait_factory._trait_factory_instances = old_tfi


class TestTraitCast(unittest.TestCase):

    def test_trait_cast_ctrait(self):
        ct = Int().as_ctrait()

        result = trait_cast(ct)

        self.assertIs(result, ct)

    def test_trait_cast_trait_type_class(self):
        result = trait_cast(Int)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, Int)

    def test_trait_cast_trait_type_instance(self):
        trait = Int()

        result = trait_cast(trait)

        self.assertIsInstance(result, CTrait)
        self.assertIs(result.handler, trait)

    def test_trait_cast_trait_factory(self):
        int_trait_factory = TraitFactory(lambda: Int().as_ctrait())

        with reset_trait_factory():
            result = trait_cast(int_trait_factory)
            ct = int_trait_factory.as_ctrait()

        self.assertIsInstance(result, CTrait)
        self.assertIs(result, ct)

    def test_trait_cast_none(self):
        result = trait_cast(None)

        self.assertIsNone(result)

    def test_trait_cast_other(self):
        result = trait_cast(1)

        self.assertIsNone(result)


class TestTraitFrom(unittest.TestCase):

    def test_trait_from_ctrait(self):
        ct = Int().as_ctrait()

        result = trait_from(ct)

        self.assertIs(result, ct)

    def test_trait_from_trait_type_class(self):
        result = trait_from(Int)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, Int)

    def test_trait_from_trait_type_instance(self):
        trait = Int()

        result = trait_from(trait)

        self.assertIsInstance(result, CTrait)
        self.assertIs(result.handler, trait)

    def test_trait_from_trait_factory(self):
        int_trait_factory = TraitFactory(lambda: Int().as_ctrait())

        with reset_trait_factory():
            result = trait_from(int_trait_factory)
            ct = int_trait_factory.as_ctrait()

        self.assertIsInstance(result, CTrait)
        self.assertIs(result, ct)

    def test_trait_from_none(self):
        result = trait_from(None)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, Any)

    def test_trait_from_other(self):
        result = trait_from(1)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, TraitCastType)
        self.assertEqual(result.handler.aType, int)


class TestCheckTrait(unittest.TestCase):

    def test_check_trait_ctrait(self):
        ct = Int().as_ctrait()

        result = check_trait(ct)

        self.assertIs(result, ct)

    def test_check_trait_trait_type_class(self):
        result = check_trait(Int)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, Int)

    def test_check_trait_trait_type_instance(self):
        trait = Int()

        result = check_trait(trait)

        self.assertIsInstance(result, CTrait)
        self.assertIs(result.handler, trait)

    def test_check_trait_trait_factory(self):
        int_trait_factory = TraitFactory(lambda: Int().as_ctrait())

        with reset_trait_factory():
            result = check_trait(int_trait_factory)
            ct = int_trait_factory.as_ctrait()

        self.assertIsInstance(result, CTrait)
        self.assertIs(result, ct)

    def test_check_trait_none(self):
        result = check_trait(None)

        self.assertIsNone(result)

    def test_check_trait_other(self):
        result = check_trait(1)

        self.assertEqual(result, 1)


class TestTraitFor(unittest.TestCase):

    def test_trait_for_ctrait(self):
        ct = Int().as_ctrait()

        result = trait_for(ct)

        self.assertIs(result, ct)

    def test_trait_for_trait_type_class(self):
        result = trait_for(Int)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, Int)

    def test_trait_for_trait_type_instance(self):
        trait = Int()

        result = trait_for(trait)

        self.assertIsInstance(result, CTrait)
        self.assertIs(result.handler, trait)

    def test_trait_for_trait_factory(self):
        int_trait_factory = TraitFactory(lambda: Int().as_ctrait())

        with reset_trait_factory():
            result = trait_for(int_trait_factory)
            ct = int_trait_factory.as_ctrait()

        self.assertIsInstance(result, CTrait)
        self.assertIs(result, ct)

    def test_trait_for_none(self):
        result = trait_for(None)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, TraitInstance)
        self.assertEqual(result.handler.aClass, type(None))

    def test_trait_for_other(self):
        result = trait_for(1)

        self.assertIsInstance(result, CTrait)
        self.assertIsInstance(result.handler, TraitCastType)
        self.assertEqual(result.handler.aType, int)
