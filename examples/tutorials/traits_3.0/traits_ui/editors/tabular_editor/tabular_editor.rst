The TabularEditor
=================

Traits 3.0 introduces a new editor, called the **TabularEditor**, located in the
*traitsui.wx.extras.tabular_editor* module that can be used for many
of the same purposes as the existing **TableEditor**. However, while similar in
function, each editor has its own particular strengths and weaknesses.

Some of the strengths of the new **TabularEditor** are:

- **Very fast**. The editor uses a *virtual* model which only accesses data
  from the underlying data model as needed. For example, if you have a million
  element array, but can only view 50 rows at a time, the editor will only 
  request 50 rows at a time.
  
- **Very flexible data model**. The editor uses a new adapter model for 
  interfacing with your underlying data that allows it to easily deal with many
  types of data representation: from lists of objects, to arrays of numbers, to
  tuples of tuples, and many other formats as well.
  
- **Supports a useful set of data operations**. The editor includes built-in
  support for a number of useful data operations, including:
  
  - Moving the selection up and down using the keyboard arrow keys.
  - Moving rows up and down using the keyboard arrow keys.
  - Inserting and deleting rows using the keyboard.
  - Begin editing table rows using the keyboard.
  - Drag and drop of table items to and from the editor, including support for
    both *copy* and *move* operations for single or multiple table items.
    
- **Visually appealing**. The editor, in general, uses the underlying OS's
  native table or grid control, and as a result often looks better than the 
  control used by the **TableEditor**.
  
- **Supports displaying text and images in any cell**. Note however that 
  the images displayed must all be the same size for optimal results.
  
Some of the weaknesses of the **TabularEditor** compared to the **TableEditor**
are:

- **Not as full-featured**. The **TableEditor** includes support for arbitrary
  data filters and searches and different types of data sorting. The differences
  here may narrow over time as new features get added to the **TabularEditor**.
  
- **Limited data editing capabilities**: The **TabularEditor** only supports 
  editing textual values, unlike the **TableEditor**, which supports a wide 
  variety of column editors and can be extended with more as needed. This is 
  due to limitations of the underlying native OS control used by the editor.
  
Setting up a **TabularEditor** for use in a Traits UI is divided into two main
parts:

- Configuring the **TabularEditor** object.
- Creating a suitable adapter (or adapters) for use with the editor.

We'll start off first with a description of the **TabularEditor** class, and
describe the adapter interface in a later section.

The TabularEditor Class
-----------------------

The **TabularEditor** class defines a large number of traits which are used to
configure the editor. We'll divide the set of traits into several categories,
and describe each in turn.

Visual Traits
-------------
    
show_titles
    A boolean value which specifies whether or not column headers should be
    displayed at the top of the table. It defaults to **True**.
    
horizontal_lines
    A boolean value which specifies whether or not horizontal lines should be 
    drawn between rows in the table. It defaults to **True**.
    
vertical_lines
    A boolean value which specifies whether or not vertical lines should be 
    drawn between columns in the table. It defaults to **True**.
    
Control Traits
--------------
    
editable
    A boolean value that specifies whether or not the user is allowed to edit
    data in the table. It defaults to **True**.
                 
multi_select
    A boolean value that specifies whether or not the user is allowed to select
    multiple rows in the table at once. It defaults to **False**.

operations
    A list of strings that specify what operations the user is allowed to
    perform on items in the table. The possible values are:
    
    - **delete**: The user can delete table rows.
    - **insert**: The user can insert new table rows at any position in the 
      table.
    - **append**: The user can append new table rows to the end of the table.
    - **edit**: The user can edit the contents of table rows.
    - **move**: The user can move table rows within the table.
    
    You should include in the list all operations that you want to allow the
    user to perform (e.g. *['delete','insert','append']*).
          
drag_move
    A boolean value that specifies whether *drag move* operations are allowed
    (**True**), or should all drag operations be treated as *drag copy*
    operations (**False**). The default is **False**.
           
adapter
    An instance of **TabularAdapter** that the editor uses to interface to the
    underlying **Item** data supplied to the editor. This is normally an
    instance of a subclass of **TabularAdapter** specially written for the type 
    of data being edited. This will be described more fully in the 
    **TabularAdapter** section.
    
