import logging
import os.path
from email import Encoders
from email.MIMEBase import MIMEBase

from enthought.envisage import get_application
from enthought.envisage.core.application import Application
from enthought.traits.api import Instance


# Setup a logger for this module.
logger = logging.getLogger(__name__)


class Attachments:

    app = Instance(Application)
    message = None

    def __init__(self, message):
        self.app = get_application()
        self.message = message


    def package_workspace(self):
        if self.app is None:
            pass

        workspace = self.app.service_registry.get_service('enthought.envisage.project.IWorkspace')
        if workspace is not None:
            dir = workspace.path
            self._attach_directory(dir)
        return


    def package_single_project(self):
        if self.app is None:
            pass

        single_project = self.app.service_registry.get_service('enthought.envisage.single_project.ModelService')
        if single_project is not None:
            dir = single_project.location
            self._attach_directory(dir)

    def package_proava2_project(self):
        if self.app is None:
            pass

        plugin = self.app.service_registry.get_service('cp.proava2.IAttributeManager')
        if (plugin is not None) and (plugin.active_project is not None):
            dir = os.path.join(plugin.active_project.path, plugin.active_project.name)
            self._attach_directory(dir)


    def package_any_relevant_files(self):
        self.package_workspace()
        self.package_single_project()
        self.package_proava2_project()
        return

    def _attach_directory(self, dir):
        relpath = os.path.basename(dir)

        import zipfile
        from cStringIO import StringIO

        ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg = MIMEBase(maintype, subtype)

        file_object = StringIO()
        zip = zipfile.ZipFile(file_object, 'w')
        _append_to_zip_archive(zip, dir, relpath)
        zip.close()

        msg.set_payload(file_object.getvalue())

        Encoders.encode_base64(msg) # Encode the payload using Base64
        msg.add_header('Content-Disposition', 'attachment', filename='project.zip')

        self.message.attach(msg)

        file_object.close()




def _append_to_zip_archive(zip, dir, relpath):
    """ Add all files in and below directory dir into zip archive"""
    for filename in os.listdir(dir):
        path = os.path.join(dir, filename)

        if os.path.isfile(path):
            name = os.path.join(relpath, filename)
            zip.write(path, name)
            logger.debug('adding %s to error report' % path)
        else:
            if filename != ".svn": # skip svn files if any
                subdir = os.path.join(dir, filename)
                _append_to_zip_archive(zip, subdir, os.path.join(relpath, filename))
    return

