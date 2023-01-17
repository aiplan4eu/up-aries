#!/usr/bin/env python3
import os
import platform

from setuptools import find_packages, setup

# Based on platform, build the appropriate wheel with the binary extension.
arch = (platform.system(), platform.machine())

# TODO: Implement a better way to determine the correct binary.
EXECUTABLES = {
    ("Linux", "x86_64"): "bins/aries_linux_amd64",
    ("Linux", "aarch64"): "bins/aries_linux_aarch64",
    ("Darwin", "x86_64"): "bins/aries_macos_x86_64",
    ("Darwin", "aarch64"): "bins/aries_macos_aarch64",
    ("Darwin", "arm64"): "bins/aries_macos_aarch64",
    ("Windows", "AMD64"): "bins/aries_windows_amd64.exe",
    ("Windows", "aarch64"): "bins/aries_windows_aarch64.exe",
    # ("Windows", "x86"): "aries_windows_x86.exe",
    # ("Windows", "aarch32"): "aries_windows_aarch32.exe",
}

executable = EXECUTABLES[arch]

# Update permissions on the binary.
os.chmod(os.path.realpath(os.path.join(os.path.dirname(__file__), "up_aries", executable)), 0o755)

long_description = ""

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="up_aries",
    version="0.0.2",
    description="Aries is a project aimed at exploring constraint-based techniques for automated planning and scheduling. \
        It relies on an original implementation of constraint solver with optional variables and clause learning to which \
        various automated planning problems can be submitted.",
    author="CNRS-LAAS",
    author_email="abitmonnot@laas.fr",
    install_requires=["unified_planning", "grpcio", "grpcio-tools", "pytest"],
    packages=find_packages(include=["up_aries", "up_aries.*"]),
    package_data={"": [executable]},
    include_package_data=True,
    url="https://github.com/plaans/aries",
    license="MIT",
)
