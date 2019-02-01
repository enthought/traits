""" Tests for the the "anytrait" static notifiers. """
import unittest

from traits import trait_notifiers
from traits.api import Float, HasTraits, Undefined


anycalls_0 = []


class AnytraitStaticNotifiers0(HasTraits):
    ok = Float

    def _anytrait_changed():
        anycalls_0.append(True)


class AnytraitStaticNotifiers0Fail(HasTraits):
    fail = Float

    def _anytrait_changed():
        raise Exception("error")


class AnytraitStaticNotifiers1(HasTraits):
    ok = Float

    def _anytrait_changed(self):
        if not hasattr(self, "anycalls"):
            self.anycalls = []
        self.anycalls.append(True)


class AnytraitStaticNotifiers1Fail(HasTraits):
    fail = Float

    def _anytrait_changed(self):
        raise Exception("error")


class AnytraitStaticNotifiers2(HasTraits):
    ok = Float

    def _anytrait_changed(self, name):
        if not hasattr(self, "anycalls"):
            self.anycalls = []
        self.anycalls.append(name)


class AnytraitStaticNotifiers2Fail(HasTraits):
    fail = Float

    def _anytrait_changed(self, name):
        raise Exception("error")


class AnytraitStaticNotifiers3(HasTraits):
    ok = Float

    def _anytrait_changed(self, name, new):
        if not hasattr(self, "anycalls"):
            self.anycalls = []
        self.anycalls.append((name, new))


class AnytraitStaticNotifiers3Fail(HasTraits):
    fail = Float

    def _anytrait_changed(self, name, new):
        raise Exception("error")


class AnytraitStaticNotifiers4(HasTraits):
    ok = Float

    def _anytrait_changed(self, name, old, new):
        if not hasattr(self, "anycalls"):
            self.anycalls = []
        self.anycalls.append((name, old, new))


class AnytraitStaticNotifiers4Fail(HasTraits):
    fail = Float

    def _anytrait_changed(self, name, old, new):
        raise Exception("error")


class TestNotifiers(unittest.TestCase):
    """ Tests for the static notifiers, and the "anytrait" static notifiers.
    """

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.exceptions = []
        trait_notifiers.push_exception_handler(self._handle_exception)

    def tearDown(self):
        trait_notifiers.pop_exception_handler()

    #### Private protocol #####################################################

    def _handle_exception(self, obj, name, old, new):
        self.exceptions.append((obj, name, old, new))

    #### Tests ################################################################

    def test_anytrait_static_notifiers_0(self):
        obj = AnytraitStaticNotifiers0(ok=2)
        obj.ok = 3

        self.assertEqual(len(anycalls_0), 2)

    def test_anytrait_static_notifiers_1(self):
        obj = AnytraitStaticNotifiers1(ok=2)
        obj.ok = 3

        # 3 calls (see test_anytrait_static_notifiers_4):
        # 1 to add trait 'anycalls',
        # 1 from the constructor,
        # 1 to set ok to 3
        self.assertEqual(len(obj.anycalls), 3)

    def test_anytrait_static_notifiers_2(self):
        obj = AnytraitStaticNotifiers2(ok=2)
        obj.ok = 3

        expected = ["trait_added", "ok", "ok"]
        self.assertEqual(expected, obj.anycalls)

    def test_anytrait_static_notifiers_3(self):
        obj = AnytraitStaticNotifiers3(ok=2)
        obj.ok = 3

        expected = [("trait_added", "anycalls"), ("ok", 2), ("ok", 3)]
        self.assertEqual(expected, obj.anycalls)

    def test_anytrait_static_notifiers_4(self):
        obj = AnytraitStaticNotifiers4(ok=2)
        obj.ok = 3

        expected = [
            ("trait_added", Undefined, "anycalls"),
            ("ok", 0, 2),
            ("ok", 2, 3),
        ]
        self.assertEqual(expected, obj.anycalls)

    def test_anytrait_static_notifiers_0_fail(self):
        obj = AnytraitStaticNotifiers0Fail()
        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_anytrait_static_notifiers_1_fail(self):
        obj = AnytraitStaticNotifiers1Fail()
        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_anytrait_static_notifiers_2_fail(self):
        obj = AnytraitStaticNotifiers2Fail()
        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_anytrait_static_notifiers_3_fail(self):
        obj = AnytraitStaticNotifiers3Fail()
        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_anytrait_static_notifiers_4_fail(self):
        obj = AnytraitStaticNotifiers4Fail()
        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])
