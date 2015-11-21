#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Rewritten Core Traits)-----------------------------------------------------
"""
Rewritten Core Traits
=====================

For several reasons, including the ability to subclass types, many of the
previous core Traits package types have been entirely rewritten as subclasses
of **TraitType**, the new base class for subclassable trait types.

The core trait types which have been rewritten as subclasses of **TraitType**
are:

- Any
- Bool
- CBool
- CComplex
- CInt
- CFloat
- CLong
- Code
- Complex
- CStr
- CUnicode
- Dict
- Directory
- Enum
- Expression
- File
- Float
- HTML
- Instance
- Int
- List
- Long
- Password
- PythonValue
- Range
- Regex
- Str
- String
- Tuple
- Unicode
- WeakRef

This may be useful information if you find yourself in need of creating a new
trait type with behavior similar to any of these core trait types.
"""
