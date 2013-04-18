## ex_traits_notification_06.py

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
    print( 'myTL[] fired. Name: %s' % name )
    print( new )
    print( self.myTL )

  ## define another handler for the list elements
  #@on_trait_change( 'myTL_items' )
  #def fired( self,name,new ):
  #  print( 'myTL_items fired. Name: %s' % name )
  #  print( new )
  #  print( self.myTL )

## -- Main ------------------------------------------------------------------

if __name__ == "__main__":

  # build an instantiation of the class
  traitedClass = TraitedClass()

  # fires the handler
  traitedClass.myTL[0] = 8

  # fires the handler
  traitedClass.myTL = [8,7,6,5]

  # fires the handler
  traitedClass.myTL.append(4)

  # fires the handler
  traitedClass.myTL.sort()

## -- EOF -------------------------------------------------------------------
