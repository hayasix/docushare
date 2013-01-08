#!/usr/bin/env python2.6
# vim: fileencoding=cp932 fileformat=dos

"""wiki  -  DochShare Wiki object

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from .object import DSObject, register
from .collection import Collection


__all__ = ("WikiPage", "Wiki")


@register
class WikiPage(DSObject):
    pass


@register
class Wiki(Collection):
    pass
