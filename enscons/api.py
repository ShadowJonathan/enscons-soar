"""
PEP 517 interface to enscons.

To be invoked by a future version of pip.

May not be possible to invoke more than one function without reloading Python.
"""

import os.path
import sys
import SCons.Script.Main

from .util import get_build_from


# optional hooks
#
# def get_build_wheel_requires(settings):
#     return []
#
# def get_build_sdist_requires(settings):
#     return []


def _run(alias):
    build_from = get_build_from()
    if build_from is not None:
        print(f"Changing directory to {build_from} to position SCons")
        os.chdir(build_from)
    else:
        print("Not changing directory")

    try:
        SCons.Script.Main.main()
    except SystemExit as e:
        if e.code != 0:
            raise Exception("scons exited non-0: " + str(e))

    # extreme non-api:
    lookup = SCons.Node.arg2nodes_lookups[0](alias)
    if lookup is None:
        raise Exception("build failed")
    sources = lookup.sources[0]
    return os.path.basename(str(sources))


def pyproject_arg() -> str:
    return "--pyproject-dir=" + os.path.abspath(".")


def prepare_metadata_for_build_wheel(metadata_directory, settings):
    sys.argv[1:] = [pyproject_arg(), "--wheel-dir=" + metadata_directory, "dist_info"]
    return _run("dist_info")


def build_wheel(wheel_directory, settings, metadata_directory=None):
    sys.argv[1:] = [pyproject_arg(), "--wheel-dir=" + wheel_directory, "bdist_wheel"]
    return _run("bdist_wheel")


def build_sdist(sdist_directory, settings):
    sys.argv[1:] = [pyproject_arg(), "--dist-dir=" + sdist_directory, "sdist"]
    return _run("sdist")


# PEP 660 editable installation
def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    sys.argv[1:] = [pyproject_arg(), "--wheel-dir=" + wheel_directory, "editable"]
    return _run("editable")
