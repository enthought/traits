## ex_traits_notification_03.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Int, on_trait_change

class TraitedClass( HasTraits ):

  # define some Traits Ints
  foo1TI = Int( 2 )
  foo2TI = Int( 3 )

  notFooTI = Int( 4 )

  # define a handler
  @on_trait_change( 'foo+' )
  def fired( self,name,new ):
    print( '@on_trait_change( foo+ ) fired. Name: %s, New: %i' % (name,new) )

if __name__ == "__main__":

  tc = TraitedClass()

  # fires the handler
  tc.foo1TI = 8

  # fires the handler
  tc.foo2TI = 9

  # doesn't fire the handler
  tc.notFooIT = 10
