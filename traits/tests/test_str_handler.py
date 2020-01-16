import unittest

from traits.api import HasTraits, Trait, TraitError, TraitHandler
from traits.trait_base import strx


# Validation via function
def validator(object, name, value):
    if isinstance(value, str):
        # arbitrary rule for testing
        if value.find("fail") < 0:
            return value
        else:
            raise TraitError
    else:
        raise TraitError


# Validation via Handler
class MyHandler(TraitHandler):
    def validate(self, object, name, value):
        try:
            value = strx(value)
            if value.find("fail") < 0:
                return value
        except:
            pass
        self.error(object, name, value)

        return

    def info(self):
        msg = "a string not containing the character sequence 'fail'"
        return msg


class Foo(HasTraits):
    s = Trait("", validator)


class Bar(HasTraits):
    s = Trait("", MyHandler())


class StrHandlerCase(unittest.TestCase):
    def test_validator_function(self):
        f = Foo()
        self.assertEqual(f.s, "")

        f.s = "ok"
        self.assertEqual(f.s, "ok")

        self.assertRaises(TraitError, setattr, f, "s", "should fail.")
        self.assertEqual(f.s, "ok")

        return

    def test_validator_handler(self):
        b = Bar()
        self.assertEqual(b.s, "")

        b.s = "ok"
        self.assertEqual(b.s, "ok")

        self.assertRaises(TraitError, setattr, b, "s", "should fail.")
        self.assertEqual(b.s, "ok")

        return
