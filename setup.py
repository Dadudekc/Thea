from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="digital-dreamscape",
    version="1.0.0",
    author="Dream.OS Team",
    author_email="maintainers@example.com",
    description="A standalone extraction of working components from Dream.OS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dreamos/digital-dreamscape-standalone",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-qt>=4.4.0",
            "black>=24.0.0",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dreamscape=digital_dreamscape.gui.main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "digital_dreamscape": ["templates/*", "styles/*"],
    },
) 