#!/usr/bin/env python
#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: David C. Morrill
# Date: 2/03/2003
# Description: Python setup for the 'traits' package
#------------------------------------------------------------------------------

import os

minimum_numpy_version = '0.9.7.2467'
def configuration(parent_package='enthought.traits',top_path=None):
    import numpy
    if numpy.__version__ < minimum_numpy_version:
        raise RuntimeError, 'numpy version %s or higher required, but got %s'\
              % (minimum_numpy_version, numpy.__version__)

    from numpy.distutils.misc_util import Configuration
    config = Configuration('ui',parent_package,top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=False,
                       quiet=True)

    #add the parent __init__.py to allow for importing
    config.add_data_files(('..', os.path.abspath(os.path.join('..','__init__.py'))))
    config.add_data_files(( os.path.join('..', '..'), os.path.abspath(os.path.join('..','..','__init__.py'))))

    config.add_data_dir('demos')
    config.add_data_dir('extras')
    config.add_data_dir('images')
    config.add_data_dir('null')
    config.add_data_dir('tests')
    
    config.add_subpackage('demos')
    config.add_subpackage('extras')
    config.add_subpackage('null')
    return config

if __name__ == "__main__":
    try:
        from numpy.distutils.core import setup
        setup(version='1.1.0',
              description  = 'UI subpackage of enthought.traits',
              author       = 'David C. Morrill',
              author_email = 'dmorrill@enthought.com',
              url          = 'http://code.enthought.com/traits',
              license      = 'BSD',
              zip_safe     = False,
              configuration=configuration)
    except ImportError:
        # fall back to scipy_distutils based setup script if numpy not present
        execfile('setup_traits.py')
