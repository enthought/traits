#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
Core packages for the Enthought Tool Suite.

The EnthoughtBase project includes a few core packages that are used by many
other projects in the Enthought Tool Suite:

- **enthought.etsconfig**: Supports configuring settings that need to be shared
  across multiple projects or programs on the same system. Most significant of
  these is the GUI toolkit to be used. You can also configure locations for
  writing application data and user data, and the name of the company 
  responsible for the software (which is used in the application and user data
  paths on some systems).
- **enthought.logger**: Provides convenience functions for creating logging
  handlers.
- ****enthought.util: Provides miscellaneous utility functions.
"""
import os, zipfile

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from distutils.command.build import build as distbuild
from distutils import log
from pkg_resources import DistributionNotFound, parse_version, require, VersionConflict 

from setup_data import INFO
from make_docs import HtmlBuild


# NOTE: EnthoughtBase should *never* depend on another ETS project!  We need
# to fix the below ASAP!

# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies.
ENVISAGECORE = etsdep('EnvisageCore', '3.0.0b1')  # -- all from logger.(plugin|agent|widget)
ENVISAGEPLUGINS = etsdep('EnvisagePlugins', '3.0.0b1')  # -- all from logger.plugin
TRAITS = etsdep('Traits', '3.0.0b1')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.0.0b1')  # -- only from e.util.traits.editor.parameter_choice_editor.py
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')  # -- from logger.(agent|plugin|widget)
TRAITS_UI = etsdep('Traits[ui]', '3.0.0b1')

# The following "soft dependencies" are wrapped in try..except blocks
#APPTOOLS -- util/wx/drag_and_drop
#SCIMATH -- util/wx/spreadsheet/unit_renderer.py

def generate_docs():
    """If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')
    source_dir = os.path.join(doc_dir, 'source')
    html_zip = os.path.join(doc_dir,  'html.zip')
    dest_dir = doc_dir
    
    required_sphinx_version = "0.4.1"
    sphinx_installed = False
    try:
        require("Sphinx>=%s" % required_sphinx_version)
        sphinx_installed = True
    except (DistributionNotFound, VersionConflict):
        log.warn('Sphinx install of version %s could not be verified.'
                    ' Trying simple import...' % required_sphinx_version)
        try:
            import sphinx
            if parse_version(sphinx.__version__) < parse_version(required_sphinx_version):
                log.error("Sphinx version must be >=%s." % required_sphinx_version)
            else:
                sphinx_installed = True
        except ImportError:
            log.error("Sphnix install not found.")
    
    if sphinx_installed:             
        log.info("Generating %s documentation..." % INFO['name'])
        docsrc = source_dir
        target = dest_dir
        
        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': docsrc,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False
                }, [])
            del build
            
        except:
            log.error("The documentation generation failed.  Falling back to "
                      "the zip file.")
            
            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, doc_dir)
    else:
        # Unzip the docs into the 'html' folder.
        log.info("Installing %s documentaion from zip file.\n" % INFO['name'])
        unzip_html_docs(html_zip, doc_dir)

def unzip_html_docs(src_path, dest_dir):
    """Given a path to a zipfile, extract
    its contents to a given 'dest_dir'.
    """
    file = zipfile.ZipFile(src_path)
    for name in file.namelist():
        cur_name = os.path.join(dest_dir, name)
        if not name.endswith('/'):
            out = open(cur_name, 'wb')
            out.write(file.read(name))
            out.flush()
            out.close()
        else:
            if not os.path.exists(cur_name):
                os.mkdir(cur_name)
    file.close()

class my_develop(develop):
    def run(self):
        develop.run(self)
        # Generate the documentation.
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        # Generate the documentation.
        generate_docs()

setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    cmdclass = {
        'develop': my_develop,
        'build': my_build
    },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = 'EnthoughtBase is the root project of all other ETS projects',
    extras_require = {
        'agent': [
            ENVISAGECORE,
            TRAITS,
            TRAITSGUI,
            ],
        'distribution': [
            TRAITS_UI,
            ],
        'envisage': [
            ENVISAGECORE,
            ENVISAGEPLUGINS,
            TRAITSGUI,
            TRAITS_UI,
            ],
        'traits': [
            TRAITS,
            TRAITSBACKENDWX,
            ],
        'ui': [    # -- this includes util.ui.* and util.wx.* (see extras.map)
            TRAITSGUI,
            TRAITS_UI,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            ],
        },
    license = 'BSD',
    include_package_data = True,
    install_requires = [
        ],
    name = 'EnthoughtBase',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = INFO['version'],
    zip_safe = False,
    )

