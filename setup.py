import json
from setuptools import setup, find_packages

setup(
    name='Rambo-vagrant',
    version='0.3.1',
    description='Virtual Machines on Any Provider',
    url='https://github.com/terminal-labs/rambo',
    author='Terminal Labs',
    author_email='solutions@terminallabs.com',
    license=license,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'bash',
        'click'
    ],
    entry_points='''
        [console_scripts]
        rambo=rambo.cli:main
     '''
)
