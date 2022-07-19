#!/usr/bin/env python3

from setuptools import setup

long_description = ""

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="up_aries",
    version="0.0.2",
    description="Aries is a project aimed at exploring constraint-based techniques for automated planning and scheduling. \
        It relies on an original implementation of constraint solver with optional variables and clause learning to which \
        various automated planning problems can be submitted.",
    author="CNRS-LAAS",
    author_email="abitmonnot@laas.fr",
    packages=["up_aries"],
    url="https://github.com/plaans/aries",  # TODO: Add documentation URL if any
    license="MIT",
)