adapter_name
    An optional string that specifies the extended trait name of a trait that
    contains the **TabularAdapter** the editor should used. If the value of the
    trait changes while the editor is active, the editor will automatically
    start using the new adapter. Normally you will use either the *adapter*
    trait *or* the *adapter_name* trait, but not both. However, it is possible 
    to use both together if needed.
                       
images
    An optional list of **ImageResource** objects describing a set of images 
    that can be displayed in the table's cells. Specifying a set here allows you
    to refer to the images by name within the adapter. However, it is also
    possible for the adapter to supply the **ImageResource** object directly
    for any image it wants to display.
 
Event Handling Traits
---------------------

selected
    An optional string that specifies the extended trait name of a trait that
    contains the currently selected table items. For a single-select mode
    editor, this should be a scalar trait, and for a multi-select mode editor,
    it should be a list trait. The type of the trait should be the same as the
    type of data being displayed in the table. This trait can be used to both
    set and get the current table selection.
    
selected_row
    An optional string that specifies the extended trait name of a trait that
    contains the currently selected table item indices. For a single-select mode
    editor this should be an **Int** value, and for a multi-select mode editor
    it should be a **List(Int)** value. This trait can be used to both set and
    get the current table selection.
 
activated    
    An optional string that specifies the extended trait name of a trait that
    contains the currently activated table item. It should be an instance of the
    table item data type. The trait can only be used to get the value of
    the most recently activated table item. An item is activated either by the
    user double-clicking on it or by pressing the **Enter** key when the item 
    is selected.
     
activated_row
    An optional string that specifies the extended trait name of a trait that
    contains the currently activated table item index. It should be an **Int** 
    value. The trait can only be used to get the index of the most recently 
    activated table item. An item is activated either by the user
    double-clicking on it or by pressing the **Enter** key when the item is
    selected.
    
clicked
    An optional string that specifies the extended trait name of a trait that
    contains a **TabularEditorEvent** object containing the information 
    associated with the most recent left mouse button click within the editor.
    The trait can only be used to get the **TabularEditorEvent** object. The
    **TabularEditorEvent** object is described in the next section.
    
dclicked
    An optional string that specifies the extended trait name of a trait that
    contains a **TabularEditorEvent** object containing the information 
    associated with the most recent left mouse button double-click within the 
    editor. The trait can only be used to get the **TabularEditorEvent** 
    object. The **TabularEditorEvent** object is described in the next section.
    
right_clicked
    An optional string that specifies the extended trait name of a trait that
    contains a **TabularEditorEvent** object containing the information 
    associated with the most recent right mouse button click within the editor.
    The trait can only be used to get the **TabularEditorEvent** object. The
    **TabularEditorEvent** object is described in the next section.
    
right_dclicked
    An optional string that specifies the extended trait name of a trait that
    contains a **TabularEditorEvent** object containing the information 
    associated with the most recent right mouse button double-click within the 
    editor. The trait can only be used to get the **TabularEditorEvent** 
    object. The **TabularEditorEvent** object is described in the next section.

The TabularEditorEvent Class
----------------------------

Objects of the **TabularEditorEvent** class contain information related to a 
mouse button click that occurs within the editor. The class has no methods, 
but does define the following traits:

row
    An integer specifying the index of the table item that was clicked on.
    
column
    A value specifying the column id of the table cell that was clicked on.
    This value will correspond to the second element of the tuple used to
    define the column in the **TabularEditor** adapter supplied to the editor. 
    This will be described in a later section.
    
item
    The data item corresponding to the table row that was clicked on. The type
    of this data will depend upon the type of data contained in the underlying
    data model.
    
The TabularEditor User Interface
--------------------------------

Depending upon how you have configured the **TabularEditor** and its associated
adapter, the following user interface features may be available:

- **Up arrow**: Move the selection up one line.
- **Down arrow**: Move the selection down one line.
- **Page down**: Append a new item to the end of the list (*'append'*).
- **Left arrow**: Move the current selection up one line (*'move'*).
- **Right arrow**: Move the current selection down one line (*'move'*).
- **Backspace, Delete**: Delete all items in the current selection from the 
  list (*'delete'*).
- **Enter, Escape**: Edit the current selection (*'edit'*).
- **Insert**: Insert a new item before the current selection (*'insert'*).

