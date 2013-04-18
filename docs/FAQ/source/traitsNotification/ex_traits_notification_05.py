## ex_traits_notification_05.py

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
    print( '@on_trait_change( myTD_items ) fired.' )
    print( 'Name: %s\nNew: %s' % (name,new) )
    print( '  name.__dict__: %s\n  new.__dict__: %s' % (name.__dict__,new.__dict__) )

if __name__ == "__main__":

  tc = TraitedClass()

  ## read the data
  #print( tc.myTD )

  # change an element. fires the event
  tc.myTD['first'] = 42

  # change the entire dictionary. does not fire the event
  tc.myTD = {'third': 3, 'fourth': 4}
