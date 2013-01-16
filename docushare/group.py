#!/usr/bin/env python2.6
# vim: fileencoding=cp932 fileformat=dos

"""group  -  DochShare Group

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from . import dsclient
from .object import DSObject, register


__all__ = ("Group",)


@register
class Group(DSObject):

    typenum = dsclient.DSXITEMTYPE_GROUP
    subobject_types = dsclient.DSCONTF_CHILDREN
