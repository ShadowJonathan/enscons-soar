"""
Utilities otherwise provided by pkg_resources or wheel
"""

import re
from packaging.requirements import Requirement
import os.path
import toml


def get_build_from() -> "str | None":

    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as pyproject:
            project = toml.load(pyproject)

        if "tool" in project:
            tools = project["tool"]

            if "enscons" in tools:
                enscons = tools["enscons"]

                if "build-from" in enscons:
                    return os.path.abspath(enscons["build-from"])


def safe_name(name):
    """Convert an arbitrary string to a standard distribution name

    Any runs of non-alphanumeric/. characters are replaced with a single '-'.
    """
    return re.sub('[^A-Za-z0-9.]+', '-', name)


def safe_extra(extra):
    """Convert an arbitrary string to a standard 'extra' name

    Any runs of non-alphanumeric characters are replaced with a single '_',
    and the result is always lowercased.
    """
    return re.sub('[^A-Za-z0-9.-]+', '_', extra).lower()


def to_filename(name):
    """Convert a project or version name to its filename-escaped form

    Any '-' characters are currently replaced with '_'.
    """
    return name.replace('-', '_')


# from wheel
def requires_to_requires_dist(requirement):
    """Return the version specifier for a requirement in PEP 345/566 fashion."""
    if getattr(requirement, "url", None):
        return " @ " + requirement.url

    requires_dist = []
    for op, ver in requirement.specs:
        requires_dist.append(op + ver)
    if not requires_dist:
        return ""
    return " (%s)" % ",".join(sorted(requires_dist))


def generate_requirements(extras_require):
    """
    Convert requirements from a setup()-style dictionary to ('Requires-Dist', 'requirement')
    and ('Provides-Extra', 'extra') tuples.

    extras_require is a dictionary of {extra: [requirements]} as passed to setup(),
    using the empty extra {'': [requirements]} to hold install_requires.
    """
    for extra, depends in extras_require.items():
        condition = ""
        extra = extra or ""
        if ":" in extra:  # setuptools extra:condition syntax
            extra, condition = extra.split(":", 1)

        extra = safe_extra(extra)
        if extra:
            yield "Provides-Extra", extra
            if condition:
                condition = "(" + condition + ") and "
            condition += "extra == '%s'" % extra

        for dependency in depends:
            new_req = Requirement(dependency)
            if condition:
                if new_req.marker:
                    new_req.marker = "(%s) and %s" % (new_req.marker, condition)
                else:
                    new_req.marker = condition
            yield "Requires-Dist", str(new_req)
