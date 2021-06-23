# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
    A Trait Documenter
    (Subclassed from the autodoc ClassLevelDocumenter)

"""
from importlib import import_module
import inspect
import io
import token
import tokenize
import traceback

from sphinx.ext.autodoc import ClassLevelDocumenter
from sphinx.util import logging

from traits.has_traits import MetaHasTraits
from traits.trait_type import TraitType
from traits.traits import generic_trait


logger = logging.getLogger(__name__)


def _is_class_trait(name, cls):
    """ Check if the name is in the list of class defined traits of ``cls``.
    """
    return (
        isinstance(cls, MetaHasTraits)
        and name in cls.__class_traits__
        and cls.__class_traits__[name] is not generic_trait
    )


class TraitDocumenter(ClassLevelDocumenter):
    """ Specialized Documenter subclass for trait attributes.

    The class defines a new documenter that recovers the trait definition
    signature of module level and class level traits.

    To use the documenter, append the module path in the extension
    attribute of the `conf.py`.
    """

    # ClassLevelDocumenter interface #####################################

    objtype = "traitattribute"
    directivetype = "attribute"
    member_order = 60

    # must be higher than other attribute documenters
    priority = 12

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        """ Check that the documented member is a trait instance.
        """
        check = (
            isattr
            and issubclass(type(member), TraitType)
            or _is_class_trait(membername, parent.object)
        )
        return check

    def document_members(self, all_members=False):
        """ Trait attributes have no members """
        pass

    def import_object(self):
        """ Get the Trait object.

        Notes
        -----
        Code adapted from autodoc.Documenter.import_object.

        """
        try:
            current = self.module = import_module(self.modname)
            for part in self.objpath[:-1]:
                current = self.get_attr(current, part)
            name = self.objpath[-1]
            self.object_name = name
            self.object = None
            self.parent = current
            return True
        # this used to only catch SyntaxError, ImportError and
        # AttributeError, but importing modules with side effects can raise
        # all kinds of errors.
        except Exception as err:
            if self.env.app and not self.env.app.quiet:
                self.env.app.info(traceback.format_exc().rstrip())
            msg = (
                "autodoc can't import/find {0} {r1}, it reported error: "
                '"{2}", please check your spelling and sys.path'
            )
            self.directive.warn(
                msg.format(self.objtype, str(self.fullname), err)
            )
            self.env.note_reread()
            return False

    def add_directive_header(self, sig):
        """ Add the directive header 'attribute' with the annotation
        option set to the trait definition.

        """
        ClassLevelDocumenter.add_directive_header(self, sig)
        try:
            definition = trait_definition(
                cls=self.parent,
                trait_name=self.object_name,
            )
        except ValueError:
            # Without this, a failure to find the trait definition aborts
            # the whole documentation build.
            logger.warning(
                "No definition for the trait {!r} could be found in "
                "class {!r}.".format(self.object_name, self.parent),
                exc_info=True)
            return

        # Workaround for enthought/traits#493: if the definition is multiline,
        # throw away all lines after the first.
        if "\n" in definition:
            definition = definition.partition("\n")[0] + " …"

        self.add_line("   :annotation: = {0}".format(definition), "<autodoc>")


def trait_definition(*, cls, trait_name):
    """ Retrieve the portion of the source defining a Trait attribute.

    For example, given a class::

        class MyModel(HasStrictTraits)
            foo = List(Int, [1, 2, 3])

    ``trait_definition(cls=MyModel, trait_name="foo")`` returns
    ``"List(Int, [1, 2, 3])"``.

    Parameters
    ----------
    cls : MetaHasTraits
        Class being documented.
    trait_name : str
        Name of the trait being documented.

    Returns
    -------
    str
        The portion of the source containing the trait definition. For
        example, for a class trait defined as ``"my_trait = Float(3.5)"``,
        the returned string will contain ``"Float(3.5)"``.

    Raises
    ------
    ValueError
        If *trait_name* doesn't appear as a class-level variable in the
        source.
    """
    # Get the class source and tokenize it.
    source = inspect.getsource(cls)
    string_io = io.StringIO(source)
    tokens = tokenize.generate_tokens(string_io.readline)

    # find the trait definition start
    trait_found = False
    name_found = False
    while not trait_found:
        item = next(tokens, None)
        if item is None:
            break
        if name_found and item[:2] == (token.OP, "="):
            trait_found = True
            continue
        if item[:2] == (token.NAME, trait_name):
            name_found = True

    if not trait_found:
        raise ValueError(
            "No trait definition for {!r} found in {!r}".format(
                trait_name, cls)
        )

    # Retrieve the trait definition.
    definition_tokens = _get_definition_tokens(tokens)
    definition = tokenize.untokenize(definition_tokens).strip()
    return definition


def _get_definition_tokens(tokens):
    """ Given the tokens, extracts the definition tokens.

    Parameters
    ----------
    tokens : iterator
        An iterator producing tokens.

    Returns
    -------
    A list of tokens for the definition.
    """
    # Retrieve the trait definition.
    definition_tokens = []
    first_line = None

    for type, name, start, stop, line_text in tokens:
        if first_line is None:
            first_line = start[0]

        if type == token.NEWLINE:
            break

        item = (
            type,
            name,
            (start[0] - first_line + 1, start[1]),
            (stop[0] - first_line + 1, stop[1]),
            line_text,
        )

        definition_tokens.append(item)

    return definition_tokens


def setup(app):
    """ Add the TraitDocumenter in the current sphinx autodoc instance. """
    app.add_autodocumenter(TraitDocumenter)
