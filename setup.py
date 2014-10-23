#!/usr/bin/env python2.7
# vim: fileencoding=utf-8

from distutils.core import setup

from docushare.__init__ import \
        __author__, __copyright__, __license__, __version__, __email__


setup(
    name="docushare",
    version=__version__,
    author=__author__,
    author_email=__email__,
    url="http://launchpad.net/docushare",
    description="A DocuShare Client Library.",
    long_description="""`docushare' is a client library for DocuShare by Xerox Corporation.""",
    license=__license__,
    platforms=["win32",],
    packages=["docushare",],
    package_data={"docushare": ["*.csv",]},
    zipfile="docushare.zip",
    )
