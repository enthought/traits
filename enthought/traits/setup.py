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
def configuration(parent_package='enthought',top_path=None):
    import numpy
    if numpy.__version__ < minimum_numpy_version:
        raise RuntimeError, 'numpy version %s or higher required, but got %s'\
              % (minimum_numpy_version, numpy.__version__)

    from numpy.distutils.misc_util import Configuration
    config = Configuration('traits',parent_package,top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_extension('ctraits',['ctraits.c'])

    # for unknown reasons, if ../__init__.py isn't referred to by its absolute
    # path, enthought/traits/__init__.py gets copied instead
    config.add_data_files(('..', os.path.abspath(os.path.join('..','__init__.py'))))
    
    config.add_data_dir('demo')
    
    config.add_data_dir('doc/examples')
    config.add_data_files('doc/Traits2_UM.pdf')
    
    config.add_data_dir('examples')
    config.add_data_dir('images')
    config.add_data_dir('plugins')
    config.add_data_dir('tests')
    
    config.add_subpackage('ui')
    config.add_subpackage('protocols')

    config.add_subpackage('vet')
    config.add_data_dir('vet/examples')
    config.add_data_dir('vet/images')

    config.add_data_files('*.txt')
    
    return config

if __name__ == "__main__":
    try:
        from numpy.distutils.core import setup
        setup(version          = '2.1.0',
              description      = 'Explicitly typed Python attributes package',
              author           = 'David C. Morrill',
              author_email     = 'dmorrill@enthought.com',
              url              = 'http://code.enthought.com/traits',
              license          = 'BSD',
              install_requires = ['numpy', 'enthought.ets', 'enthought.resource', 'enthought.pyface'],
              extras_require   = {'wx' : ['enthought.traits.ui.wx'] },
              zip_safe         = False,
              configuration    = configuration)
    except ImportError:
        # Fall back to scipy_distutils based setup script if numpy not present:
        execfile( 'setup_traits.py' )
