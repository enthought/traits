#------------------------------------------------------------------------------
#  file: refactor_doc.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
"""
.. warning::
        This is a smelly module (i.e. architecture and speed) but the
        first working implementation of my view on refactoring the source rst
        documentation so that is shpinx friendly.
"""
import re

#------------------------------------------------------------------------------
#  Precompiled regexes
#------------------------------------------------------------------------------
indent_regex = re.compile(r'\s+')

#------------------------------------------------------------------------------
#  Functions to manage indention
#------------------------------------------------------------------------------

def add_indent(lines, indent=4):
    """ Add spaces to indent a list of lines.

    Arguments
    ---------
    lines : list
        The list of strings to indent.

    indent : int
        The number of spaces to add.

    Returns
    -------
    lines : list
        The indented strings (lines).

    .. note:: Empty strings are not changed

    """
    indent_str = ' ' * indent
    output = []
    for line in lines:
        if is_empty(line):
            output.append(line)
        else:
            output.append(indent_str + line)
    return output

def remove_indent(lines):
    """ Remove all indentation from the lines.

    """
    return [line.lstrip() for line in lines]

def get_indent(line):
    """ Return the indent portion of the line.

    """
    indent = indent_regex.match(line)
    if indent is None:
        return ''
    else:
        return indent.group()

#------------------------------------------------------------------------------
#  Functions to detect line type
#------------------------------------------------------------------------------

def is_variable_field(line, indent=''):
    regex = indent + r'\w+\s:\s*'
    match = re.match(regex, line)
    return match

def is_method_field(line, indent=''):
    regex = indent + r'\w+\(.*\)\s*'
    match = re.match(regex, line)
    return match

def is_empty(line):
    return not line.strip()

