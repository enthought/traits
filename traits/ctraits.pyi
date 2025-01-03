# (C) Copyright 2020-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from typing import Any

# Constants used in DefaultValue enumeration.
_CALLABLE_AND_ARGS_DEFAULT_VALUE: int
_CALLABLE_DEFAULT_VALUE: int
_CONSTANT_DEFAULT_VALUE: int
_DICT_COPY_DEFAULT_VALUE: int
_DISALLOW_DEFAULT_VALUE: int
_LIST_COPY_DEFAULT_VALUE: int
_MAXIMUM_DEFAULT_VALUE_TYPE: int
_MISSING_DEFAULT_VALUE: int
_OBJECT_DEFAULT_VALUE: int
_TRAIT_DICT_OBJECT_DEFAULT_VALUE: int
_TRAIT_LIST_OBJECT_DEFAULT_VALUE: int
_TRAIT_SET_OBJECT_DEFAULT_VALUE: int

def _validate_complex_number(value: Any) -> complex: ...
def _validate_float(value: Any) -> float: ...

class CHasTraits:
    def __init__(self, **traits: Any): ...

class cTrait: ...
