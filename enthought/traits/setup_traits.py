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
# Date: 12/20/2002
# Description: Python setup for the 'traits' package
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path import join
from glob import glob
from scipy_distutils.misc_util import default_config_dict, get_path, dot_join
from scipy_distutils.core import Extension

#-------------------------------------------------------------------------------
#  Define the configuration information:
#-------------------------------------------------------------------------------

def configuration ( parent_package = '', parent_path=None ):
    package = 'traits'
    config = default_config_dict(package, parent_package)

    local_path = get_path(__name__, parent_path)
    install_path = join(*config['name'].split('.'))

    config['data_files'].append((join(install_path,'images'),
                                 glob(join(local_path,'images','*.gif'))))

    ext = Extension(dot_join(parent_package,package,'ctraits'), 
                    sources=[join(local_path,'ctraits.c')])
    config['ext_modules'].append(ext)

    package_cur = dot_join( parent_package, package, 'ui' )
    config[ 'packages' ].append( package_cur )
    config[ 'package_dir' ][package_cur] = join( local_path, 'ui' )

    package_cur = dot_join( parent_package, package, 'ui', 'wx' )
    config[ 'packages' ].append( package_cur )
    config[ 'package_dir' ][package_cur] = join( local_path, 'ui', 'wx' )
    
    return config

#-------------------------------------------------------------------------------
#  Do the setup if we are run stand-alone:
#-------------------------------------------------------------------------------
    
if __name__ == '__main__':
    from scipy_distutils.core import setup
    setup( version      = '1.0.2',
           description  = 'Explicitly typed Python attributes package',
           author       = 'David C. Morrill',
           author_email = 'dmorrill@enthought.com',
           url          = 'http://www.scipy.org/site_content/traits',
           license      = 'BSD',
           **configuration( parent_path='' )
           )
