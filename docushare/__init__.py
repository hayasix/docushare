#!/usr/bin/env python2.7
# vim: fileencoding=cp932 fileformat=dos

"""DochShare Client Package

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""


__author__ = "HAYASI Hideki"
__copyright__ = "Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>"
__license__ = "ZPL 2.1"
__version__ = "0.4.1"
__email__ = "linxs@linxs.org"
__status__ = "Development"


from .client import Client
from .server import Server
from .user import User
from .group import Group
from .file import Version, File  # synonym = document.Document
from .collection import Collection
from .bulletinboard import Bulletin, BulletinBoard
from .weblog import WeblogEntry, Weblog
from .wiki import WikiPage, Wiki
