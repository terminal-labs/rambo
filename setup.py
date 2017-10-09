import json
from setuptools import setup, find_packages

setup(
    name='rambo-vagrant',
    version='0.2.2.dev',
    description='rambo',
    url='https://github.com/terminal-labs/rambo',
    author='Terminal Labs',
    author_email='solutions@terminallabs.com',
    license=license,
    packages=find_packages(),
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
