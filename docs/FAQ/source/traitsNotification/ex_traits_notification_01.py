## ex_traits_notification_01.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, List, on_trait_change

class TraitedClass( HasTraits ):

  # define a Traits List. myTL = my Traits List
  myTL = List( value = [1,2,3] )

  # define a handler
  @on_trait_change( 'myTL' )
  def fired( self,name,new ):
    print( 'on_trait_change() fired. Name: %s. Value: %s' % (name,str(new)) )

if __name__ == "__main__":

  tc = TraitedClass()
  print( 'myTL: %s' % str(tc.myTL) )

  # does not fire the handler
  tc.myTL[0] = 8

  # fires the handler
  tc.myTL = [8,7,6,5]

  # does not fire the handler
  tc.myTL.append(4)
