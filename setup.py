"""
Setup script for Dream.OS Backtesting Framework.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dreamos",
    version="0.1.0",
    author="Dream.OS Team",
    author_email="team@dreamos.ai",
    description="A powerful and flexible backtesting framework for testing trading strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dreamos/backtesting",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest>=8.0.0",
        "pytest-asyncio>=0.23.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.12.0",
        "pytest-xdist>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "dreamos-backtest=dreamos.backtesting.cli:main",
        ],
    },
) 