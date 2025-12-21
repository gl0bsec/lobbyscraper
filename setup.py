#!/usr/bin/env python3
"""
Setup script for EU Lobbyscraper package
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from package
version = {}
version_file = Path(__file__).parent / "eu_lobbyscraper" / "__init__.py"
with open(version_file, encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="eu-lobbyscraper",
    version=version.get("__version__", "1.0.0"),
    description="Download and convert public consultation feedback from EU Better Regulation Portal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="EU Lobbyscraper Contributors",
    author_email="",
    url="https://github.com/yourusername/eu-lobbyscraper",
    license="MIT",
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "eu-lobbyscraper-download=eu_lobbyscraper.cli:download_cli",
            "eu-lobbyscraper-convert=eu_lobbyscraper.cli:convert_cli",
            "eu-lobbyscraper-batch-convert=eu_lobbyscraper.cli:batch_convert_cli",
            "eu-lobbyscraper-list=eu_lobbyscraper.cli:list_cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="eu european-union lobbying consultation feedback scraper pandoc markdown",
    project_urls={
        "Documentation": "https://github.com/yourusername/eu-lobbyscraper",
        "Source": "https://github.com/yourusername/eu-lobbyscraper",
        "Tracker": "https://github.com/yourusername/eu-lobbyscraper/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
