## ex_traits_notification_07.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Dict, on_trait_change

class TraitedClass( HasTraits ):

  # a Traits dictionary
  myTD = Dict( {'first': 1, 'second': 2} )

  ## define a handler
  @on_trait_change( 'myTD_items' )
  def fired( self,name,old,new ):
    print( 'fired. Name: %s\nNew: %s' % (name,new) )
    print( '  name.__dict__: %s\n  new.__dict__: %s' % (name.__dict__,new.__dict__) )

  # also works
  #def _myTD_items_changed( self,name,old,new ):
  #  print( 'fired. Name: %s\nNew: %s' % (name,new) )
  #  print( '  new.__dict__: %s' % new.__dict__ )

## -- Main ------------------------------------------------------------------

if __name__ == "__main__":

  # build an instantiation of the class
  traitedClass = TraitedClass()

  # read the data
  print( traitedClass.myTD )

  # change an element. fires the event
  traitedClass.myTD['first'] = 42
  print( traitedClass.myTD )

  # change the entire dictionary. does not fire the event
  traitedClass.myTD = {'third': 3, 'fourth': 4}
  print( traitedClass.myTD )

## -- EOF -------------------------------------------------------------------
