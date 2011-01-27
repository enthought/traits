

.. _glossary-of-terms:

=============================
Appendix I: Glossary of Terms
=============================
.. glossary::
    
   attribute 
        An element of data that is associated with all instances of a given
        class, and is named at the class level. [19]_ In most cases, attributes
        are stored and assigned separately for each instance (for the exception, 
        see :term:`class attribute`). Synonyms include "data member" and 
        "instance variable".
        
   class attribute
        An element of data that is associated with a class, and is named at the
        class level. There is only one value for a class attribute, associated
        with the class itself. In contrast, for an instance :term:`attribute`,
        there is a value associated with every instance of a class.
        
   command button
        A button on a window that globally controls the window. Examples include
        :guilabel:`OK`, :guilabel:`Cancel`, :guilabel:`Apply`, 
        :guilabel:`Revert`, and:guilabel:` Help`. 
        
   controller
        The element of the :term:`MVC` ("model-view-controller") design pattern
        that manages the transfer of information between the data :term:`model`
        and the :term:`view` used to observe and edit it.
        
   dialog box 
        A secondary window whose purpose is for a user to specify additional
        information when entering a command.
        
   editor 
        A user interface component for editing the value of a trait attribute.
        Each type of trait has a default editor, but you can override this 
        selection with one of a number of editor factories provided by the 
        Traits UI package. In some cases an editor can include multiple widgets,
        e.g., a slider and a text box for a Range trait attribute. 
        
   editor factory 
        An instance of the Traits class EditorFactory. Editor factories generate
        the actual widgets used in a user interface. You can use an editor 
        factory without knowing what the underlying GUI toolkit is.
        
   factory
        An object used to produce other objects at run time without necessarily
        assigning them to named variables or attributes. A single factory is 
        often parameterized to produce instances of different classes as needed.
        
   Group 
        An object that specifies an ordered set of Items and other Groups for 
        display in a Traits UI View. Various display options can be specified 
        by means of attributes of this class, including a border, a group label,
        and the orientation of elements within the Group. An instance of the 
        Traits UI class Group.
        
   Handler
        A Traits UI object that implements GUI logic (data manipulation and
        dynamic window behavior) for one or more user interface windows. A 
        Handler instance fills the role of :term:`controller` in the MVC 
        design pattern. An instance of the Traits UI class :term:`Handler`.
        
   HasTraits 
        A class defined in the Traits package to specify objects whose 
        attributes are typed. That is, any attribute of a HasTraits subclass can
        be a :term:`trait attribute`.
        
   instance 
        A concrete entity belonging to an abstract category such as a class. In
        object-oriented programming terminology, an entity with allocated 
        memory storage whose structure and behavior are defined by the class 
        to which it belongs. Often called an :term:`object`.
                
   Item
        A non-subdividable element of a Traits user interface specification
        (View), usually specifying the display options to be used for a single
        trait attribute. An instance of the Traits UI class Item.
        
   live 
        A term used to describe a window that is linked directly to the
        underlying model data, so that changes to data in the interface are
        reflected immediately in the model. A window that is not live displays
        and manipulates a copy of the model data until the user confirms any
        changes.
        
   livemodal 
        A term used to describe a window that is both :term:`live` and
        :term:`modal`.
        
   MVC 
        A design pattern for interactive software applications. The initials
        stand for "Model-View-Controller", the three distinct entities 
        prescribed for designing such applications. (See the glossary entries
        for :term:`model`, :term:`view`, and :term:`controller`.)
        
   modal 
        A term used to describe a window that causes the remainder of the
        application to be suspended, so that the user can interact only with
        the window until it is closed.
        
   model 
        A component of the :term:`MVC` design pattern for interactive software
        applications. The model consists of the set of classes and objects that
        define the underlying data of the application, as well as any internal
        (i.e., non-GUI-related) methods or functions on that data.
        
   nonmodal 
        A term used to describe a window that is neither :term:`live` nor
        :term:`modal`.
        
   object
        Synonym for :term:`instance`.
        
   panel 
        A user interface region similar to a window except that it is embedded
        in a larger window rather than existing independently.
        
   predefined trait type
        Any trait type that is built into the Traits package.
        
   subpanel 
        A variation on a :term:`panel` that ignores (i.e., does not display) 
        any command buttons.
        
   trait 
        A term used loosely to refer to either a :term:`trait type` or a 
        :term:`trait attribute`.
        
   trait attribute
        An :term:`attribute` whose type is specified and checked by means of the
        Traits package.
        
   trait type 
        A type-checked data type, either built into or implemented by means of 
        the Traits package.
        
   Traits 
        An open source package engineered by Enthought, Inc. to perform explicit
        typing in Python.
        
   Traits UI 
        A high-level user interface toolkit designed to be used with the Traits
        package.
        
   View
        A template object for constructing a GUI window or panel for editing a
        set of traits. The structure of a View is defined by one or more Group
        or Item objects; a number of attributes are defined for specifying 
        display options including height and width, menu bar (if any), and the
        set of buttons (if any) that are displayed. A member of the Traits UI
        class View.
        
   view 
        A component of the :term:`MVC` design pattern for interactive software
        applications. The view component encompasses the visual aspect of the
        application, as opposed to the underlying data (the :term:`model`) and
        the application's behavior (the :term:`controller`).
        
   ViewElement 
        A View, Group or Item object. The ViewElement class is the parent of 
        all three of these subclasses.
        
   widget
        An interactive element in a graphical user interface, e.g., a scrollbar,
        button, pull-down menu or text box.
        
   wizard 
        An interface composed of a series of :term:`dialog box` windows, usually
        used to guide a user through an interactive task such as software 
        installation.
        
   wx 
        A shorthand term for the low-level GUI toolkit on which TraitsUI and
        PyFace are currently based (`wxWidgets <http://wxwidgets.org>`_) and its
        Python wrapper  (`wxPython <http://www.wxpython.org>`_). 

.. rubric:: Footnotes

.. [19] This is not always the case in Python, where attributes can be added to
   individual objects.
   
