## ex_traits_Introspection_07.py

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

  # get the (very large) list of class members, then filter on the variables
  # beginning with "my". myTI is missing
  membersList = inspect.getmembers( tc )
  myList = [thisItem for thisItem in membersList if thisItem[0][0:2] == 'my']
  print( 'before accessing tc.myTI' )
  print( myList )

  # access myTI
  foo = tc.myTI + 2

  # do it again. get the list of class members and look for the my* variables
  # myTI is now present
  membersList = inspect.getmembers( tc )
  myList = [thisItem for thisItem in membersList if thisItem[0][0:2] == 'my']
  print( 'after accessing tc.myTI' )
  print( myList )
