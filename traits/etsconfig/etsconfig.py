# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Enthought Tool Suite configuration information. """


# Standard library imports.
import contextlib
import os
import sys


class ETSToolkitError(RuntimeError):
    """ Error raised by issues importing ETS toolkits

    Attributes
    ----------
    message : str
        The message detailing the error.

    toolkit : str or None
        The toolkit associated with the error.
    """

    def __init__(self, message="", toolkit=None, *args):
        if not message and toolkit:
            message = "could not import toolkit '{0}'".format(toolkit)
        self.toolkit = toolkit
        self.message = message
        if message:
            if toolkit:
                args = (toolkit,) + args
            args = (message,) + args
        self.args = args


class ETSConfigType:
    """
    Enthought Tool Suite configuration information.

    Instances of this class record state useful for ETS-using applications,
    including the current GUI toolkit in use, and data and home directory
    setttings.

    Users typically shouldn't make use of this class directly. Instead, use the
    module-level :data:`~.ETSConfig` instance of this class, which is shared
    between the various ETS packages.
    """
    # This class should not use ANY other package in the tool suite so that it
    # will always work no matter which other packages are present.

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    #### operator methods #####################################################

    def __init__(self):
        # Note that this constructor can only ever be called from within this
        # module, since we don't expose the class.

        # Shadow attributes for properties.
        self._application_data = None
        self._application_home = None
        self._company = None
        self._toolkit = None
        self._kiva_backend = None
        self._user_data = None

    ###########################################################################
    # 'ETSConfig' interface.
    ###########################################################################

    #### properties ###########################################################

    def get_application_data(self, create=False):
        """ Return the application data directory path.

            Parameters
            ----------
            create: bool
                Create the corresponding directory or not.

            Notes
            -----
            - This is a directory that applications and packages can safely
              write non-user accessible data to i.e. configuration
              information, preferences etc.

            - Do not put anything in here that the user might want to
              navigate to e.g. projects, user data files etc.

            - The actual location differs between operating systems.

        """
        if self._application_data is None:
            self._application_data = self._initialize_application_data(
                create=create
            )

        return self._application_data

    @property
    def application_data(self):
        """ Property getter, see get_application_data's docstring.
        """
        return self.get_application_data(create=True)

    @application_data.setter
    def application_data(self, application_data):
        """
        Property setter.

        """

        self._application_data = application_data

    @application_data.deleter
    def application_data(self):
        self._application_data = None

    def get_application_home(self, create=False):
        """ Return the application home directory path.

            Parameters
            ----------
            create: bool
                Create the corresponding directory or not.

            Note
            ----
            - This is a directory named after the current, running
              application that imported this module that applications and
              packages can safely write non-user accessible data to i.e.
              configuration information, preferences etc.  It is a
              sub-directory of self.application_data, named after the
              directory that contains the "main" python script that started
              the process.  For example, if application foo is started with
              a script named "run.py" in a directory named "foo", then the
              application home would be: <ETSConfig.application_data>/foo,
              regardless of if it was launched with "python
              <path_to_foo>/run.py" or "cd <path_to_foo>; python run.py"

            - This is useful for library modules used in apps that need to
              store state, preferences, etc. for the specific app only, and
              not for all apps which use that library module.  If the
              library module uses ETSConfig.application_home, they can
              store prefs for the app all in one place and do not need to
              know the details of where each app might reside.

            - Do not put anything in here that the user might want to
              navigate to e.g. projects, user home files etc.

            - The actual location differs between operating systems.

        """
        if self._application_home is None:
            self._application_home = os.path.join(
                self.get_application_data(create=create),
                self._get_application_dirname(),
            )

        return self._application_home

    @property
    def application_home(self):
        """ Property getter, see get_application_home's docstring.
        """
        return self.get_application_home(create=True)

    @application_home.setter
    def application_home(self, application_home):
        """
        Property setter.

        """

        self._application_home = application_home

    @application_home.deleter
    def application_home(self):
        self._application_home = None

    @property
    def company(self):
        """
        Property getter.

        """

        if self._company is None:
            self._company = self._initialize_company()

        return self._company

    @company.setter
    def company(self, company):
        """
        Property setter for the company name.

        """

        self._company = company

    @company.deleter
    def company(self):
        self._company = None

    @contextlib.contextmanager
    def provisional_toolkit(self, toolkit):
        """ Perform an operation with toolkit provisionally set

        This sets the toolkit attribute of the ETSConfig object to the
        provided value. If the operation fails with an exception, the toolkit
        is reset to nothing.

        This method should only be called if the toolkit is not currently set.

        Parameters
        ----------
        toolkit : string
            The name of the toolkit to provisionally use.

        Raises
        ------
        ETSToolkitError
            If the toolkit attribute is already set, then an ETSToolkitError
            will be raised when entering the context manager.
        """
        if self.toolkit:
            msg = "ETSConfig toolkit is already set to '{0}'"
            raise ETSToolkitError(msg.format(self.toolkit))
        self.toolkit = toolkit
        try:
            yield
        except:
            # reset the toolkit state
            self._toolkit = ""
            raise

    @property
    def toolkit(self):
        """
        Property getter for the GUI toolkit.  The value returned is, in order
        of preference: the value set by the application; the value specified by
        the 'ETS_TOOLKIT' environment variable; otherwise the empty string.

        """

        if self._toolkit is None:
            self._toolkit = self._initialize_toolkit()

        return self._toolkit.split(".")[0]

    @toolkit.setter
    def toolkit(self, toolkit):
        """
        Property setter for the GUI toolkit.  The toolkit can be set more than
        once, but only if it is the same one each time.  An application that is
        written for a particular toolkit can explicitly set it before any other
        module that gets the value is imported.

        """

        if self._toolkit and self._toolkit != toolkit:
            raise ValueError(
                "cannot set toolkit to %s because it has "
                "already been set to %s" % (toolkit, self._toolkit)
            )

        self._toolkit = toolkit

    @toolkit.deleter
    def toolkit(self):
        self._toolkit = None

    @property
    def enable_toolkit(self):
        """
        Deprecated: This property is no longer used.

        Property getter for the Enable backend.  The value returned is, in
        order of preference: the value set by the application; the value
        specified by the 'ENABLE_TOOLKIT' environment variable; otherwise the
        empty string.
        """
        from warnings import warn

        warn("Use of the enable_toolkit attribute is deprecated.")

        return self.toolkit

    @enable_toolkit.setter
    def enable_toolkit(self, toolkit):
        """
        Deprecated.

        Property setter for the Enable toolkit.  The toolkit can be set more
        than once, but only if it is the same one each time.  An application
        that is written for a particular toolkit can explicitly set it before
        any other module that gets the value is imported.
        """
        from warnings import warn

        warn("Use of the enable_toolkit attribute is deprecated.")

    @property
    def kiva_backend(self):
        """
        Property getter for the Kiva backend. The value returned is dependent
        on the value of the toolkit property. If toolkit specifies a kiva
        backend using the extended syntax: <enable toolkit>[.<kiva backend>]
        then the value of the property will be whatever was specified.
        Otherwise the value will be a reasonable default for the given enable
        backend.
        """
        if self._toolkit is None:
            raise AttributeError(
                "The kiva_backend attribute is dependent on toolkit, "
                "which has not been set."
            )

        if "." in self._toolkit:
            return self._toolkit.split(".")[1]
        elif self.toolkit == "wx" and sys.platform == "darwin":
            return "quartz"
        else:
            return "image"

    @property
    def user_data(self):
        """
        Property getter.

        This is a directory that users can safely write user accessible data
        to i.e. user-defined functions, edited functions, etc.

        The actual location differs between operating systems.

        """

        if self._user_data is None:
            self._user_data = self._initialize_user_data()

        return self._user_data

    @user_data.setter
    def user_data(self, user_data):
        """
        Property setter.

        """

        self._user_data = user_data

    @user_data.deleter
    def user_data(self):
        self._user_data = None

    #### private methods #####################################################

    # fixme: In future, these methods could allow the properties to be set
    # via the (as yet non-existent) preference/configuration mechanism. This
    # would allow configuration via (in order of precedence):-
    #
    # - a configuration file
    # - environment variables
    # - the command line

    def _get_application_dirname(self):
        """
        Return the name of the directory (not a path) that the "main"
        Python script which started this process resides in, or "" if it could
        not be determined or is not appropriate.

        For example, if the script that started the current process was named
        "run.py" in a directory named "foo", and was launched with "python
        run.py", the name "foo" would be returned (this assumes the directory
        name is the name of the app, which seems to be as good of an assumption
        as any).

        """

        dirname = ""

        main_mod = sys.modules.get("__main__", None)
        if main_mod is not None:
            if hasattr(main_mod, "__file__"):
                main_mod_file = os.path.abspath(main_mod.__file__)
                dirname = os.path.basename(os.path.dirname(main_mod_file))

        return dirname

    def _initialize_application_data(self, create=True):
        """
        Initializes the (default) application data directory.

        """

        if sys.platform == "win32":
            environment_variable = "APPDATA"
            directory_name = self.company

        else:
            environment_variable = "HOME"
            directory_name = "." + self.company.lower()

        # Lookup the environment variable.
        parent_directory = os.environ.get(environment_variable, None)
        if parent_directory is None or parent_directory == "/root":
            import tempfile
            from warnings import warn

            parent_directory = tempfile.gettempdir()
            user = os.environ.get("USER", None)
            if user is not None:
                directory_name += "_%s" % user
            warn(
                'Environment variable "%s" not set, '
                'setting home directory to %s'
                % (environment_variable, parent_directory)
            )

        application_data = os.path.join(parent_directory, directory_name)

        if create:
            # If a file already exists with this name then make sure that it is
            # a directory!
            if os.path.exists(application_data):
                if not os.path.isdir(application_data):
                    raise ValueError(
                        'File "%s" already exists' % application_data
                    )

            # Otherwise, create the directory.
            else:
                os.makedirs(application_data)

        return application_data

    def _initialize_company(self):
        """
        Initializes the (default) company.

        """

        return "Enthought"

    def _initialize_toolkit(self):
        """
        Initializes the toolkit.

        """
        if self._toolkit is not None:
            toolkit = self._toolkit
        else:
            toolkit = os.environ.get("ETS_TOOLKIT", "")

        return toolkit

    def _initialize_user_data(self):
        """
        Initializes the (default) user data directory.

        """

        # We check what the os.path.expanduser returns
        parent_directory = os.path.expanduser("~")
        directory_name = self.company

        if sys.platform == "win32":
            try:
                from win32com.shell import shell, shellcon

                # Due to the fact that the user's My Documents directory can
                # be in some pretty strange places, it's safest to just ask
                # Windows where it is.
                MY_DOCS = shellcon.CSIDL_PERSONAL
                parent_directory = shell.SHGetFolderPath(0, MY_DOCS, 0, 0)
            except ImportError:
                # But if they don't have pywin32 installed, just do it the
                # naive way...

                # Check if the usr_dir is C:\\John Doe\\Documents and Settings.
                # If yes, then we should modify the usr_dir to be
                # 'My Documents'. If no, then the user must have modified the
                # os.environ variables and the directory chosen is a desirable
                # one.
                desired_dir = os.path.join(parent_directory, "My Documents")

                if os.path.exists(desired_dir):
                    parent_directory = desired_dir

        else:
            directory_name = directory_name.lower()

        # The final directory.
        usr_dir = os.path.join(parent_directory, directory_name)

        # If a file already exists with this name then make sure that it is
        # a directory!
        if os.path.exists(usr_dir):
            if not os.path.isdir(usr_dir):
                raise ValueError('File "%s" already exists' % usr_dir)

        # Otherwise, create the directory.
        else:
            os.makedirs(usr_dir)

        return usr_dir


#: This single instance of :class:`~.ETSConfigType` is shared between the
#: various ETS packages, and used to store global state relevant to
#: ETS-using applications.
#:
#: See https://github.com/enthought/traits/discussions/1666 for a discussion
#: of writing tests that depend on :data:`~.ETSConfig` state.
ETSConfig = ETSConfigType()
