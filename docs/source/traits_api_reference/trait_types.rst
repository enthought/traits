:mod:`trait_types` Module
=========================

.. automodule:: traits.trait_types
    :no-members:

Traits
------

.. autoclass:: Any

.. autoclass:: Generic

.. autoclass:: BaseInt

.. autoclass:: Int

.. autoclass:: BaseFloat

.. autoclass:: Float

.. autoclass:: BaseComplex

.. autoclass:: Complex

.. autoclass:: BaseStr

.. autoclass:: Str

.. autoclass:: Title

.. autoclass:: BaseUnicode

.. autoclass:: Unicode

.. autoclass:: BaseBytes

.. autoclass:: Bytes

.. autoclass:: BaseBool

.. autoclass:: Bool

.. autoclass:: BaseCInt

.. autoclass:: CInt

.. autoclass:: BaseCFloat

.. autoclass:: CFloat

.. autoclass:: BaseCComplex

.. autoclass:: CComplex

.. autoclass:: BaseCStr

.. autoclass:: CStr

.. autoclass:: BaseCUnicode

.. autoclass:: CUnicode

.. autoclass:: BaseCBytes

.. autoclass:: CBytes

.. autoclass:: BaseCBool

.. autoclass:: CBool

.. autoclass:: String

.. autoclass:: Regex

.. autoclass:: Code

.. autoclass:: HTML

.. autoclass:: Password

.. autoclass:: Callable

.. autoclass:: BaseType

.. autoclass:: This

.. autoclass:: self

.. autoclass:: Function

.. autoclass:: Method

.. autoclass:: Module

.. autoclass:: Python

.. autoclass:: ReadOnly

.. autoclass:: Disallow

.. autoclass:: Constant

.. autoclass:: Delegate

.. autoclass:: DelegatesTo

.. autoclass:: PrototypedFrom

.. autoclass:: Expression

.. autoclass:: PythonValue

.. autoclass:: BaseFile

.. autoclass:: File

.. autoclass:: BaseDirectory

.. autoclass:: Directory

.. autoclass:: BaseRange

.. autoclass:: Range

.. autoclass:: BaseEnum

.. autoclass:: Enum

.. autoclass:: BaseTuple
   :special-members: __init__

.. autoclass:: Tuple

.. autoclass:: ValidatedTuple
   :special-members: __init__

.. autoclass:: List

.. autoclass:: CList

.. autoclass:: Set

.. autoclass:: CSet

.. autoclass:: Dict

.. autoclass:: BaseClass

.. autoclass:: BaseInstance

.. autoclass:: Instance

.. autoclass:: Supports

.. autoclass:: AdaptsTo

.. autoclass:: Type

.. autoclass:: Event

.. autoclass:: Button

.. autoclass:: ToolbarButton

.. autoclass:: Either

.. autoclass:: Symbol

.. autoclass:: UUID

.. autoclass:: WeakRef
    :members: __init__

.. autodata:: Date

.. autodata:: Time

Deprecated Traits
-----------------

The following :class:`~.TraitType` instances are deprecated, and may
be removed in a future version of Traits. In user code, these should be
replaced with the corresponding compound types (e.g., replace ``ListStr``
with ``List(Str)`` and ``DictStrAny`` with ``Dict(Str, Any)``).

.. deprecated:: 6.0.0

.. autodata:: false

.. autodata:: true

.. autodata:: undefined

.. autodata:: ListInt

.. autodata:: ListFloat

.. autodata:: ListStr

.. autodata:: ListUnicode

.. autodata:: ListComplex

.. autodata:: ListBool

.. autodata:: ListFunction

.. autodata:: ListMethod

.. autodata:: ListThis

.. autodata:: DictStrAny

.. autodata:: DictStrStr

.. autodata:: DictStrInt

.. autodata:: DictStrFloat

.. autodata:: DictStrBool

.. autodata:: DictStrList


Private Classes
---------------

.. autoclass:: HandleWeakRef

Functions
---------

.. autofunction:: default_text_editor
