from traits.api import Enum, HasTraits


class TestClass(HasTraits):
    en = Enum("foo", "bar", "baz")



