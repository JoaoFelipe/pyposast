#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = "Extends Python ast nodes with positional informations"

setup(
    name="PyPosAST",
    version="1.2.0",
    description="Extends Python ast nodes with positional informations",
    long_description=long_description,
    packages=find_packages(exclude=["tests_*", "tests"]),
    author=("Joao Pimentel",),
    author_email="joaofelipenp@gmail.com",
    license="MIT",
    keywords="ast python position offset",
    url="https://github.com/JoaoFelipe/PyPosAST",
)
