Traits Notification
===================

.. highlight:: python
  :linenothreshold: 5

.. toctree::
  :maxdepth: 2

Extended examples that demonstrate how to trigger handlers for changes
in Traits Lists and Dictionaries, and their individual elements.

.. todo:: Name Parameter

.. index:: Notification; Lists

Notification on Lists
---------------------

When passed a Traits List, the ``on_trait_change()`` events fire only when the
entire Traits List changes, not when elements of the List change.
::

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

produces::

  myTL: [1, 2, 3]
  on_trait_change() fired. Name: myTL. Value: [8, 7, 6, 5]

.. index:: Notification; List Items

Notification on List Items
--------------------------

To fire on items in the List, use the ``on_trait_change( 'myTL[]' )`` form of
the decorator
::

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

Results in::

  on_trait_change( myTL[] ) fired. Name: myTL_items
  New: [8]
  self.myTL: [8, 2, 3]
  on_trait_change( myTL[] ) fired. Name: myTL
  New: [8, 7, 6, 5]
  self.myTL: [8, 7, 6, 5]
  on_trait_change( myTL[] ) fired. Name: myTL_items
  New: [4]
  self.myTL: [8, 7, 6, 5, 4]
  on_trait_change( myTL[] ) fired. Name: myTL_items
  New: [4, 5, 6, 7, 8]
  self.myTL: [4, 5, 6, 7, 8]

Note that the ``@on_trait_change`` decorator appends the string ''_items'' to
the name of the object that changed. You can also use the following forms to
catch changes in the list items::

  # define another handler for the list elements
  @on_trait_change( 'myTL_items' )
  def fired( self,name,new ):
    print( 'myTL_items fired. Name: %s' % name )
    print( 'New: %s' % str(new) )
    print( 'self.myTL: %s' % str(self.myTL) )

  # define a handler for the list elements. No ``@on_trait_change( 'myTL[]' )``
  # decorator required
  def _myTL_items_changed( self,name,old,new ):
    print( 'myTL[] fired. Name: %s' % name )
    print( 'New: %s' % str(new) )
    print( 'self.myTL: %s' % str(self.myTL) )

.. index:: Notification; Dictionaries

Notification on Dictionaries
----------------------------

Traits Dictionaries behave very much like Trait Lists for notification purposes.
Handlers connected to dictionaries fire only when the entire dictionary changes.
::

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

produces::

  on_trait_change( myTD ) fired. Name: myTD
  New: {'fourth': 4, 'third': 3}
  self.myTD: {'fourth': 4, 'third': 3}

.. index:: Notification; Dictionary Items

Notification on Dictionary Items
--------------------------------

Detecting changes to Traits Dictionary items requires either an
``@on_trait_change( 'myTD_items' )`` decorator or a
``def _myTD_items_changed( self,name,old,new ):`` form of the handler name::

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

produces::

  @on_trait_change( myTD_items ) fired.
  Name: <__main__.TraitedClass object at 0x023D4630>
  New: <traits.trait_handlers.TraitDictEvent object at 0x023D5590>
    name.__dict__: {'myTD': {'second': 2, 'first': 42}}
    new.__dict__: {'removed': {}, 'added': {}, 'changed': {'first': 1}}

.. index:: Notification; Traits Name Prefixes

Notification on Traits Name Prefixes
------------------------------------

Traits allows us to define a prefix that will fire an ``on_trait_change()``
handler. The user passes the ``@on_trait_change()`` decorator a string of the form::

  prefix+

to match any trait attribute whose name begins with ''prefix''. For example,
::

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

produces::

  @on_trait_change( foo+ ) fired. Name: foo1TI, New: 8
  @on_trait_change( foo+ ) fired. Name: foo2TI, New: 9

