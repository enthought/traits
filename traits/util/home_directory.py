import os


def get_home_directory():
    """ Determine the user's home directory."""

    # 'HOME' should work on most Unixes, and 'USERPROFILE' works on at
    # least Windows XP ;^)
    #
    # FIXME: Is this really better than the following??
    #       path = os.path.expanduser('~')
    # The above seems to work on both Windows and Unixes though the docs
    # indicate it might not work as well on Macs.
    for name in ["HOME", "USERPROFILE"]:
        if name in os.environ:
            # Make sure that the path ends with a path separator.
            path = os.environ[name]
            if path[-1] != os.path.sep:
                path += os.path.sep

            break

    # If all else fails, the current directory will do.
    else:
        path = ""

    return path
