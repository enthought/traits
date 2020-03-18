from traits.api import HasTraits, Property, Float, Int


class TestClass(HasTraits):
    i = Int()
    prop1 = Property(Float)
    prop2 = Property(i)
    prop3 = Property(3)  # E: arg-type
    prop4 = Property(depends_on='i')
