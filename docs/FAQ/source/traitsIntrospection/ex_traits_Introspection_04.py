## ex_traits_Introspection_04.py

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

  # build the object
  tc = TraitedClass()

  # get the (very large) list of class members
  membersList = inspect.getmembers( tc )
  print( membersList )

  # retrieve only the public members of the list
  publicList = [thisItem for thisItem in membersList if thisItem[0][0] != '_']
  print( publicList )

  # retrive only the members beginning with "my"
  myList = [thisItem for thisItem in membersList if thisItem[0][0:2] == 'my']
  print( myList )

  # try print_traits
  print( tc.print_traits() )
