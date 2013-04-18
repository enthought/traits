## ex_traits_Introspection_08.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Int

class TraitedClass( HasTraits ):
  '''illustrates Traits introspection'''

  # a Traits Int
  myTI = Int( 3 )

  # fire when myTI changes
  def _myTI_changed( self,old,new ):
    '''prints when fired'''
    print( '_myTI_changed() fired. old: %i, new: %i' % (old,new) )

if __name__ == "__main__":

  tc = TraitedClass()

  # myTI changes. _myTI_changed() fires
  print( 'adding 2' )
  tc.myTI = tc.myTI + 2

  # myTI accessed, but not changed. _myTI_changed() does not fire.
  print( 'adding 0' )
  tc.myTI = tc.myTI + 0
