## ex_traits_Introspection_01.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Int

class TraitedClass( HasTraits ):

  # define a Traits Int and a python int.
  intTraits = Int(3)
  intPython = int(4)

  print( 'in TraitedClass' )
  print( type(intPython) )
  print( type(intTraits) )

if __name__ == "__main__":

  tc = TraitedClass()

  print( 'in Main' )
  print( type(tc.intPython) )
  print( type(tc.intTraits) )
