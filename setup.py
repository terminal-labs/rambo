import json
import os
import shutil
import urllib.request
from setuptools import setup, find_packages
from setuptools.command.egg_info import egg_info
from setuptools.command.develop import develop
from setuptools.command.install import install
from zipfile import ZipFile

def download_sample_states(command_subclass):
    """Customized setuptools command to download saltstack sample states
    dependencies from https://github.com/terminal-labs/sample-states
    """
    orig_run = command_subclass.run

    def modified_run(self):
        url = 'https://github.com/terminal-labs/sample-states/archive/basic.zip'
        filename = 'sample-states.zip'
        with urllib.request.urlopen(url) as response, open(
                filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        zipfile = filename
        with ZipFile(zipfile) as zf:
            zf.extractall()
        target = os.path.abspath('rambo/saltstack')
        if not os.path.exists(target):
            shutil.move(os.path.abspath('sample-states-basic/saltstack'), target)
        os.remove(filename)
        shutil.rmtree('sample-states-basic')
        orig_run(self)

    command_subclass.run = modified_run
    return command_subclass

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
    version='0.3.4.dev',
    description='Virtual Machines on Any Provider',
    url='https://github.com/terminal-labs/rambo',
    author='Terminal Labs',
    author_email='solutions@terminallabs.com',
    license=license,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click',
        'termcolor'
    ],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
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
