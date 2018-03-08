# Before anything else, bail if not Python3
import sys
if sys.version_info.major < 3:
    sys.exit('Python 3 required but lower version found. Aborted.')

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
        target = os.path.abspath('rambo/saltstack')
        yes = {'yes','y', 'ye', ''}
        no = {'no','n'}

        ## Special Case of sdist (upload)
        if type(self).__name__ == 'CustomSdistCommand':
            if os.path.exists(target):
                choice = input('%s exists. Delete and redownload before running sdist? (Y/n): ' % target).lower()
                if choice in yes:
                    shutil.rmtree(target) # Delete.
                elif choice in no:
                    pass # Don't delete.
                else:
                    print("Please respond with 'yes' or 'no'")
            else:
                print('%s did not yet exist, so we must download it for packaging.' % target)

        ## Download states and copy if we need to.
        if not os.path.exists(target): # Do not overwrite existing saltstack dir. Installs don't delete!
            url = 'https://github.com/terminal-labs/sample-states/archive/basic.zip'
            filename = 'sample-states.zip'
            with urllib.request.urlopen(url) as response, open(
                    filename, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            zipfile = filename
            with ZipFile(zipfile) as zf:
                zf.extractall()
            shutil.move(os.path.abspath('sample-states-basic/saltstack'), target)
            os.remove(filename)
            shutil.rmtree('sample-states-basic')
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

setup(
    name='Rambo-vagrant',
    version=rambo.__version__,
    description=rambo.__description__,
    url='https://github.com/terminal-labs/rambo',
    author='Terminal Labs',
    author_email='solutions@terminallabs.com',
    license=license,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click',
        'click-configfile<=1',
        'sphinx_rtd_theme',
    ],
    dependency_links=[
        'https://github.com/terminal-labs/click-configfile/archive/merge-with-primary-schema.zip#egg=click-configfile-1',
    ],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
        'sdist': CustomSdistCommand,
    },
    classifiers = [
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
    ],
    entry_points='''
        [console_scripts]
        rambo=rambo.cli:main
     '''
)
