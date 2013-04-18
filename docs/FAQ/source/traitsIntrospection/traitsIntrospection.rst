Introspection into Traits Variables
===================================

.. highlight:: python
  :linenothreshold: 5

.. toctree::
  :maxdepth: 2

At some point, you'll find yourself digging into the Python Traits code and
you'll want to do a little introspection on the variables and methods available
in the name space. There are a several idiosyncrasies associated with
how Traits manages variables that can make introspection quite non-intuitive.

.. index:: Introspection; Python

Overview of Python's Introspection Abilities
--------------------------------------------

Python provides an ``inspect`` module::

  import inspect

which supplies useful functions which allow you to look at objects and their
attributes. We'll concern ourselves mainly with ``inspect.getmembers()`` which
returns the members of an object in a list of (name, value) pairs sorted
by name. The ``inspect.getmembers()`` method usually returns too much data for
Traits objects and we have to filter the results to produce useful
data. For example, the following code::

  ## ex_traits_Introspection_03.py

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

    # get the (very large) list of class members
    membersList = inspect.getmembers( tc )
    print( membersList )

produces a list of 113 (name, value) pairs. We can filter the (name, value)
list to exclude private entries (i.e. those entries beginning with an
underscore) from the list using::

  publicList = [thisItem for thisItem in membersList if thisItem[0][0] != '_']