In the preceding list, the values in parentheses refer to the operation that
must be included in the **TabularEditor** *operations* trait in order for the 
specified key to have any effect.

The *append*, *move*, *edit* and *insert* operations are only available if a
single item is selected. The *delete* operation works when the selection has
one or more items.

Depending upon how the **TabularEditor** and adapter are specified, drag and
drop operations may also be available. If multiple items are selected and the
user drags one of the selected items, all selected items will be included in
the drag operation. If the user drags a non-selected item, only that item will
be dragged.

The editor also supports both *drag-move* and *drag-copy* semantics. A
*drag-move* operation means that the dragged items will be sent to the target
and removed from the list data. A *drag-copy* operation means that the
dragged items will be sent to the target, but will *not* be deleted from the
**Item** data. Note that in a *drag-copy* operation, if you do not want the
target to receive the same data contained in the list, then you must return a
copy or clone of the data when the editor requests the drag data from the
adapter.

You can prevent *drag-move* operations by making sure that the 
**TabularEditor** *drag_move* trait is set to **False** (the default).

Note that the default operation when a user begins a drag operation is
*drag_move*. A *drag-copy* operation occurs when the user also holds the
*Ctrl* key down during the drag operation (the mouse pointer changes to indicate
the change in drag semantics). If *drag_move* operations are disabled by
setting the **TabularEditor** *drag_move* trait to **False**, any *drag-move*
operation is automatically treated as a *drag_copy*.

The tabular editor only allows the user to edit the first column of data in the
table (a restriction imposed by the underlying OS widget). If the *'edit'* 
operation is enabled, the user can begin editing the first column either by 
clicking on the row twice, or by selecting the row and pressing the **Enter** or 
**Escape** key.

Finally, the user can resize columns in the table by dragging the column title
dividers left or right with the mouse. Once resized in this manner, the column
remains that size until the user resizes the column again. This is true
even if you assigned a dynamic width to the column (see the **TabularAdapter**
section for more information about what this means). If the user wants to allow
a previously user-sized column to be restored to its original developer
specified size again, they must right-click on the column title to *release* 
its user specified size and restore its original size. 

If you enable *persistence* for the editor by specifying a non-empty *id* trait
for the editor's **Item** and **View** objects, any user specified column 
widths will be saved across application sessions.

The TabularAdapter Class
------------------------

The power and flexibility of the tabular editor is mostly a result of the
**TabularAdapter** class, which is the base class from which all tabular editor
adapters must be derived.

The **TabularEditor** object interfaces between the underlying toolkit widget
and your program, while the **TabularAdapter** object associated with the
editor interfaces between the editor and your data.

The design of the **TabularAdapter** base class is such that it tries to make
simple cases simple and complex cases possible. How it accomplishes this is what
we'll be discussing in the following sections.

The TabularAdapter *columns* Trait
----------------------------------

First up is the **TabularAdapter** *columns* trait, which is a list of values
which define, in presentation order, the set of columns to be displayed by the
associated **TabularEditor**.

Each entry in the *columns* list can have one of two forms: 

- string 
- ( string, any )

where *string* is the user interface name of the column (which will appear in
the table column header) and *any* is any value that you want to use to 
identify that column to your adapter. Normally this value is either a trait name 
or an integer index value, but it can be any value you want. If only *string*
is specified, then *any* is the index of the *string* within *columns*.

For example, say you want to display a table containing a list of tuples, each
of which has three values: a name, an age, and a weight. You could then use
the following value for the *columns* trait::

    columns = [ 'Name', 'Age', 'Weight' ]
    
By default, the *any* values (also referred to in later sections as the 
*column ids*) for the columns will be the corresponding tuple index values.

Say instead that you have a list of **Person** objects, with *name*, *age* and
*weight* traits that you want to display in the table. Then you could use the
following *columns* value instead::

    columns = [ ( 'Name',   'name' ), 
                ( 'Age',    'age' ),
                ( 'Weight', 'weight' ) ]
                
In this case, the *column ids* are the names of the traits you want to display
in each column.

Note that it is possible to dynamically modify the contents of the *columns*
trait while the **TabularEditor** is active. The **TabularEditor** will 
automatically modify the table to show the new set of defined columns.

The Core TabularAdapter Interface
---------------------------------

