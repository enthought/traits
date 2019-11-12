# ------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   11/06/2004
#
# ------------------------------------------------------------------------------

""" Adds a "category" capability to Traits-based classes, similar to that
    provided by the Cocoa (Objective-C) environment for the Macintosh.

    You can use categories to extend an existing HasTraits class, as an
    alternative to subclassing. An advantage of categories over subclassing is
    that you can access the added members on instances of the original class,
    without having to change them to instances of a subclass. Unlike
    subclassing, categories do not allow overriding trait attributes.
"""

# -------------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------------

from __future__ import absolute_import

import warnings

import six

from .has_traits import (
    MetaHasTraits,
    update_traits_class_dict,
    BaseTraits,
    ClassTraits,
    InstanceTraits,
    PrefixTraits,
    ListenerTraits,
    ViewTraits,
)

# -------------------------------------------------------------------------------
#  'MetaCategory' class:
# -------------------------------------------------------------------------------


class MetaCategory(MetaHasTraits):
    """
    Metaclass providing magic for the category extension mechanism.

    .. deprecated:: 5.2
       The category extension mechanism is deprecated, and the Category
       and MetaCategory classes will be removed in a future version of Traits.

    """
    def __new__(cls, class_name, bases, class_dict):

        # Make sure the correct usage is being applied:
        if len(bases) > 2:
            raise TypeError(
                "Correct usage is: class FooCategory(Category,Foo):"
            )

        # Categories are deprecated. Only warn if len(bases) == 2 to avoid
        # a spurious warning when creating the Category class itself.
        if len(bases) == 2:
            # See enthought/traits#319 for deprecation rationale.
            warnings.warn(
                (
                    "Use of the Category class is deprecated. Category "
                    "will be removed in a future version of Traits."
                ),
                DeprecationWarning,
                stacklevel=2,
            )

        # Process any traits-related information in the class dictionary:
        update_traits_class_dict(
            class_name, bases, class_dict, is_category=True
        )

        if len(bases) == 2:
            category_class = bases[1]

            # Update the class and each of the existing subclasses:
            category_class._add_trait_category(
                class_dict.pop(BaseTraits),
                class_dict.pop(ClassTraits),
                class_dict.pop(InstanceTraits),
                class_dict.pop(PrefixTraits),
                class_dict.pop(ListenerTraits),
                class_dict.pop(ViewTraits),
            )

            # Move all remaining items in our class dictionary to the base
            # class's dictionary:
            for name, value in list(class_dict.items()):
                if not hasattr(category_class, name):
                    setattr(category_class, name, value)
                    del class_dict[name]

        # Finish building the class using the updated class dictionary:
        return type.__new__(cls, class_name, bases, class_dict)


# -------------------------------------------------------------------------------
#  'Category' class:
# -------------------------------------------------------------------------------


@six.add_metaclass(MetaCategory)
class Category(object):
    """ Used for defining "category" extensions to existing classes.

    .. deprecated:: 5.2
       The category extension mechanism is deprecated, and the Category
       and MetaCategory classes will be removed in a future version of Traits.

    To define a class as a category, specify "Category," followed by the name
    of the base class name in the base class list.

    The following example demonstrates defining a category::

        from traits.api import HasTraits, Str, Category

        class Base(HasTraits):
            x = Str("Base x")
            y = Str("Base y")

        class BaseExtra(Category, Base):
            z = Str("BaseExtra z")
    """
