## ex_traits_notification_04.py

# standard imports
import inspect

# Enthought imports
from traits.api import HasTraits, Dict, on_trait_change

class TraitedClass( HasTraits ):

  # a Traits dictionary. myTD = my Traits Dictionary
  myTD = Dict( {'first': 1, 'second': 2} )

  # define a handler
  @on_trait_change( 'myTD' )
  def fired( self,name,new ):
    print( 'on_trait_change( myTD ) fired. Name: %s' % name )
    print( 'New: %s' % str(new) )
    print( 'self.myTD: %s' % str(self.myTD) )

if __name__ == "__main__":

  tc = TraitedClass()

  # change an element. not fired
  tc.myTD['first'] = 42

  # change the entire dictionary. fires
  tc.myTD = {'third': 3, 'fourth': 4}
