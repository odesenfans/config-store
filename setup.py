import setuptools

from conflex import __version__ as module_version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conflex",
    version=module_version,
    author="Olivier Desenfans",
    author_email="desenfans.olivier@gmail.com",
    description="A flexible config store library that supports any configuration format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/odesenfans/conflex.git",
    install_requires=["pyyaml>=5.0.0"],
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent",],
    python_requires=">=3.7",
)
