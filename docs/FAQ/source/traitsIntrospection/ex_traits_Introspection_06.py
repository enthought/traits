## ex_traits_Introspection_06.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Int

class TraitedClass( HasTraits ):
  '''play with Traits and Introspection'''

  # define a Traits Int and a python int.
  intTraits = Int(3)
  intPython = int(4)

if __name__ == "__main__":

  # build an instantiation of the class
  tc = TraitedClass()

  # Both of these statements work because both intPython and intTraits
  # are now true Python integers
  foo = tc.intPython + 8
  foo = tc.intTraits + 8