List ``publicList`` is now only 50 entries long::

  publicList
  [
  ('add_class_trait', <bound method MetaHasTraits.add_class_trait of <class '__main__.TraitedClass'>>),
  ('add_trait', <bound method TraitedClass.add_trait of <__main__.TraitedClass object at 0x02A24630>>),
  ('add_trait_category', <bound method MetaHasTraits.add_trait_category of <class '__main__.TraitedClass'>>),
  ('add_trait_listener', <bound method TraitedClass.add_trait_listener of <__main__.TraitedClass object at 0x02A24630>>),
  ('all_trait_names', <bound method TraitedClass.all_trait_names of <__main__.TraitedClass object at 0x02A24630>>),
  ('base_trait', <bound method TraitedClass.base_trait of <__main__.TraitedClass object at 0x02A24630>>),
  ('class_default_traits_view', <bound method MetaHasTraits.class_default_traits_view of <class '__main__.TraitedClass'>>),
  ('class_editable_traits', <bound method MetaHasTraits.class_editable_traits of <class '__main__.TraitedClass'>>),
  ('class_trait_names', <bound method MetaHasTraits.class_trait_names of <class '__main__.TraitedClass'>>),
  ('class_trait_view', <bound method MetaHasTraits.class_trait_view of <class '__main__.TraitedClass'>>),
  ('class_trait_view_elements', <bound method MetaHasTraits.class_trait_view_elements of <class '__main__.TraitedClass'>>),
  ('class_traits', <bound method MetaHasTraits.class_traits of <class '__main__.TraitedClass'>>),
  ('clone_traits', <bound method TraitedClass.clone_traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('configure_traits', <bound method TraitedClass.configure_traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('copy_traits', <bound method TraitedClass.copy_traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('copyable_trait_names', <bound method TraitedClass.copyable_trait_names of <__main__.TraitedClass object at 0x02A24630>>),
  ('default_traits_view', <bound method TraitedClass.default_traits_view of <__main__.TraitedClass object at 0x02A24630>>),
  ('edit_traits', <bound method TraitedClass.edit_traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('editable_traits', <bound method TraitedClass.editable_traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('get', <bound method TraitedClass.trait_get of <__main__.TraitedClass object at 0x02A24630>>),
  ('has_traits_interface', <bound method TraitedClass.has_traits_interface of <__main__.TraitedClass object at 0x02A24630>>),
  ('myFloat', 6.7),
  ('myInt', 5),
  ('on_trait_change', <bound method TraitedClass.on_trait_change of <__main__.TraitedClass object at 0x02A24630>>),
  ('on_trait_event', <bound method TraitedClass.on_trait_change of <__main__.TraitedClass object at 0x02A24630>>),
  ('print_traits', <bound method TraitedClass.print_traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('remove_trait', <bound method TraitedClass.remove_trait of <__main__.TraitedClass object at 0x02A24630>>),
  ('remove_trait_listener', <bound method TraitedClass.remove_trait_listener of <__main__.TraitedClass object at 0x02A24630>>),
  ('reset_traits', <bound method TraitedClass.reset_traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('set', <bound method TraitedClass.trait_set of <__main__.TraitedClass object at 0x02A24630>>),
  ('set_trait_dispatch_handler', <bound method MetaHasTraits.set_trait_dispatch_handler of <class '__main__.TraitedClass'>>),
  ('sync_trait', <bound method TraitedClass.sync_trait of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait', <bound method TraitedClass.trait of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_context', <bound method TraitedClass.trait_context of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_get', <bound method TraitedClass.trait_get of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_items_event', <built-in method trait_items_event of TraitedClass object at 0x02A24630>),
  ('trait_monitor', <bound method MetaHasTraits.trait_monitor of <class '__main__.TraitedClass'>>),
  ('trait_names', <bound method TraitedClass.trait_names of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_property_changed', <built-in method trait_property_changed of TraitedClass object at 0x02A24630>),
  ('trait_set', <bound method TraitedClass.trait_set of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_setq', <bound method TraitedClass.trait_setq of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_subclasses', <bound method MetaHasTraits.trait_subclasses of <class '__main__.TraitedClass'>>),
  ('trait_view', <bound method TraitedClass.trait_view of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_view_elements', <bound method TraitedClass.trait_view_elements of <__main__.TraitedClass object at 0x02A24630>>),
  ('trait_views', <bound method TraitedClass.trait_views of <__main__.TraitedClass object at 0x02A24630>>),
  ('traits', <bound method TraitedClass.traits of <__main__.TraitedClass object at 0x02A24630>>),
  ('traits_init', <built-in method traits_init of TraitedClass object at 0x02A24630>),
  ('traits_inited', <built-in method traits_inited of TraitedClass object at 0x02A24630>),
  ('validate_trait', <bound method TraitedClass.validate_trait of <__main__.TraitedClass object at 0x02A24630>>),
  ('wrappers',
    { 'new': <class traits.trait_notifiers.NewTraitChangeNotifyWrapper at 0x027F1458>,
      'ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x027F13E8>,
      'extended': <class traits.trait_notifiers.ExtendedTraitChangeNotifyWrapper at 0x027F13B0>,
      'fast_ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x027F13E8>,
      'same': <class traits.trait_notifiers.TraitChangeNotifyWrapper at 0x027F1378>})
  ]

This list shows many of the Trait management methods. It also shows two of
our TraitedClass variables, ``myInt`` and ``myFloat``. However, the Traits variable
``myTI`` is missing. We'll get to that later.

We can filter the output of the inspect.getmembers()
method in any arbitrary fashion. For example, we can filter on the first
two characters::

  myList = [thisItem for thisItem in membersList if thisItem[0][0:2] == 'my']
  myList
  [('myFloat', 6.7), ('myInt', 5)]

Again, we see the two python attributes but do not see the Traits ``myTI``
attribute.

Traits itself occasionally provides a ``print_traits()`` method. If we break in
the main routine above, anytime after the traitedClass object is
instantiated, we can perform::

  print( tc.print_traits() )

and obtain
::

  myTI: 3

We've finally seen the ``myTI`` Trait! For reference, the full introspection
code is::

  ## ex_traits_Introspection_04.py

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

    # build the object
    tc = TraitedClass()

    # get the (very large) list of class members
    membersList = inspect.getmembers( tc )
    print( membersList )

    # retrieve only the public members of the list
    publicList = [thisItem for thisItem in membersList if thisItem[0][0] != '_']
    print( publicList )

    # retrive only the members beginning with "my"
    myList = [thisItem for thisItem in membersList if thisItem[0][0:2] == 'my']
    print( myList )

    # try print_traits
    print( tc.print_traits() )

.. index::
  pair: Introspection; Traits

Traits Introspection
--------------------

Let's look at some Traits-specific introspection::

  ## ex_traits_Introspection_01.py

  # standard imports
  import inspect

  # Enthought imports
  from traits.api import HasTraits, Int

  class TraitedClass( HasTraits ):

    # define a Traits Int and a python int.
    intTraits = Int(3)
    intPython = int(4)

    print( 'in TraitedClass' )
    print( type(intPython) )
    print( type(intTraits) )

  if __name__ == "__main__":

    tc = TraitedClass()

    print( 'in Main' )
    print( type(tc.intPython) )
    print( type(tc.intTraits) )

which produces::

  in TraitedClass
  <type 'int'>
  <class 'traits.trait_types.Int'>
  in Main
  <type 'int'>
  <type 'int'>

Inside of the TraitedClass class, the two types of integers are different. The
``intPython`` variable is a ``<type 'int'>`` while the ``intTraits`` is a
``<class 'traits.trait_types.Int'>``. Inspecting the same variables in the main
routine produces ``<type 'int'>`` for both ``intPython`` and ``intTraits``.
Passing through the method return has converted ``intTraits`` from a ``<class
'traits.trait_types.Int'>`` into a ``<type 'int'>``. What's going on?

**WARNING: Python Black Magic ahead**

There are a few areas of Python that are regarded as Black Magic, and
this is one of them. In the Traits package, the authors are customizing class
creation using a metaclass. Python is *extremely* flexible, and one of the
attributes you can change is class creation. The idea is that Python
metaclasses allow you to change how classes get created via the __new__()
method. So when you write something like this::

  class TraitedClass( HasTraits ):
    '''illustrates Traits introspection'''

    # a Traits Int
    myTI = Int( 3 )

    # a python Int, Float
    myInt = 5
    myFloat = 6.7

It's not going through your typical class creation process.  HasTraits
has a metaclass, and it's changing how TraitedClass works. It appears that the
metaclass is walking over the class definition and extracting traited members,
and wiring them up correctly to operate in the traits ecosystem. The saying is,
"If you don't know how metaclasses work in Python, then you don't need them."

Using metaclasses, any Traits variable (e.g. List, Str, Int, Float, etc) behaves
exactly like a normal Python variables (e.g. list, str, int, float, etc), yet
the Traits code is listening for Traits Events behind the scenes.

This effect also implies that you have to be careful when handling Traited
variables before they've undergone their conversion from a Traits class to a
python class. The following code throws an error::

  ## ex_traits_Introspection_05.py

  # standard imports
  import inspect

  # Enthought imports
  from traits.api import HasTraits, Int

  class TraitedClass( HasTraits ):
    '''play with Traits and Introspection'''

    # define a Traits Int and a python int.
    intTraits = Int(3)
    intPython = int(4)

    # this statement will work because intPython is a true Python
    # integer
    foo = intPython + 8

    # this statement will throw an error because the Traits Int has not
    # yet been converted to a Python integer. This conversion happens when
    # the method constructor returns.
    foo = intTraits + 8

  if __name__ == "__main__":

    # build an instantiation of the class
    traitedClass = TraitedClass()

The error is::

  Traceback (most recent call last):
    File "C:\Users\Kevin\Documents\My OS\Enthought\Traits\traitsIntrospection\ex_traits_Introspection_05.py", line 18, in <module>
      class TraitedClass( HasTraits ):
    File "C:\Users\Kevin\Documents\My OS\Enthought\Traits\traitsIntrospection\ex_traits_Introspection_05.py", line 32, in TraitedClass
      foo = intTraits + 8
  TypeError: unsupported operand type(s) for +: 'Int' and 'int'

However, the following code executes sucessfully because the addition happens
after the ``<class 'traits.trait_types.Int'>`` is converted into a ``<type
'int'>`` at the constructor return.
::

  ## ex_traits_Introspection_06.py

  # standard imports
  import inspect

  # Enthought imports
  from traits.api import HasTraits, Int

  class TraitedClass( HasTraits ):
    '''play with Traits and Introspection'''

    # define a Traits Int and a python int.
    intTraits = Int(3)
    intPython = int(4)

  if __name__ == "__main__":

    # build an instantiation of the class
    tc = TraitedClass()

    # Both of these statements work because both intPython and intTraits
    # are now true Python integers
    foo = tc.intPython + 8
    foo = tc.intTraits + 8

.. index:: Initialization; Lazy Initialization
.. index:: Lazy Initialization

Lazy Initialization
-------------------

Now, let's investigate the missing Traits variable, ``myTI``. The following code
illustrates the issue.
::

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

The output is::

  before accessing tc.myTI
  [('myFloat', 6.7), ('myInt', 5)]
  after accessing tc.myTI
  [('myFloat', 6.7), ('myInt', 5), ('myTI', 3)]

The Traits variable ``myTI`` isn't present in the object until we ask to read
the variable. The reason is that Traits uses Lazy Initialization on the Traits
of an Instance. When you build a method containing Traited variables,
those variables won't exist in the method until they are explicitly set
or got. In the example above, ``myTI`` didn't exist until we asked for it.

The statement ``myTI = Int( 3 )`` set ``myTI`` to an initial value of 3.
However, setting a variable to its default value in the initialization doesn't
count as setting the variable. These rules affect when when an Event is fired.
::

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

This code produces::

  adding 2
  _myTI_changed() fired. old: 3, new: 5
  adding 0

According to Traits, ``myTI`` was set only once, in the ``__main__`` routine, when
we added two to it. The initialization and adding zero do not count as
changes to ``myTI``.