In this section, we'll describe the core interface to the **TabularAdapter**
class. This is the actual interface used by the **TabularEditor** to access your
data and display attributes. In the most complex data representation cases, 
these are the methods that you must override in order to have the greatest
control over what the editor sees and does. 

However, the base **TabularAdapter** class provides default implementations for 
all of these methods. In subsequent sections, we'll look at how these default 
implementations provide simple means  of customizing the adapter to your needs.
But for now, let's start by covering the details of the core interface itself.

To reduce the amount of repetition, we'll use the following definitions in all 
of the method argument lists that follow in this section:

object
    The object whose trait is being edited by the **TabularEditor**.
    
trait
    The name of the trait the **TabularEditor** is editing.
    
row
    The row index (starting with 0) of a table item. 
    
column
    The column index (starting with 0) of a table column.

The adapter interface consists of a number of methods which can be divided into
two main categories: those which are sensitive to the type of a particular table
item, and those which are not. We'll begin with the methods that are
sensitive to an item's type:

get_alignment ( object, trait, column )
    Returns the alignment style to use for a specified column. 
    
    The possible values that can be returned are: *'left'*, *'center'* or
    *'right'*. All table items share the same alignment for a specified column.

get_width ( object, trait, column )
    Returns the width to use for a specified column. The result can either be a
    float or integer value. 
    
    If the value is <= 0, the column will have a *default* width, which is the 
    same as specifying a width of *0.1*. 
    
    If the value is > 1.0, it is converted to an integer and the result is
    the width of the column in pixels. This is referred to as a *fixed width*
    column.
    
    If the value is a float such that 0.0 < value <= 1.0, it is treated as the 
    *unnormalized fraction of the available space* that is to be assigned to the
    column. What this means requires a little explanation. 
    
    To arrive at the size in pixels of the column at any given time, the editor
    adds together all of the *unnormalized fraction* values returned for all
    columns in the table to arrive at a total value. Each 
    *unnormalized fraction* is then divided by the total to create a 
    *normalized fraction*. Each column is then assigned an amount of space in 
    pixels equal to the maximum of 30 or its *normalized fraction* multiplied 
    by the *available space*. The *available space* is defined as the actual 
    width of the table minus the width of all *fixed width* columns. Note that 
    this calculation is performed each time the table is resized in the user 
    interface, thus allowing columns of this type to increase or decrease their
    width dynamically, while leaving *fixed width* columns unchanged.
        
get_can_edit ( object, trait, row )
    Returns a boolean value indicating whether the user can edit a specified 
    *object.trait[row]* item. 
    
    A **True** result indicates that the value can be edited, while a **False**
    result indicates that it cannot.
    
get_drag ( object, trait, row )
    Returns the value to be *dragged* for a specified *object.trait[row]* item. 
    A result of **None** means that the item cannot be dragged. Note that the
    value returned does not have to be the actual row item. It can be any
    value that you want to drag in its place. In particular, if you want the
    drag target to receive a copy of the row item, you should return a copy or
    clone of the item in its place.
    
    Also note that if multiple items are being dragged, and this method returns
    **None** for any item in the set, no drag operation is performed.
        
get_can_drop ( object, trait, row, value )
    Returns whether the specified *value* can be dropped on the specified 
    *object.trait[row]* item. A value of **True** means the *value* can be 
    dropped; and a value of **False** indicates that it cannot be dropped.
    
    The result is used to provide the user positive or negative drag feedback 
    while dragging items over the table. *Value* will always be a single value,
    even if multiple items are being dragged. The editor handles multiple drag
    items by making a separate call to *get_can_drop* for each item being
    dragged.
        
get_dropped ( object, trait, row, value )
    Returns how to handle a specified *value* being dropped on a specified 
    *object.trait[row]* item. The possible return values are:
                
    - **'before'**: Insert the specified *value* before the dropped on item.
    - **'after'**: Insert the specified *value* after the dropped on item.
    
    Note there is no result indicating *do not drop* since you will have already
    indicated that the *object* can be dropped by the result returned from a 
    previous call to *get_can_drop*.
        
get_font ( object, trait, row )
    Returns the font to use for displaying a specified *object.trait[row]* item.
    
    A result of **None** means use the default font; otherwise a **wx.Font**
    object should be returned. Note that all columns for the specified table row
    will use the font value returned.
        
