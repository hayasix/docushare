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

from . import dsclient
from .object import DSObject, DSContainer, register


__all__ = ("WikiPage", "Wiki")


@register
class WikiPage(DSObject):

    #typenum = dsclient.DSXITEMTYPE_WIKIPAGE  # is not valid.
    pass


@register
class Wiki(DSContainer):

    typenum = dsclient.DSXITEMTYPE_WIKI
    subobject_types = dsclient.DSCONTF_CHILDREN

    def add(self, title, **kw):
        """Add a WeblogEntry of Weblog.

        title       (unicode)
        Summary     (unicode)
        Description (unicode)
        """
        DSContainer.add(self, "WeblogEntry", Title=title, **kw)
