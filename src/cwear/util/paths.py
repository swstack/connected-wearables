import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

import pkg_resources
import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def project_root():
    return os.path.abspath(os.path.join(THIS_DIR, "..", "..", ".."))


def env():
    return os.path.join(project_root(), ".env")


def webif_static():
    return pkg_resources.resource_filename("cwear.webif", "static")


def webif_templates():
    return pkg_resources.resource_filename("cwear.webif", "templates")


def project_tmp():
    return os.path.join(env(), "tmp")


def init_dirs(path):
    """Helper function to make the directories in `path` if they don't exist

    Path should only consist of directories, to avoid making a directory with
    a filename extension, but we will put in place checks against this.
    """
    if not os.path.exists(path):  # path doesn't exist, safe to proceed
        # make sure the path doesn't look file-like
        end_of_path = os.path.split(path)[-1]
        if ("." in end_of_path) and (not end_of_path.startswith(".")):
            dirs, filename = os.path.split(path)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
        else:
            os.makedirs(path)
