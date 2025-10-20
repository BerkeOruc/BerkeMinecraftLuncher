#!/usr/bin/env python3
"""
Berke Minecraft Launcher - Enhanced Setup Script
"""

from setuptools import setup, find_packages
import os

# Read version from version.py
with open("version.py", "r") as f:
    exec(f.read())

# Read README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="berke-minecraft-launcher",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Advanced Minecraft launcher with keyboard navigation, mod support, skin management, and performance monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    license=__license__,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["i18n", "version"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Games/Entertainment",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "berke-minecraft-launcher=berkemc.core.launcher:main",
            "berkemc=berkemc.core.launcher:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="minecraft launcher mod skin management performance monitoring",
    project_urls={
        "Bug Reports": "https://github.com/BerkeOruc/BerkeMinecraftLuncher/issues",
        "Source": "https://github.com/BerkeOruc/BerkeMinecraftLuncher",
        "Documentation": "https://github.com/BerkeOruc/BerkeMinecraftLuncher#readme",
    },
)
