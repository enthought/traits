#!/usr/bin/env python
import logging
import time
import zipfile

from enthought.envisage.ui.workbench.api import WorkbenchApplication
from enthought.envisage.api import Plugin
from enthought.pyface.workbench.api import Perspective, PerspectiveItem
from enthought.traits.api import Callable, List


def write_str_to_zipfile(zf, path, bytes, mode=0644):
    """ Write a string to filename in a .zip file.

    Parameters
    ----------
    zf : zipfile.ZipFile
        The .zip file object to add to.
    path : str
        The filename inside of the ZipFile.
    bytes : str
        The bytes comprising the content of the file.
    """
    now = time.localtime(time.time())[:6]
    info = zipfile.ZipInfo(path)
    info.date_time = now
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (mode & 0xFFFF) << 16
    zf.writestr(info, bytes)

class LoggerDemoPerspective(Perspective):
    name = 'Logger Demo'
    enabled = True
    show_editor_area = False
    contents = [
        PerspectiveItem(id='enthought.logger.plugin.view.logger_view.LoggerView', position='top'),
        PerspectiveItem(id='enthought.plugins.python_shell_view', position='bottom'),
    ]

class LoggerDemoPlugin(Plugin):
    """ Add some perspectives.
    """

    id = 'LoggerDemoPlugin'

    BINDINGS = 'enthought.plugins.python_shell.bindings'
    PERSPECTIVES = 'enthought.envisage.ui.workbench.perspectives'
    COMMANDS = 'enthought.plugins.python_shell.commands'
    MAIL_FILES = 'enthought.logger.plugin.mail_files'
    
    perspectives = List(contributes_to=PERSPECTIVES)
    bindings = List(contributes_to=BINDINGS)
    commands = List(contributes_to=COMMANDS)
    mail_files = List(contributes_to=MAIL_FILES)

    def _perspectives_default(self):
        return [LoggerDemoPerspective]

    def _bindings_default(self):
        bindings = [dict(
            test=self._test,
            test_timing=self._test_timing,
        )]
        return bindings

    def _commands_default(self):
        commands = [
            'import logging',
        ]
        return commands

    def _mail_files_default(self):
        return [self._package_project_files]

    def _test(self, n=2000):
        for i in range(n):
            logging.warn('foo %r', i)

    def _test_timing(self, n=2000):
        t = time.time()
        for i in range(1,n+1):
            if not (i%100):
                t2 = time.time()
                print '%1.2f s for 100 logs' % (t2-t)
                t = t2
            logging.warn('foo %r', i)

    def _package_project_files(self, zf):
        """ Add dummy project files to the userdata.zip file to be mailed back.
        """
        write_str_to_zipfile(zf, 'logger_demo/data.txt', 'Foo!\n')


def main():
    from enthought.envisage.core_plugin import CorePlugin
    from enthought.envisage.ui.workbench.workbench_plugin import WorkbenchPlugin
    from enthought.logger.plugin.logger_plugin import LoggerPlugin
    from enthought.plugins.python_shell.python_shell_plugin import PythonShellPlugin
    plugins = [
        CorePlugin(),
        WorkbenchPlugin(),
        LoggerPlugin(),
        PythonShellPlugin(),
        LoggerDemoPlugin(),
    ]
    app = WorkbenchApplication(
        id='enthought.logger.demo',
        name='Logger Demo',
        plugins=plugins,
    )
    app.run()

if __name__ == '__main__':
    main()
