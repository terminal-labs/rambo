# Before anything else, bail if not Python3
import sys
if sys.version_info < (3, 6, 0):
    sys.exit('Python 3.6+ required but lower version found. Aborted.')

import json
import os
import re
import shutil
import urllib.request
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist
from setuptools.command.egg_info import egg_info
from setuptools.command.develop import develop
from setuptools.command.install import install
from zipfile import ZipFile

import rambo

here = os.path.abspath(os.path.dirname(__file__))


def download_sample_states(command_subclass):
    """Customized setuptools command to download saltstack sample states
    dependencies from https://github.com/terminal-labs/sample-states

    This is ran anytime this project is installed or (sdist) uploaded.

    If ran during an upload, this will prompt to get a fresh copy
    of the sample-states.
    """
    orig_run = command_subclass.run

    def modified_run(self):
        target = os.path.abspath("rambo/saltstack")
        yes = {"yes", "y", "ye", ""}
        no = {"no", "n"}

        # Special Case of sdist (upload)
        if type(self).__name__ == "CustomSdistCommand":
            if os.path.exists(target):
                choice = input(
                    f"{target} exists. Delete and redownload before running sdist? "
                    "(Y/n): "
                ).lower()
                if choice in yes:
                    shutil.rmtree(target)  # Delete.
                elif choice in no:
                    pass  # Don't delete.
                else:
                    print("Please respond with 'yes' or 'no'")
            else:
                print(
                    f"{target} did not yet exist, so we must download it for packaging."
                )

        # Download states and copy if we need to.
        if not os.path.exists(
            target
        ):  # Do not overwrite existing saltstack dir. Installs don't delete!
            url = "https://github.com/terminal-labs/sample-states/archive/rambo.zip"
            filename = "sample-states.zip"
            with urllib.request.urlopen(url) as response, open(
                filename, "wb"
            ) as out_file:
                shutil.copyfileobj(response, out_file)
            zipfile = filename
            with ZipFile(zipfile) as zf:
                zf.extractall()
            shutil.move(os.path.abspath("sample-states-basic/saltstack"), target)
            os.remove(filename)
            shutil.rmtree("sample-states-basic")
        orig_run(self)

    command_subclass.run = modified_run
    return command_subclass


@download_sample_states
class CustomSdistCommand(sdist):
    pass


@download_sample_states
class CustomEggInfoCommand(egg_info):
    pass


@download_sample_states
class CustomDevelopCommand(develop):
    pass


@download_sample_states
class CustomInstallCommand(install):
    pass


install_requires = ["click"]
docs_require = [
    "recommonmark",  # Higher versions break relative paths in links.
    "sphinx-markdown-tables",
    "sphinx_rtd_theme",
]
dev_require = docs_require + ["black", "ipdb"]

setup(
    author="Terminal Labs",
    author_email="solutions@terminallabs.com",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
        "egg_info": CustomEggInfoCommand,
        "sdist": CustomSdistCommand,
    },
    description=rambo.__description__,
    entry_points="""
        [console_scripts]
        rambo=rambo.cli:main
     """,
    extras_require={"dev": dev_require, "docs": docs_require},
    include_package_data=True,
    install_requires=install_requires,
    license=license,
    name="Rambo-vagrant",
    packages=find_packages(),
    url="https://github.com/terminal-labs/rambo",
    version=rambo.__version__,
    zip_safe=False,
)
