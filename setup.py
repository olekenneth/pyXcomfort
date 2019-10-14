from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyxcomfort",
    version="1.0.0",
    description="Python library for controlling Moeller Eaton Xcomfort lights.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olekenneth/pyxcomfort",
    author="Ole-Kenneth Bratholt",
    author_email="ok@rait.no",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="xcomfort lights smart house automation home assistant",
    packages=["xcomfort"],
    install_requires=["pyserial", "pycrc"],
    python_requires=">=3",
    project_urls={
        "Bug Reports": "https://github.com/olekenneth/pyxcomfort/issues",
        "Source": "https://github.com/olekenneth/pyxcomfort/",
    },
)
