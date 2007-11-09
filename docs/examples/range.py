# range.py --- Example of the Range() trait factory
from enthought.traits.api import HasTraits, Range

class GuiSplitter(HasTraits):
    bar_size = Range(1, 15, value=4)