#------------------------------------------------------------------------------
#  Classes
#------------------------------------------------------------------------------
class BaseDocstring(object):
    """Base abstract docstring refactoring class.

    The class' main purpose is to parse the dosctring and find the
    sections that need to be refactored. It also provides a number of
    methods to help with the refactoring. Subclasses should provide
    the methods responsible for refactoring the sections.

    Attributes
    ----------
    docstring : list
        A list of strings (lines) that holds docstrings

    index : int
        The current zero-based line number of the docstring that is
        proccessed.

    verbose : bool
        When set the class prints a lot of info about the proccess
        during runtime.

    headers : dict
        The sections that the class refactors. Each entry in the
        dictionary should have as key the name of the section in the
        form that it appears in the docstrings. The value should be
        the postfix of the method, in the subclasses, that is
        responsible for refactoring (e.g. {'Methods': 'method'}).

    Methods
    -------
    extract_fields(indent='', field_check=None)
        Extract the fields from the docstring

    get_field()
        Get the field description.

    get_next_paragraph()
        Get the next paragraph designated by an empty line.

    is_section()
        Check if the line defines a section.

    parse_field(lines)
        Parse a field description.

    peek(count=0)
        Peek ahead

    read()
        Return the next line and advance the index.

    insert_lines(lines, index)
        Insert refactored lines

    remove_lines(index, count=1)
        Removes the lines for the docstring

    seek_to_next_non_empty_line()
        Goto the next non_empty line

    """

    def __init__(self, lines, headers = None, verbose=False):
        """ Initialize the class

        The method setups the class attributes and starts parsing the
        docstring to find and refactor the sections.

        Arguments
        ---------
        lines : list of strings
            The docstring to refactor

        headers : dict
            The sections for which the class has custom refactor methods.
            Each entry in the dictionary should have as key the name of
            the section in the form that it appears in the docstrings.
            The value should be the postfix of the method, in the
            subclasses, that is responsible for refactoring (e.g.
            {'Methods': 'method'}).

        verbose : bool
            When set the class prints a lot of info about the proccess
            during runtime.

        """
        try:
            self._docstring = lines.splitlines()
        except AttributeError:
            self._docstring = lines
        self.verbose = verbose
        if headers is None:
            self.headers = {}
        else:
            self.headers = headers
        self.index = 0

        if self.verbose:
            print 'INPUT DOCSTRING'
            print '\n'.join(lines)
        self.parse()
        if self.verbose:
            print 'OUTPUT DOCSTRING'
            print '\n'.join(lines)

    def parse(self):
        """ Parse the docstring.

        The docstring is parsed for sections. If a section is found then
        the corresponding refactoring method is called.

        """
        self.index = 0
        self.seek_to_next_non_empty_line()
        while not self.eol:
            if self.verbose:
                print 'current index is', self.index
            header = self.is_section()
            if header:
                self._refactor(header)
            else:
                self.index += 1
                self.seek_to_next_non_empty_line()

    def _refactor(self, header):
        """Call the heading refactor method.

        The name of the refctoring method is constructed using the form
        _refactor_<header>. Where <header> is the value corresponding to
        ``self.headers[header]``. If there is no custom method for the
        section then the self._refactor_header() is called with the
        found header name as input.

        """
        if self.verbose:
            print 'Header is', header
            print 'Line is', self.index

        refactor_postfix = self.headers.get(header, 'header')
        method_name = ''.join(('_refactor_', refactor_postfix))
        method = getattr(self, method_name)
        method(header)

    def _refactor_header(self, header):
        """ Refactor the header section using the rubric directive.

        """
        if self.verbose:
            print 'Refactoring {0}'.format(header)
        index = self.index
        indent = get_indent(self.peek())
        self.remove_lines(index, 2)
        descriptions = []
        descriptions.append(indent + '.. rubric:: {0}'.format(header))
        descriptions.append('')
        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return descriptions


    def extract_fields(self, indent='', field_check=None):
        """Extract the fields from the docstring

        Parse the fields into tuples of name, type and description in a
        list of strings. The strings are also removed from the list.

        Arguments
        ---------
        indent : str, optional
            the indent argument is used to make sure that only the lines
            with the same indent are considered when checking for a
            field header line. The value is used to define the field
            checking function.

        field_check : function
            Optional function to use for checking if the next line is a
            field. The signature of the function is ``foo(line)`` and it
            should return ``True`` if the line contains a valid field
            The default function is checking for fields of the following
            formats::

                <name> : <type>

            or::

                <name> :

            Where the name has to be one word.

        Returns
        -------
        parameters : list of tuples
            list of parsed parameter tuples as returned from the
            :meth:`~BaseDocstring.parse_field` method.

        """

        #TODO raise error when there is no parameter

        if self.verbose:
            print "PARSING PARAMETERS"

        if field_check:
            is_field = field_check
        else:
            is_field = is_variable_field

        parameters = []

        while (not self.eol) and is_field(self.peek(), indent):
            field = self.get_field()
            if self.verbose:
                print "next field is: ", field
            parameters.append(self.parse_field(field))

        return parameters

    def parse_field(self, lines):
        """Parse a field description.

        The field is assumed to be in the following formats::

            <name> : <type>
                <description>

            <name> :
                <description>

            <name>
                <description>


        Arguments
        ---------
        lines :
            docstring lines to parse for the field.

        Returns
        -------
        arg_name : str
            The name of the parameter.

        arg_type : str
            The type of the parameter (if defined).

        desc : list
            A list of the strings that make up the description.

        """
        header = lines[0].strip()
        if ' :' in header:
            arg_name, arg_type = re.split(' \:\s?', header)
        else:
            arg_name, arg_type = header, ''
        if self.verbose:
            print "name is:", arg_name, " type is:", arg_type
            print "the output of 're.split(' \:\s?', header)' was", \
                        re.split(' \:\s?', header)
        if len(lines) > 1:
            lines = [line.rstrip() for line in lines]
            return arg_name.strip(), arg_type.strip(), lines[1:]
        else:
            return arg_name.strip(), arg_type.strip(), ['']

    def get_field(self):
        """ Get the field description.

        The method reads lines (staring with the first line of the field)
        until a line with the same indent appears.

        """
        docstring = self.docstring
        index = self.index
        field = self.read()
        initial_indent = len(get_indent(field))
        lines = [field]
        empty_lines = 0

        for line in docstring[(index + 1):]:
            indent = len(get_indent(line))
            if is_empty(line):
                empty_lines += 1
            else:
                empty_lines = 0
            if (indent <= initial_indent) and not is_empty(line):
                break
            if empty_lines > 1:
                break
            lines.append(line)

        del docstring[index:(index + len(lines))]
        self.index = index
        return lines[:-1]

    def is_section(self):
        """Check if the line defines a section.

        """
        if self.eol:
            return False

        # peek at line
        header = self.peek()

        if self.verbose:
            print 'current line is: {0} at index {1}'.format(header, self.index)

        # peek at second line
        line2 = self.peek(1)

        if self.verbose:
            print 'second line is:', header

        # check for underline type format
        underline = re.match(r'\s*\S+\s*\Z', line2)
        if underline is None:
            return False
        # is the nextline an rst underline?
        striped_header = header.rstrip()
        expected_underline1 = re.sub(r'[A-Za-z]|\b\s', '-', striped_header)
        expected_underline2 = re.sub(r'[A-Za-z]|\b\s', '=', striped_header)
        if ((underline.group().rstrip() == expected_underline1) or
            (underline.group().rstrip() == expected_underline2)):
            return header.strip()
        else:
            return False

    def insert_lines(self, lines, index):
        """ Insert refactored lines

        Arguments
        ---------
        new_lines : list
            The list of lines to insert

        index : int
            Index to start the insertion
        """
        docstring = self.docstring
        for line in reversed(lines):
            docstring.insert(index, line)

    def seek_to_next_non_empty_line(self):
        """ Goto the next non_empty line

        """
        docstring = self.docstring
        for line in docstring[self.index:]:
            if not is_empty(line):
                break
            self.index += 1


    def get_next_paragraph(self):
        """ Get the next paragraph designated by an empty line.

        """
        docstring = self.docstring
        lines = []
        index = self.index

        for line in docstring[index:]:
            if is_empty(line):
                break
            lines.append(line)

        del docstring[index:(index + len(lines))]
        return lines

    def read(self):
        """ Return the next line and advance the index.

        """
        index = self.index
        line = self._docstring[index]
        self.index += 1
        return line

    def remove_lines(self, index, count=1):
        """ Removes the lines for the docstring

        """
        docstring = self.docstring
        del docstring[index:(index + count)]

    def peek(self, ahead=0):
        """ Peek ahead a number of lines

        The function retrieves the line that is ahead of the current
        index. If the index is at the end of the list then it returns an
        empty string.

        Arguments
        ---------
        ahead : int
            The number of lines to look ahead.


        """
        position = self.index + ahead
        try:
            line = self.docstring[position]
        except IndexError:
            line = ''
        return line

    @property
    def eol(self):
        return self.index >= len(self.docstring)

    @property
    def docstring(self):
        """ Get the docstring lines.

        """
        return self._docstring


