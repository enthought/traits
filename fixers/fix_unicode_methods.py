from lib2to3 import fixer_base
from lib2to3.fixer_util import Name


class FixUnicodeMethods(fixer_base.BaseFix):
    """ Custom fixer for the __unicode__ method

    Renames __unicode__ methods to __str__.

    Code used from:
    http://lucumr.pocoo.org/2010/2/11/porting-to-python-3-a-guide/

    """
    PATTERN = r"funcdef< 'def' name='__unicode__' parameters< '(' NAME ')' > any+ >"  # noqa

    def transform(self, node, results):
        name = results['name']
        name.replace(Name('__str__', prefix=name.prefix))
