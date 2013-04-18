## ex_traits_Introspection_03.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Int

class TraitedClass( HasTraits ):
  '''illustrates Traits introspection'''

  # a Traits Int
  myTI = Int( 3 )

  # a python Int, Float
  myInt = 5
  myFloat = 6.7

if __name__ == "__main__":

  tc = TraitedClass()

  # get the (very large) list of class members
  membersList = inspect.getmembers( tc )
  print( membersList )
