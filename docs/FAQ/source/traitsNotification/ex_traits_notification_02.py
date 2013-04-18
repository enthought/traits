## ex_traits_notification_02.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, List, on_trait_change

class TraitedClass( HasTraits ):

  # define a Traits List. myTL = my Traits List
  myTL = List( value = [1,2,3] )

  # define a handler for the list elements
  @on_trait_change( 'myTL[]' )
  def fired( self,name,new ):
    print( 'on_trait_change( myTL[] ) fired. Name: %s' % name )
    print( 'New: %s' % str(new) )
    print( 'self.myTL: %s' % str(self.myTL) )

if __name__ == "__main__":

  tc = TraitedClass()

  # fires the handler
  tc.myTL[0] = 8

  # fires the handler
  tc.myTL = [8,7,6,5]

  # fires the handler
  tc.myTL.append(4)

  # fires the handler
  tc.myTL.sort()
