import os
import sys
import warnings

# Hack to silence atexit traceback in some Python versions
try:
    import multiprocessing  # noqa: F401
except ImportError:
    pass

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension


class custom_build_ext(build_ext):
    """Allow C extension building to fail.

    The C extension speeds up BSON encoding, but is not essential.
    """

    warning_message = """
********************************************************************
WARNING: %s could not
be compiled. No C extensions are essential for BSON to run,
although they do result in significant speed improvements.
%s
********************************************************************
"""

    def run(self):
        try:
            build_ext.run(self)
        except Exception:
            if "TOX_ENV_NAME" in os.environ:
                raise
            e = sys.exc_info()[1]
            sys.stdout.write("%s\n" % str(e))
            warnings.warn(
                self.warning_message
                % (
                    "Extension modules",
                    "There was an issue with your platform configuration - see above.",
                )
            )

    def build_extension(self, ext):
        name = ext.name
        try:
            build_ext.build_extension(self, ext)
        except Exception:
            if "TOX_ENV_NAME" in os.environ:
                raise
            e = sys.exc_info()[1]
            sys.stdout.write("%s\n" % str(e))
            warnings.warn(
                self.warning_message
                % (
                    "The %s extension module" % (name,),
                    "The output above this warning shows how the compilation failed.",
                )
            )


ext_modules = [
    Extension(
        "bson._cbson",
        include_dirs=["bson"],
        sources=["bson/_cbsonmodule.c", "bson/time64.c", "bson/buffer.c"],
    ),
]


if "--no_ext" in sys.argv or os.environ.get("NO_EXT"):
    sys.argv.remove("--no_ext")
    ext_modules = []
elif sys.platform.startswith("java") or sys.platform == "cli" or "PyPy" in sys.version:
    sys.stdout.write(
        """
*****************************************************\n
The optional C extensions are currently not supported\n
by this python implementation.\n
*****************************************************\n
"""
    )
    ext_modules = []

setup(name="bson-py", cmdclass={"build_ext": custom_build_ext}, ext_modules=ext_modules)  # type:ignore
