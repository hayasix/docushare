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

        **kw        (dict) attributes to create object

        Returns the created WeblogEntry.

        Each **kw key is a DocuShare object attribute name, e.g. 'Title' or
        'MimeType'.  Note that such attribute names should be capitalized.
        For example, object.Title, object.MimeType and object.Mimetype are
        valid Docushare object attributes.  object.title is a normal Python
        object attribute and may cause AttributeError.
        """
        DSContainer.add(self, type="WeblogEntry", **kw)