class FunctionDocstring(BaseDocstring):
    """Docstring refactoring for functions"""

    def __init__(self, lines, headers=None, verbose=False):

        if headers is None:
            headers = {'Returns': 'returns', 'Arguments': 'arguments',
                       'Parameters': 'arguments', 'Raises': 'raises',
                       'Yields': 'returns', 'Notes':'notes'}

        super(FunctionDocstring, self).__init__(lines, headers, verbose)
        return

    def _refactor_returns(self, header):
        """Refactor the return section to sphinx friendly format"""

        if self.verbose:
            print 'Returns section refactoring'

        descriptions = []
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        fields = self.extract_fields(indent)

        if self.verbose:
            print 'Return items'
            print fields

        # generate sphinx friendly rst
        descriptions = []
        descriptions.append(indent + ':returns:')
        if len(fields) == 1:
            name_format = '**{0}** '
        else:
            name_format = '- **{0}** '

        for arg_name, arg_type, desc in fields:
            arg_name = indent + '    ' + name_format.format(arg_name)
            if arg_type != '':
                arg_type = '({0})'.format(arg_type)
            else:
                arg_type = ''
            if not is_empty(desc[0]):
                arg_type = arg_type + ' - '
            paragraph = ' '.join(remove_indent(desc))
            descriptions.append(arg_name + arg_type + paragraph)

        descriptions.append('')
        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return

    def _refactor_raises(self, header):
        """Refactor the raises section to sphinx friendly format"""

        if self.verbose:
            print 'Raised section refactoring'

        descriptions = []
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        fields = self.extract_fields(indent)

        if self.verbose:
            print 'Raised Errors'
            print fields

        descriptions = []
        descriptions.append(indent + ':raises:')
        if len(fields) == 1:
            name_format = '**{0}** '
        else:
            name_format = '- **{0}** '

        for arg_name, arg_type, desc in fields:
            if not is_empty(desc[0]):
                arg_name = name_format.format(arg_name) + '- '
            else:
                arg_name = name_format.format(arg_name)
            arg_name = indent + '    ' + arg_name
            paragraph = ' '.join(remove_indent(desc))
            descriptions.append(arg_name + paragraph)
        descriptions.append('')

        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return

    def _refactor_arguments(self, header):
        """Refactor the argument section to sphinx friendly format"""

        if self.verbose:
            print '{0} Section'.format(header)

        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        parameters = self.extract_fields(indent)

        descriptions = []
        for arg_name, arg_type, desc in parameters:
            descriptions.append(indent + ':param {0}: {1}'.\
                                format(arg_name, desc[0].strip()))
            desc = add_indent(desc)
            for line in desc[1:]:
                descriptions.append('{0}'.format(line))
            descriptions.append(indent + ':type {0}: {1}'.\
                                format(arg_name, arg_type))
        descriptions.append('')
        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return

    def _refactor_notes(self, header):
        """Refactor the argument section to sphinx friendly format"""

        if self.verbose:
            print 'Refactoring Notes'

        descriptions = []
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        paragraph = self.get_next_paragraph()
        descriptions.append(indent + '.. note::')
        descriptions += add_indent(paragraph)
        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return descriptions


