from traits.api import HasTraits, Instance


class Friut:
    info = "good for you"


class Orange(Friut):
    pass


class Pizza:
    pass


class TestClass(HasTraits):
    itm = Instance(Friut)


obj = TestClass()
obj.itm = Orange()
obj.itm = Pizza()