get_text_color ( object, trait, row )
    Returns the text color to use for a specified *object.trait[row]* item. 
    
    A result of **None** means use the default text color; otherwise a 
    **wx.Colour** object should be returned. Note that all columns for the 
    specified table row will use the text color value returned. 
     
get_bg_color ( object, trait, row )
    Returns the background color to use for a specified *object.trait[row]*
    item. 
    
    A result of **None** means use the default background color; otherwise a
    **wx.Colour** object should be returned. Note that all columns for the 
    specified table row will use the background color value returned.
        
get_image ( object, trait, row, column )
    Returns the image to display for a specified *object.trait[row].column* 
    item. 
    
    A result of **None** means no image will be displayed in the specified table
    cell. Otherwise the result should either be the name of the image, or an 
    **ImageResource** object specifying the image to display. 
    
    A name is allowed in the case where the image is specified in the 
    **TabularEditor** *images* trait. In that case, the name should be the same 
    as the string specified in the **ImageResource** constructor.
     
get_format ( object, trait, row, column )
    Returns the Python formatting string to apply to the specified 
    *object.trait[row].column* item in order to display it in the table.
    
    The result can be any Python string containing exactly one Python formatting
    sequence, such as *'%.4f'* or *'(%5.2f)'*.
     
get_text ( object, trait, row, column )
    Returns a string containing the text to display for a specified 
    *object.trait[row].column* item.
    
    If the underlying data representation for a specified item is not a string,
    then it is your responsibility to convert it to one before returning it as
    the result.
     
set_text ( object, trait, row, text ):
    Sets the value for the specified *object.trait[row].column* item to the 
    string specified by *text*. 
    
    If the underlying data does not store the value as text, it is your 
    responsibility to convert *text* to the correct representation used. This 
    method is called when the user completes an editing operation on a table 
    cell.
        
get_tooltip ( object, trait, row, column )
    Returns a string containing the tooltip to display for a specified 
    *object.trait[row].column* item. 
    
    You should return the empty string if you do not wish to display a tooltip.
 
The following are the remaining adapter methods, which are not sensitive to the
type of item or column data:
    
get_item ( object, trait, row )
    Returns the specified *object.trait[row]* item.
    
    The value returned should be the value that exists (or *logically* exists)
    at the specified *row* in your data. If your data is not really a list or
    array, then you can just use *row* as an integer *key* or *token* that
    can be used to retrieve a corresponding item. The value of *row* will 
    always be in the range: 0 <= row < *len( object, trait )* (i.e. the result
    returned by the adapter *len* method).
    
len ( object, trait )
    Returns the number of row items in the specified *object.trait* list.
    
    The result should be an integer greater than or equal to 0.
        
delete ( object, trait, row )
    Deletes the specified *object.trait[row]* item. 
    
    This method is only called if the *delete* operation is specified in the 
    **TabularEditor** *operation* trait, and the user requests that the item be
    deleted from the table. The adapter can still choose not to delete the 
    specified item if desired, although that may prove confusing to the user.
        
insert ( object, trait, row, value )
    Inserts *value* at the specified *object.trait[row]* index. The specified
    *value* can be:
    
    - An item being moved from one location in the data to another.
    - A new item created by a previous call to *get_default_value*.
    - An item the adapter previously approved via a call to *get_can_drop*.
    
    The adapter can still choose not to insert the item into the data, although
    that may prove confusing to the user.
    
get_default_value ( object, trait )
    Returns a new default value for the specified *object.trait* list. 
    
    This method is called when *insert* or *append* operations are allowed and
    the user requests that a new item be added to the table. The result should
    be a new instance of whatever underlying representation is being used for
    table items.

Creating a Custom TabularAdapter
--------------------------------

Having just taken a look at the core **TabularAdapter** interface, you might now
be thinking that there are an awful lot of methods that need to be specified to 
get an adapter up and running. But as we mentioned earlier, **TabularAdapter**
is not an abstract base class. It is a concrete base class with implementations
for each of the methods in its interface. And the implementations are written
in such a way that you will hopefully hardly ever need to override them.

In this section, we'll explain the general implementation style used by these
methods, and how you can take advantage of them in creating your own adapters.

