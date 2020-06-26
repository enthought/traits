from traits.api import Float, HasTraits, Interface, provides, Str, Tuple


class IHasName(Interface):
    name = Str()


@provides(IHasName)
class NamedColor(HasTraits):
    name = Str()

    rgb = Tuple(Float, Float, Float)


named_color = NamedColor(name="green", rgb=(0.0, 1.0, 0.0))
