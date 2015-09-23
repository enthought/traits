#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# keywords.py --- Example of trait keywords

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Str


#--[Code]----------------------------------------------------------------------
class Person(HasTraits):
    # 'label' is used for Traits UI field labels;
    # 'desc' can be used for tooltips.
    first_name = Str('',
                     desc='first or personal name',
                     label='First Name')
    last_name = Str('',
                    desc='last or family name',
                    label='Last Name')