One of the things you probably noticed as you read through the core adapter
interface section is that most of the methods have names of the form:
*get_xxx* or *set_xxx*, which is similar to the familiar *getter/setter* pattern
used when defining trait properties. The adapter interface is purposely defined 
this way so that it can expose and leverage a simple set of design rules.

The design rules are followed consistently in the implementations of all of the
adapter methods described in the first section of the core adapter interface, so
that once you understand how they work, you can easily apply the design pattern
to all items in that section. Then, only in the case where the design rules will
not work for your application will you ever have to override any of those 
**TabularAdapter** base class method implementations.

So the first thing to understand is that if an adapter method name has the form:
*get_xxx* or *set_xxx* it really is dealing with some kind of trait called 
*xxx*, or which contains *xxx* in its name. For example, the *get_alignment* 
method retrieves the value of some *alignment* trait defined on the adapter.
In the following discussion we'll simply refer to an attribute name generically 
as *attribute*, but you will need to replace it by an actual attribute name 
(e.g. *alignment*) in your adapter.

The next thing to keep in mind is that the adapter interface is designed to
easily deal with items that are not all of the same type. As we just said, the
design rules apply to all adapter methods in the first group, which were
defined as methods which are sensitive to an item's type. Item type sensitivity 
plays an important part in the design rules, as we will see shortly.

With this in mind, we now describe the simple design rules used by the first
group of methods in the **TabularAdapter** class:

- When getting or setting an adapter attribute, the method first retrieves the 
  underlying item for the specified data row. The item, and type (i.e. class) of
  the item, are then used in the next rule.
  
- The method gets or sets the first trait it finds on the adapter that matches 
  one of the following names:
  
  - *classname_columnid_attribute*
  - *classsname_attribute*
  - *columnid_attribute*
  - *attribute*

  where:
  
  - *classname* is the name of the class of the item found in the first step, or
    one of its base class names, searched in the order defined by the *mro*
    (**method resolution order**) for the item's class.
  - *columnid* is the column id specified by the developer in the adapter's
    *column* trait for the specified table column.
  - *attribute* is the attribute name as described previously (e.g. 
    *alignment*).
    
Note that this last rule always finds a matching trait, since the 
**TabularAdapter** base class provides traits that match the simple *attribute*
form for all attributes these rules apply to. Some of these are simple traits, 
while others are properties. We'll describe the behavior of all these *default*
traits shortly.
    
The basic idea is that rather than override the first group of core adapter 
methods, you simply define one or more simple traits or trait properties on your
**TabularAdapter** subclass that provide or accept the specified information. 

All of the adapter methods in the first group provide a number of arguments,
such as *object*, *trait*, *row* and *column*. In order to define a trait 
property, which cannot be passed this information directly, the adapter always 
stores the arguments and values it computes in the following adapter traits, 
where they can be easily accessed by a trait getter or setter method:

- *row*: The table row being accessed.
- *column*: The column id of the table column being accessed (not its index).
- *item*: The data item for the specified table row (i.e. the item determined
  in the first step described above).
- *value*: In the case of a *set_xxx* method, the value to be set; otherwise it
  is **None**.

As mentioned previously, the **TabularAdapter** class provides trait definitions 
for all of the attributes these rules apply to. You can either use the
default values as they are, override the default, set a new value, or completely 
replace the trait definition in a subclass. A description of the default trait
implementation for each attribute is as follows:

default_value = Any( '' )
    The default value for a new row. 
    
    The default value is the empty string, but you will normally need to assign 
    a different (default) value.
   
format = Str( '%s' )
    The default Python formatting string for a column item.
    
    The default value is *'%s'* which will simply convert the column item to a
    displayable string value.
    
text = Property
    The text to display for the column item.
    
    The implementation of the property checks the type of the column's
    *column id*:
    
    - If it is an integer, it returns *format%item[column_id]*.
    - Otherwise, it returns *format%item.column_id*.
    
    Note that *format* refers to the value returned by a call to *get_format*
    for the current column item.
    
text_color = Property
    The text color for a row item. 
    
    The property implementation checks to see if the current table row is even
    or odd, and based on the result returns the value of the *even_text_color* 
    or *odd_text_color* trait if the value is not **None**, and the value of the
    *default_text_color* trait if it is. The definition of these additional 
    traits are as follows:
    
    - odd_text_color = Color( None )
    - even_text_color = Color( None )
    - default_text_color = Color( None )
    
    Remember that a **None** value means use the default text color.
    
