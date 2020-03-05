from traits.api import HasTraits, Instance


class Fruit:
    info = "good for you"


class Orange(Fruit):
    pass


class Pizza:
    pass


class TestClass(HasTraits):
    itm = Instance(Fruit)


obj = TestClass()
obj.itm = Orange()
obj.itm = Pizza()