class ClassDocstring(BaseDocstring):
    """Docstring refactoring for classes"""

    def __init__(self, lines, headers=None, verbose=False):

        if headers is None:
            headers = {'Attributes': 'attributes', 'Methods': 'methods',
                       'See Also': 'header', 'Abstract Methods': 'methods',
                       'Notes':'notes'}

        super(ClassDocstring, self).__init__(lines, headers, verbose)
        return

    def _refactor_attributes(self, header):
        """Refactor the attributes section to sphinx friendly format"""

        if self.verbose:
            print '{0} Section'.format(header)

        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        parameters = self.extract_fields(indent)

        descriptions = []
        for arg_name, arg_type, desc in parameters:
            descriptions.append(indent + '.. attribute:: {0}'.\
                                format(arg_name))
            descriptions.append(' ')
            description_indent = get_indent(desc[0])
            if arg_type != '':
                arg_type = description_indent + '*({0})*'.format(arg_type)
                descriptions.append(arg_type)
            paragraph = ' '.join(desc)
            descriptions.append(paragraph)
            descriptions.append('')

        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return

    def _refactor_methods(self, header):
        """Refactor the attributes section to sphinx friendly format"""
        if self.verbose:
            print '{0} section'.format(header)

        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        parameters = self.extract_fields(indent, is_method_field)

        descriptions = []
        if len(parameters) > 0 :
            max_name_length, max_method_length, max_desc_length = \
                                                    self.max_lengths(parameters)
            max_method_length += 11 + max_name_length  # to account for the
                                                       # additional rst directives
            first_column = len(indent)
            second_column = first_column + max_method_length + 1
            table_line = '{0}{1} {2}'.format(indent, '=' * max_method_length,
                                             '=' * max_desc_length)
            empty_line = table_line.replace('=', ' ')
            headings_line = empty_line[:]
            headings_line = self.replace_at('Methods', headings_line,
                                            first_column)
            headings_line = self.replace_at('Description', headings_line,
                                            second_column)
            descriptions.append(table_line)
            descriptions.append(headings_line)
            descriptions.append(table_line)
            for arg_name, arg_type, desc in parameters:
                split_result = re.split('\((.*)\)', arg_name)
                name = split_result[0]
                method_text = ':meth:`{0} <{1}>`'.format(arg_name, name)
                summary = ' '.join(desc)
                line = empty_line[:]
                line = self.replace_at(method_text, line, first_column)
                line = self.replace_at(summary, line, second_column)
                descriptions.append(line)
            descriptions.append(table_line)
            descriptions.append('')
            descriptions.append('|')
            descriptions.append('')

        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return

    def _refactor_notes(self, header):
        """Refactor the note section to use the rst ``.. note`` directive.

        """
        if self.verbose:
            print '{0} Section'.format(header)
        descriptions = []
        index = self.index
        self.remove_lines(index, 2)
        indent = get_indent(self.peek())
        paragraph = self.get_next_paragraph()
        descriptions.append(indent + '.. note::')
        descriptions += add_indent(paragraph)
        self.insert_lines(descriptions, index)
        self.index += len(descriptions)
        return descriptions

    # FIXME: I do not like this function.
    def max_lengths(self, parameters):
        """ Find the max lenght of the name and discription in the
        parameters.

        Arguments
        ---------
        parameters : list of tuples
            list of parsed parameter tuples as returned from the
            :meth:`~_FunctionDocString._parse_parameter` function.

        """
        max_name_length = max([parameter[0].find('(')
                               for parameter in parameters])
        max_method_length = max([len(parameter[0])
                               for parameter in parameters])
        max_desc_length = max([len(' '.join(parameter[2]))
                               for parameter in parameters])
        return max_name_length, max_method_length, max_desc_length

    def replace_at(self, word, line, index):
        """ Replace the text in line

        The text in line is replaced with the word without changing the
        size of the line (in most cases). The replacement starts at the
        provided index.

        Arguments
        ---------
        word : str
            The text to copy into the line.

        line : str
            The line where the copy takes place.

        index : int
            The index to start coping.

        Returns
        -------
        result : str
            line of text with the text replaced.

        """
        word_length = len(word)
        line_list = list(line)
        line_list[index: (index + word_length)] = list(word)
        return ''.join(line_list)

#------------------------------------------------------------------------------
# Extension definition
#------------------------------------------------------------------------------
def refactor_docstring(app, what, name, obj, options, lines):

    verbose = False
    # if 'component.Component' in name:
        # verbose = True

    if ('class' in what):
        ClassDocstring(lines, verbose=verbose)
    elif ('function' in what) or ('method' in what):
        FunctionDocstring(lines, verbose=verbose)

def setup(app):
    app.setup_extension('sphinx.ext.autodoc')
    app.connect('autodoc-process-docstring', refactor_docstring)