bg_color = Property
    The background color for a row item. 
    
    The property implementation checks to see if the current table row is even
    or odd, and based on the result returns the value of the *even_bg_color* or
    *odd_bg_color* trait if the value is not **None**, and the value of the 
    *default_bg_color* trait if it is. The definition of these additional 
    traits are as follows:
    
    - odd_bg_color = Color( None )
    - even_bg_color = Color( None )
    - default_bg_color = Color( None )
    
    Remember that a **None** value means use the default background color.
    
alignment = Enum( 'left', 'center', 'right' )
    The alignment to use for a specified column.
    
    The default value is *'left'*.
    
width = Float( -1 )
    The width of a specified column.
    
    The default value is *-1*, which means a dynamically sized column with an
    *unnormalized fractional* value of *0.1*.
    
can_edit = Bool( True )
    Specifies whether the text value of the current item can be edited.
    
    The default value is **True**, which means that the user can edit the value.
    
drag = Property
    A property which returns the value to be dragged for a specified row item.
    
    The property implementation simply returns the current row item.
    
can_drop = Bool( False )
    Specifies whether the specified value be dropped on the current item.
    
    The default value is **False**, meaning that the value cannot be dropped.
    
dropped = Enum( 'after', 'before' )
    Specifies where a dropped item should be placed in the table relative to
    the item it is dropped on.
    
    The default value is *'after'*.
    
font = Font
    The font to use for the current item.
    
    The default value is the standard default Traits font value.
    
image = Str( None )
    The name of the default image to use for a column.
    
    The default value is **None**, which means that no image will be displayed
    for the column.
    
    # The text of a row/column item:
    text = Property
    
tooltip = Str
    The tooltip information for a column item.
    
    The default value is the empty string, which means no tooltip information
    will be displayed for the column.

The preceding discussion applies to all of the methods defined in the first 
group of **TabularAdapter** interface methods. However, the design rules do not 
apply to the remaining five adapter methods, although they all provide a useful
default implementation:
    
get_item ( object, trait, row )
    Returns the value of the *object.trait[row]* item.
    
    The default implementation assumes the trait defined by *object.trait* is a
    *sequence* and attempts to return the value at index *row*. If an error
    occurs, it returns **None** instead. This definition should work correctly
    for lists, tuples and arrays, or any other object that is indexable, but
    will have to be overridden for all other cases. 
    
    Note that this method is the one called in the first design rule described
    previously to retrieve the item at the current table row.
    
len ( object, trait )
    Returns the number of items in the specified *object.trait* list.
    
    Again, the default implementation assumes the trait defined by 
    *object.trait* is a *sequence* and attempts to return the result of calling
    *len( object.trait )*. It will need to be overridden for any type of data
    which for which *len* will not work.
        
delete ( object, trait, row )
    Deletes the specified *object.trait[row]* item.
    
    The default implementation assumes the trait defined by *object.trait* is a
    mutable sequence and attempts to perform a *del object.trait[row]*
    operation.
        
insert ( object, trait, row, value )
    Inserts a new value at the specified *object.trait[row]* index.
    
    The default implementation assumes the trait defined by *object.trait* is a
    mutable sequence and attempts to perform an *object.trait[row:row]=[value]*
    operation.
    
get_default_value ( object, trait )
    Returns a new default value for the specified *object.trait* list.
    
    The default implementation simply returns the value of the adapter's
    *default_value* trait.
    
A TabularAdapter Example
------------------------

Having now learned about the core adapter interface as well as the design rules
supported by the default method implementations, you're probably wondering how
you can use a **TabularAdapter** for creating a real user interface.

So in this section we'll cover a simple example of creating a **TabularAdapter**
subclass to try and show how all of the pieces fit together.

In subsequent tutorials, we'll provide complete examples of creating
user interfaces using both the **TabularEditor** and **TabularAdapter** in 
combination.

For this example, let's assume we have the following two classes::

    class Person ( HasTraits ):
    
        name    = Str
        age     = Int
        address = Str
        
    class MarriedPerson ( Person ):
    
        partner = Instance( Person )
    
