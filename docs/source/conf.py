# -*- coding: utf-8 -*-
#
# Traits documentation build configuration file, created by
# sphinx-quickstart on Tue Jul 22 10:52:03 2008.
#
# This file is execfile()d with the current directory set to its containing
# dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed
# automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.
from __future__ import print_function
import datetime
import io
import os
import sys

import six


# The docset build will use slightly different formatting rules
BUILD_DOCSET = bool(os.environ.get("BUILD_DOCSET"))

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
sys.path.append(os.path.abspath("../../"))


def mock_modules():
    """ Optionally Mock missing modules to allow autodoc based documentation.

    The ``traits.has_dynamics_view`` imports the traitsui module and
    thus traitsui is needed so that the ``autodoc`` extension can
    extract the docstrings from the has_dynamics_view module. This
    function optionally mocks the traitsui module so that the traits
    documentation can be built without the traitui optional dependency
    installed.

    .. note::

       The mock library is needed in order to mock the traitsui
       package.

    """

    MOCK_MODULES = []
    MOCK_TYPES = []

    # Check to see if we need to mock the traitsui package
    try:
        import traitsui
    except ImportError:
        # Modules that we need to mock
        MOCK_MODULES = [
            "traitsui",
            "traitsui.api",
            "traitsui.delegating_handler",
        ]

        # Collect the types from traitsui that are based on HasTraits
        # We will need to mock them in a special way so that
        # TraitDocumenter can properly identify and document traits.
        from traits.api import HasTraits, HasPrivateTraits

        MOCK_TYPES.append(
            ("traitsui.delegating_handler", "DelegatingHandler", (HasTraits,))
        )
        MOCK_TYPES.append(
            ("traitsui.view_element", "ViewSubElement", (HasPrivateTraits,))
        )
    else:
        return

    if six.PY2:
        try:
            from mock import MagicMock
        except ImportError:
            if len(MOCK_MODULES) != 0:
                print(
                    "NOTE: TraitsUI is not installed and mock is not "
                    "available to mock the missing modules, some classes "
                    "will not be documented"
                )
                return
    else:
        from unittest.mock import MagicMock

    # Create the custom types for the HasTraits based traitsui objects.
    TYPES = {
        mock_type: type(mock_type, bases, {"__module__": path})
        for path, mock_type, bases in MOCK_TYPES
    }

    class DocMock(MagicMock):
        """ The special sphinx friendly mocking class to mock missing packages.

        Based on the suggestion from http://docs.readthedocs.org/en/latest/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules

        """

        @classmethod
        def __getattr__(self, name):
            if name in ("__file__", "__path__", "_mock_methods"):
                # sphinx does not like getting a Mock object in this case.
                return "/dev/null"
            else:
                # Return a mock or a custom type as requested.
                return TYPES.get(name, DocMock(mocked_name=name))

        # MagicMock does not define __call__ we do just to make sure
        # that we cover all cases.
        def __call__(self, *args, **kwards):
            return DocMock()

        @property
        def __name__(self):
            # Make sure that if sphinx asks for the name of a Mocked class
            # it gets a nice strings to use (instead of "DocMock")
            return self.mocked_name

    # Add the mocked modules to sys
    sys.modules.update(
        (mod_name, DocMock(mocked_name=mod_name)) for mod_name in MOCK_MODULES
    )

    # Report on what was mocked.
    print(
        "mocking modules {0} and types {1}".format(
            MOCK_MODULES, [mocked[1] for mocked in MOCK_TYPES]
        )
    )


mock_modules()

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "traits.util.trait_documenter",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General substitutions.
project = "traits"
copyright = "2008-{date.year}, Enthought Inc".format(date=datetime.date.today())

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
version_info = {}
traits_init_path = os.path.join("..", "..", "traits", "__init__.py")
with io.open(traits_init_path, "r", encoding="utf-8") as version_module:
    version_code = compile(version_module.read(), "__init__.py", "exec")
    exec(version_code, version_info)
version = release = version_info["__version__"]

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = "%B %d, %Y"

# List of documents that shouldn't be included in the build.
# unused_docs = []

# List of directories, relative to source directories, that shouldn't be
# searched for source files.
# exclude_dirs = []

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Options for the autodoc extension.
autodoc_default_flags = ["members"]

autodoc_member_order = "bysource"


# Options for HTML output
# -----------------------

# Use enthought-sphinx-theme if available
try:
    import enthought_sphinx_theme

    html_theme_path = [enthought_sphinx_theme.theme_path]
    html_theme = "enthought"

    html_static_path = []
    templates_path = []

except ImportError as exc:
    import warnings

    msg = """Can't find Enthought Sphinx Theme, using default.
                Exception was: {}
                Enthought Sphinx Theme can be installed from PyPI or EDM"""
    warnings.warn(RuntimeWarning(msg.format(exc)))

    # Use old defaults if enthought-sphinx-theme not available

    # The name of an image file (within the static path) to place at the top
    # of the sidebar.
    html_logo = os.path.join("_static", "e-logo-rev.png")

    # The name of an image file (within the static path) to use as favicon of
    # the docs.  This file should be a Windows icon file (.ico) being 16x16
    # or 32x32 pixels large.
    html_favicon = os.path.join("_static", "et.ico")

    # The style sheet to use for HTML and HTML Help pages. A file of that name
    # must exist either in Sphinx' static/ path, or in one of the custom paths
    # given in html_static_path.
    html_style = "default.css"

    # Add any paths that contain custom static files (such as style sheets)
    # here, relative to this directory. They are copied after the builtin
    # static files, so a file named "default.css" will overwrite the builtin
    # "default.css".
    html_static_path = ["_static"]

    # Add any paths that contain templates here, relative to this directory.
    templates_path = ["_templates"]


# When using docset browsers like Dash and Zeal the side bar is redundant.
if BUILD_DOCSET:
    html_theme_options = {"nosidebar": "true"}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "Traits 5 User Manual"

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
html_use_modindex = BUILD_DOCSET

# If false, no index is generated.
html_use_index = BUILD_DOCSET

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, the reST sources are included in the HTML build as _sources/<name>.
# html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = "Traitsdoc"


# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
# latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
# latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author,
#  document class [howto/manual]).
latex_documents = [
    (
        "index",
        "Traits.tex",
        "Traits 5 User Manual",
        "Enthought, Inc.",
        "manual",
    )
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = "enthought_logo.jpg"
latex_logo = "e-logo-rev.png"

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# Additional stuff for the LaTeX preamble.
# latex_preamble = ''

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_use_modindex = True

# Options for Texinfo output
# --------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "traits",
        "Traits 5 User Manual",
        "Enthought, Inc.",
        "Traits",
        "Explicitly typed attributes for Python.",
        "Python",
    )
]
