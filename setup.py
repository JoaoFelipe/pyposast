#!/usr/bin/env python
import subprocess
import sys
from setuptools import setup, find_packages

def get_version():
    """Use git describe to get version from tag"""
    proc = subprocess.Popen(
        ("git", "describe", "--tag", "--always"), 
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output, _ = proc.communicate()
    result = output.decode("utf-8").strip()
    if proc.returncode != 0:
        sys.stderr.write(
            ">>> Git Describe Error:\n    " +
            result
        )
        return "1+unknown"
    split = result.split("-", 1)
    version = "+".join(split).replace("-", ".")

    if len(split) > 1:
        sys.stderr.write(
            ">>> Please verify the commit tag:\n    " +
            version + "\n"
        )
    return version

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    sys.stderr.write(
        ">>> Please verify the pypandoc installation.\n"
    )
    long_description = "Extends Python ast nodes with positional informations"

setup(
    name="PyPosAST",
    version=get_version(),
    description="Extends Python ast nodes with positional informations",
    long_description=long_description,
    packages=find_packages(exclude=["tests_*", "tests"]),
    author=("Joao Pimentel",),
    author_email="joaofelipenp@gmail.com",
    license="MIT",
    keywords="ast python position offset",
    url="https://github.com/JoaoFelipe/PyPosAST",
)
