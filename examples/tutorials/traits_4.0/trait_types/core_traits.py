# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# --(Rewritten Core Traits)----------------------------------------------------
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
- Code
- Complex
- CStr
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
- Password
- PythonValue
- Range
- Regex
- Str
- String
- Tuple
- WeakRef

This may be useful information if you find yourself in need of creating a new
trait type with behavior similar to any of these core trait types.
"""
