from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import Float, HasTraits

    class Test(HasTraits):
        i = Float()

    o = Test()
    o.i = "5"  # {ERR}
    o.i = 5
    o.i = 5.5


class TestFloat(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)
