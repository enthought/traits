============
Introduction
============
The Traits package for the Python language allows Python programmers to use
a special kind of type definition called a trait. This document introduces the
concepts behind, and usage of, the Traits package.

For more information on the Traits package, refer to the `Traits GitHub
repository <http://github.com/enthought/traits>`_. For additional documentation
on the Traits package, refer to the `Traits API Reference
<https://docs.enthought.com/traits/traits_api_reference/index.html>`_

What Are Traits?
----------------
A trait is a type definition that can be used for normal Python object
attributes, giving the attributes some additional characteristics:

.. index:: initialization

* **Initialization**: A trait has a *default value*, which is
  automatically set as the initial value of an attribute, before its first
  use in a program.

.. index:: validation

* **Validation**: A trait attribute is *explicitly typed*. The type of a
  trait-based attribute is evident in the code, and only values that meet a
  programmer-specified set of criteria (i.e., the trait definition) can be
  assigned to that attribute. Note that the default value need not meet the
  criteria defined for assignment of values. Traits 4.0 also supports defining
  and using abstract interfaces, as well as adapters between interfaces.

.. index:: deferral

* **Deferral**: The value of a trait attribute can be contained either
  in the defining object or in another object that is *deferred to* by the
  trait.

.. index:: notification

* **Notification**: Setting the value of a trait attribute can *notify*
  other parts of the program that the value has changed.

.. index:: visualization

* **Visualization**: User interfaces that allow a user to *interactively
  modify* the values of trait attributes can be automatically constructed using
  the traits' definitions. This feature requires that a supported GUI
  toolkit be installed. However, if this feature is not used, the Traits package
  does not otherwise require GUI support. For details on the visualization
  features of Traits, see the `TraitsUI User Manual
  <http://docs.enthought.com/traitsui/traitsui_user_manual/index.html>`_.

A class can freely mix trait-based attributes with normal Python attributes,
or can opt to allow the use of only a fixed or open set of trait attributes
within the class. Trait attributes defined by a class are automatically
inherited by any subclass derived from the class.

The following example [1]_ illustrates each of the features of the Traits
package. These features are elaborated in the rest of this guide.

.. index:: examples; Traits features

::

    # all_traits_features.py --- Shows primary features of the Traits
    #                            package

    from traits.api import Delegate, HasTraits, Instance,\
                                     Int, Str
    class Parent ( HasTraits ):

        # INITIALIZATION: last_name' is initialized to '':
        last_name = Str( '' )


    class Child ( HasTraits ):

        age = Int

        # VALIDATION: 'father' must be a Parent instance:
        father = Instance( Parent )

        # DELEGATION: 'last_name' is delegated to father's 'last_name':
        last_name = Delegate( 'father' )

        # NOTIFICATION: This method is called when 'age' changes:
        def _age_changed ( self, old, new ):
            print('Age changed from %s to %s ' % ( old, new ))

    # Set up the example:
    joe = Parent()
    joe.last_name = 'Johnson'
    moe = Child()
    moe.father = joe

    # DELEGATION in action:
    print("Moe's last name is %s " % moe.last_name)
    # Result:
    # Moe's last name is Johnson

    # NOTIFICATION in action
    moe.age = 10
    # Result:
    # Age changed from 0 to 10

    # VISUALIZATION: Displays a UI for editing moe's attributes
    # (if a supported GUI toolkit is installed)
    moe.configure_traits()

Background
----------
Python does not require the data type of variables to be declared. As any
experienced Python programmer knows, this flexibility has both good and bad
points. The Traits package was developed to address some of the problems
caused by not having declared variable types, in those cases where problems
might arise. In particular, the motivation for Traits came as a direct result
of work done on Chaco, an open source scientific plotting package.

.. index:: Chaco

Chaco provides a set of high-level plotting objects, each of which has a number
of user-settable attributes, such as line color, text font, relative location,
and so on. To make the objects easy for scientists and engineers to use, the
attributes attempt to accept a wide variety and style of values. For example,
a color-related attribute of a Chaco object might accept any of the following
as legal values for the color red:

* 'red'
* 0xFF0000
* ( 1.0, 0.0, 0.0, 1.0 )

Thus, the user might write::

    plotitem.color = 'red'

In a predecessor to Chaco, providing such flexibility came at a cost:

* When the value of an attribute was used by an object internally (for example,
  setting the correct pen color when drawing a plot line), the object would
  often have to map the user-supplied value to a suitable internal
  representation, a potentially expensive operation in some cases.
* If the user supplied a value outside the realm accepted by the object
  internally, it often caused disastrous or mysterious program behavior.
  This behavior was often difficult to track down because the cause and effect
  were usually widely separated in terms of the logic flow of the program.

So, one of the main goals of the Traits package is to provide a form of type
checking that:

* Allows for flexibility in the set of values an attribute can have, such as
  allowing 'red', 0xFF0000 and ( 1.0, 0.0, 0.0, 1.0 ) as equivalent ways of
  expressing the color red.
* Catches illegal value assignments at the point of error, and provides a
  meaningful and useful explanation of the error and the set of allowable
  values.
* Eliminates the need for an object's implementation to map user-supplied
  attribute values into a separate internal representation.

In the process of meeting these design goals, the Traits package evolved into
a useful component in its own right, satisfying all of the above requirements
and introducing several additional, powerful features of its own. In projects
where the Traits package has been used, it has proven valuable for enhancing
programmers' ability to understand code, during both concurrent
development and maintenance.

The Traits |version| package works with versions 3.5 and later of
Python.  It is similar in some ways to the Python property language feature.
Standard Python properties provide the similar capabilities to the Traits
package, but with more work on the part of the programmer.

.. rubric:: Footnotes
.. [1] All code examples in this guide that include a file name are also
       available as examples in the tutorials/doc_examples/examples
       subdirectory of the Traits examples directory.  You can run them
       individually, or view them in a tutorial program by running:

       python <Traits dir>/examples/tutorials/tutor.py <Traits dir>/examples/tutorials/doc_examples
