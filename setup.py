import json
from setuptools import setup, find_packages

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
        'click'
    ],
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
