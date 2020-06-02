from traits.api import WeakRef, HasTraits


class Fruit:
    pass


class TestClass(HasTraits):
    atr = WeakRef(Fruit)
    atr2 = WeakRef(Fruit())
    atr3 = WeakRef("Fruit")
