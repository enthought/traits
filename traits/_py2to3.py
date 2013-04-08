""" Helper module, providing a common API for tasks that require a different implementation in python 2 and 3.
"""

from __future__ import division, absolute_import

import sys


if sys.version_info.major < 3:
    import string
    str_find = string.find
    str_rfind = string.rfind
else:
    str_find = str.find
    str_rfind = str.rfind

if sys.version_info.major < 3:
    from types import InstanceType,ClassType
    def is_old_style_instance(obj):
        return type(obj) is InstanceType
    def is_old_style_class(obj):
        return type(obj) is ClassType
    def is_InstanceType(obj):
        return obj is InstanceType
    def is_ClassType(obj):
        return obj is ClassType
else:
    def is_old_style_instance(obj):
        return False
    def is_old_style_instance(obj):
        return False
    def is_InstanceType(obj):
        return False
    def is_ClassType(obj):
        return False


if sys.version_info.major < 3:
    from types import InstanceType
    def type_w_old_style(obj):
        the_type = type(obj)
        if the_type is InstanceType:
            # Old-style class.
            the_type = obj.__class__
        return the_type
else:
    type_w_old_style = type

if sys.version_info.major < 3:
    from types import ClassType
    ClassTypes    = ( ClassType, type )
else:
    ClassTypes    = ( type, )


