import io

from setuptools import find_packages
from setuptools import setup

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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="A Provider Agnostic Provioning Framework",
    entry_points="""
        [console_scripts]
        rambo=rambo.cli:main
     """,
    extras_require={"dev": dev_require, "docs": docs_require},
    include_package_data=True,
    install_requires=install_requires,
    license='BSD-3-Clause',
    long_description=readme,
    long_description_content_type="text/markdown",
    name="Rambo-vagrant",
    packages=find_packages(),
    url="https://github.com/terminal-labs/rambo",
    version="0.4.5.dev0",
    zip_safe=False,
)
