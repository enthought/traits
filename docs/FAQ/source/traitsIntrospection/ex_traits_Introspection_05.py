## ex_traits_Introspection_05.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Int

class TraitedClass( HasTraits ):
  '''play with Traits and Introspection'''

  # define a Traits Int and a python int.
  intTraits = Int(3)
  intPython = int(4)

  # this statement will work because intPython is a true Python
  # integer
  foo = intPython + 8

  # this statement will throw an error because the Traits Int has not
  # yet been converted to a Python integer. This conversion happens when
  # the method constructor returns.
  foo = intTraits + 8

if __name__ == "__main__":

  # build an instantiation of the class
  traitedClass = TraitedClass()

