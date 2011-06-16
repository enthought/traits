============
Introduction
============

This guide is designed to act as a conceptual guide to :term:`Traits UI`, an
open-source package built and maintained by Enthought, Inc. The Traits UI
package is a set of GUI (Graphical User Interface) tools designed to complement
:term:`Traits`, another Enthought open-source package that provides explicit
typing, validation, and change notification for Python. This guide is intended
for readers who are already moderately familiar with Traits; those who are not
may wish to refer to the *Traits User Manual* for an introduction. This guide
discusses many but not all features of Traits UI. For complete details of the
Traits UI API, refer to the *Traits API Reference*.

.. index:: MVC design pattern, Model-View-Controller, model, view (in MVC), controller

.. _the-model-view-controller-mvc-design-pattern:

The Model-View-Controller (MVC) Design Pattern
----------------------------------------------

A common and well-tested approach to building end-user applications is the
:term:`MVC` ("Model-View-Controller") design pattern. In essence, the MVC
pattern the idea that an application should consist of three separate entities:
a :term:`model`, which manages the data, state, and internal ("business") logic
of the application; one or more :term:`view`\ s, which format the model data into
a graphical display with which the end user can interact; and a
:term:`controller`, which manages the transfer of information between model and
view so that neither needs to be directly linked to the other. In practice,
particularly in simple applications, the view and controller are often so
closely linked as to be almost indistinguishable, but it remains useful to think
of them as distinct entities.

The three parts of the MVC pattern correspond roughly to three classes in the
Traits and Traits UI packages.

* Model: :term:`HasTraits` class (Traits package)
* View: View class (Traits UI package)
* Controller: :term:`Handler` class (Traits UI package)

The remainder of this section gives an overview of these relationships.

.. index:: HasTraits class; as MVC model

.. _the-model-hastraits-subclasses-and-objects:

The Model: HasTraits Subclasses and Objects
```````````````````````````````````````````

In the context of Traits, a model consists primarily of one or more subclasses
or :term:`instance`\ s of the HasTraits class, whose :term:`trait attribute`\ s
(typed attributes as defined in Traits) represent the model data. The specifics
of building such a model are outside the scope of this manual; please see the
*Traits User Manual* for further information.

.. index:: View; as MVC view

.. _the-view-view-objects:

The View: View Objects
``````````````````````

A view for a Traits-based application is an instance of a class called,
conveniently enough, View. A View object is essentially a display specification
for a GUI window or :term:`panel`. Its contents are defined in terms of
instances of two other classes: :term:`Item` and :term:`Group`. [1]_ These three
classes are described in detail in :ref:`the-view-and-its-building-blocks`; for
the moment, it is important to note that they are all defined independently of
the model they are used to display.

Note that the terms :term:`view` and :term:`View` are distinct for the purposes
of this document. The former refers to the component of the MVC design pattern;
the latter is a Traits UI construct.

.. index:: Handler class; as MVC controller

.. _the-controller-handler-subclasses-and-objects:

The Controller: Handler Subclasses and Objects
``````````````````````````````````````````````

The controller for a Traits-based application is defined in terms of the
:term:`Handler` class. [2]_ Specifically, the relationship between any given
View instance and the underlying model is managed by an instance of the Handler
class. For simple interfaces, the Handler can be implicit. For example, none of
the examples in the first four chapters includes or requires any specific
Handler code; they are managed by a default Handler that performs the basic
operations of window initialization, transfer of data between GUI and model, and
window closing. Thus, a programmer new to Traits UI need not be concerned with
Handlers at all. Nonetheless, custom handlers can be a powerful tool for
building sophisticated application interfaces, as discussed in
:ref:`controlling-the-interface-the-handler`.

.. index:: toolkit; selection

.. _toolkit-selection:

Toolkit Selection
-----------------

The Traits UI package is designed to be toolkit-independent. Programs that use
Traits UI do not need to explicitly import or call any particular GUI toolkit
code unless they need some capability of the toolkit that is not provided by
Traits UI. However, *some* particular toolkit must be installed on the system in
order to actually display GUI windows.

Traits UI uses a separate package, traits.etsconfig, to determine which GUI
toolkit to use. This package is also used by other Enthought packages that need
GUI capabilities, so that all such packages "agree" on a single GUI toolkit per
application. The etsconfig package contains a singleton object, **ETSConfig**
(importable from `traits.etsconfig.api`), which has a string attribute,
**toolkit**, that signifies the GUI toolkit.

.. index:: ETSConfig.toolkit

The values of **ETSConfig.toolkit** that are supported by Traits UI version 3
are:

.. index:: wxPython toolkit, Qt toolkit, null toolkit

* 'wx': `wxPython <http://www.wxpython.org>`_, which provides Python bindings 
  for the `wxWidgets <http://wxwidgets.org>`_ toolkit.
* 'qt4': `PyQt <http://riverbankcomputing.co.uk/pyqt/>`_, which provides Python
  bindings for the `Qt <http://trolltech.com/products/qt>`_ framework version 4.
* 'null': A do-nothing toolkit, for situations where neither of the other 
  toolkits is installed, but Traits is needed for non-UI purposes.

The default behavior of Traits UI is to search for available toolkit-specific
packages in the order listed, and uses the first one it finds. The programmer or
the user can override this behavior in any of several ways, in the following
order of precedence:

.. index:: ETS_TOOLKIT, environment variable; ETS_TOOLKIT, toolkit; flag
.. index:: toolkit; environment variable

#. The program can explicitly set **ETSConfig.toolkit**. It must do this before
   importing from any other Enthought Tool Suite component, including
   traits.  For example, at the beginning of a program::
   
       from traits.etsconfig.api import ETSConfig
       ETSConfig.toolkit = 'wx'

#. The user can specify a -toolkit flag on the command line of the program. 
#. The user can define a value for the ETS_TOOLKIT environment variable.


.. _structure-of-this-guide:

Structure of this Guide
-----------------------

The intent of this guide is to present the capabilities of the Traits UI package
in usable increments, so that you can create and display gradually more
sophisticated interfaces from one chapter to the next. 

* :ref:`the-view-and-its-building-blocks`, :ref:`customizing-a-view`, and 
  :ref:`advanced-view-concepts` show how to construct and display views from 
  the simple to the elaborate, while leaving such details as GUI logic and 
  widget selection to system defaults.
* :ref:`controlling-the-interface-the-handler` explains how to use the Handler 
  class to implement custom GUI behaviors, as well as menus and toolbars. 
* :ref:`traits-ui-themes` described how to customize the appearance of GUIs 
  through *themes*. 
* :ref:`introduction-to-trait-editor-factories` and 
  :ref:`the-predefined-trait-editor-factories` show how to control GUI widget
  selection by means of trait :term:`editor`\ s. 
* :ref:`tips-tricks-and-gotchas` covers miscellaneous additional topics.
* Further reference materials, including a :ref:`glossary-of-terms` and an API 
  summary for the Traits UI classes covered in this Guide, are located in the
  Appendices.

.. rubric:: Footnotes

.. [1] A third type of content object, Include, is discussed briefly in 
   :ref:`include-objects`, but presently is not commonly used.

.. [2] Not to be confused with the TraitHandler class of the Traits package, 
   which enforces type validation. 


