from unittest import TestCase

from util import MypyAssertions


def code_block():
    from traits.api import HasTraits, String

    class Test(HasTraits):
        var = String()

    obj = Test()
    obj.var = "5"
    obj.var = 5  # {ERR}

    obj.var = False  # {ERR}
    obj.var = 5.5  # {ERR}

    obj.var = 5 + 4j  # {ERR}
    obj.var = True  # {ERR}


def code_block2():
    from traits.api import HasTraits, String

    class Test(HasTraits):
        var = String(minlen=5)


def code_block3():
    from traits.api import HasTraits, String

    class Test(HasTraits):
        var = String(minlen="5")  # {ERR}


class TestString(TestCase, MypyAssertions):

    def test_valid_values(self):
        self.assertRaisesMypyError(code_block)

    def test_valid_default_values(self):
        self.assertNoMypyError(code_block2)

    def test_invalid_default_values(self):
        self.assertRaisesMypyError(code_block3)
