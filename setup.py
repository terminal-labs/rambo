import io
import sys

from setuptools import find_packages
from setuptools import setup

if sys.version_info < (3, 6, 0):
    sys.exit("Python 3.6+ required but lower version found. Aborted.")

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

install_requires = ["click"]
docs_require = [
    "recommonmark",
    "sphinx_rtd_theme",
]
dev_require = docs_require + ["black", "ipdb", "pre-commit"]

setup(
    author="Terminal Labs",
    author_email="solutions@terminallabs.com",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="A Provider Agnostic Provioning Framework",
    entry_points="""
        [console_scripts]
        rambo=rambo.cli:main
     """,
    extras_require={"dev": dev_require, "docs": docs_require},
    include_package_data=True,
    install_requires=install_requires,
    license=license,
    long_description=readme,
    long_description_content_type="text/markdown",
    name="Rambo-vagrant",
    packages=find_packages(),
    url="https://github.com/terminal-labs/rambo",
    version="0.4.5.dev",
    zip_safe=False,
)
