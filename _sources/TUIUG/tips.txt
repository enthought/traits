
.. _tips-tricks-and-gotchas:

========================
Tips, Tricks and Gotchas
========================

Getting and Setting Model View Elements 
---------------------------------------

For some applications, it can be necessary to retrieve or manipulate the View
objects associated with a given model object. The HasTraits class defines two
methods for this purpose: trait_views() and trait_view().

.. _trait-views:

trait_views()
`````````````

The trait_views() method, when called without arguments, returns a list
containing the names of all Views defined in the object's class. For example, if
**sam** is an object of type SimpleEmployee3 (from 
:ref:`Example 6 <example-6-defining-multiple-view-objects-in-a-hastraits-class>`), 
the method call ``sam.trait_views()`` returns the list ``['all_view',
'traits_view']``.

Alternatively, a call to :samp:`trait_views({view_element_type})` returns a list
of all named instances of class *view_element_type* defined in the object's
class. The possible values of *view_element_type* are:

- :term:`View`
- :term:`Group`
- :term:`Item`
- :term:`ViewElement`
- ViewSubElement

Thus calling ``trait_views(View)`` is identical to calling ``trait_views()``.
Note that the call ``sam.trait_views(Group)`` returns an empty list, even though
both of the Views defined in SimpleEmployee contain Groups. This is because only
*named* elements are returned by the method.

Group and Item are both subclasses of ViewSubElement, while ViewSubElement and
View are both subclasses of ViewElement. Thus, a call to
``trait_views(ViewSubElement)`` returns a list of named Items and Groups, while
``trait_views(ViewElement)`` returns a list of named Items, Groups and Views.

trait_view()
````````````

The trait_view() method is used for three distinct purposes: 

- To retrieve the default View associated with an object
- To retrieve a particular named ViewElement (i.e., Item, Group or View)
- To define a new named ViewElement 

For example:

- ``obj.trait_view()`` returns the default View associated with object *obj*.
  For example, ``sam.trait_view()`` returns the View object called 
  ``traits_view``. Note that unlike trait_views(), trait_view() returns the
  View itself, not its name.
- ``obj.trait_view('my_view')`` returns the view element named ``my_view`` 
  (or None if ``my_view`` is not defined).
- ``obj.trait_view('my_group', Group('a', 'b'))`` defines a Group with the name
  ``my_group``. Note that although this Group can be retrieved using 
  ``trait_view()``, its name does not appear in the list returned by 
  ``traits_view(Group)``. This is because ``my_group`` is associated with
  *obj* itself, rather than with its class.


