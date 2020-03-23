from traits.api import HasTraits, BaseInstance


class Animal:
    pass


class Goldfish(Animal):
    pass


class Leprechaun:
    pass


class Test(HasTraits):
    animal = BaseInstance("Animal")
    animal2 = BaseInstance(Animal)


t = Test()
t.animal = Goldfish()
t.animal = Leprechaun()
t.animal = None
t.animal = Goldfish
t.animal = "sdf"