where **Person** represents a single person, and **MarriedPerson** represents
a married person and is derived from **Person** but adds the *partner* trait to
reference the person they are married to.

Now, assume we also have the following additional class::

    class Report ( HasTraits ):
    
        people = List( Person )
    
which has a *people* trait which contains a list of both **Person** and
**MarriedPerson** objects, and we want to create a tabular display showing the
following information:

- Name of the person
- Age of the person
- The person's address
- The name of the person's spouse (if any)

In addition:

- We want to use a Courier 10 point font for each line in the table.
- We want the age column to be right, instead of left, justified
- If the person is a minor (age < 18) and married, we want to show a red flag
  image in the age column.
- If the person is married, we want to make the background color for that row
  a light blue.

Given this set of requirements, we can now define the following
**TabularAdapter** subclass::

    class ReportAdapter ( TabularAdapter ):
    
        columns = [ ( 'Name',    'name' ), 
                    ( 'Age',     'age' ), 
                    ( 'Address', 'address' )
                    ( 'Spouse',  'spouse' ) ]
                    
        font                      = 'Courier 10'
        age_alignment             = Constant( 'right' )
        MarriedPerson_age_image   = Property
        MarriedPerson_bg_color    = Color( 0xE0E0FF )
        MarriedPerson_spouse_text = Property
        Person_spouse_text        = Constant( '' )
        
        def _get_MarriedPerson_age_image ( self ):
            if self.item.age < 18:
                return 'red_flag'
            return None
            
        def _get_MarriedPerson_spouse_text ( self ):
            return self.item.partner.name
        
Hopefully, this simple example conveys some of the power and flexibility that 
the **TabularAdapter** class provides you. But, just in case it doesn't, let's 
go over some of the more interesting details:

- Note the values in the *columns* trait. The first three values define 
  *column ids* which map directly to traits defined on our data objects, while
  the last one defines an arbitrary string which we define so that we can
  reference it in the *MarriedPerson_spouse_text* and *Person_spouse_text* trait
  definitions.
  
- Since the font we want to use applies to all table rows, we just specify a
  new default value for the existing **TabularAdapter** *font* trait.
  
- Since we only want to override the default left alignment for the age column,
  we simply define an *age_alignment* trait as a constant *'right'* value. We
  could have also used *age_alignment = Str('right')*, but *Constant* never
  requires storage to be used in an object.
  
- We define the *MarriedPerson_age_image* property to handle putting the
  *red flag* image in the age column. By including the class name of the items
  it applies to, we only need to check the *age* value in determining what
  value to return.
  
- Similary, we use the *MarriedPerson_bg_color* trait to ensure that each
  **MarriedPerson** object has the correct background color in the table.
  
- Finally, we use the *MarriedPerson_spouse_text* and *Person_spouse_text*
  traits, one a property and the other a simple constant value, to determine 
  what text to display in the *Spouse* column for the different object types. 
  Note that even though a **MarriedPerson** is both a **Person** and a
  **MarriedPerson**, it will correctly use the *MarriedPerson_spouse_text* trait
  since the search for a matching trait is always made in *mro* order.
  
Although this is completely subjective, some of the things that the author
feels stand out about this approach are:

- The class definition is short and sweet. Less code is good.
- The bulk of the code is declarative. Less room for logic errors.
- There is only one bit of logic in the class (the *if* statement in the
  *MarriedPerson_age_image* property implementation). Again, less logic usually
  translates into more reliable code).
- The defined traits and even the property implementation method names read 
  very descriptively. *_get_MarriedPerson_age_image* pretty much says what you 
  would write in a comment or doc string. The implementation almost is the
  documentation.

Look for a complete traits UI example based on this sample problem definition in 
the *Single and Married Person Example* tutorial in this section.
  
Now, as the complexity of a tabular view increases, the definition of the
**TabularAdapter** class could possibly start to get large and unwieldy. At
this point we could begin refactoring our design to use the **ITabularAdapter**
interface and **AnITabularAdapter** implementation class to create 
*sub-adapters* that can be added to our **TabularAdapter** subclass to extend
its functionality even further. Creating sub-adapters and adding them via the 
**TabularAdapter** *adapters* trait is a topic covered in a follow-on tutorial.

