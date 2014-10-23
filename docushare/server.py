#!/usr/bin/env python2.7
# vim: fileencoding=cp932 fileformat=dos

"""server  -  DochShare Server, or root folder

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import win32com.client

from . import dsclient
from .error import try_
from .object import DSContainer, getclass, register


__all__ = ("Server",)


SEARCH_FLAGS = dict(
        DisplayName=dsclient.DSSRCH_BY_TITLE,
        FileName=dsclient.DSSRCH_BY_FILENAME,
        FileType=dsclient.DSSRCH_BY_MIMETYPE,
        Content=dsclient.DSSRCH_BY_CONTENT,
        Keywords=dsclient.DSSRCH_BY_KEYWORD,
        Owner=dsclient.DSSRCH_BY_OWNER,
        CreatedTimeFrom=dsclient.DSSRCH_BY_CREATTIME,
        CreatedTimeTo=dsclient.DSSRCH_BY_CREATTIME,
        ModifiedTimeFrom=dsclient.DSSRCH_BY_MODIFTIME,
        ModifiedTimeTo=dsclient.DSSRCH_BY_MODIFTIME,
        )
SEARCH_SETS = dict(
        Summary=dsclient.DSSRCH_AS_SUMMARY,
        Description=dsclient.DSSRCH_AS_DESCRIPTN,
        Author=dsclient.DSSRCH_AS_AUTHOR,
        LastUser=dsclient.DSSRCH_AS_LASTUSER,
        )
SELECTION_TYPES = dict(
        File=dsclient.DSSRCH_TYPE_FILE,
        Collection=dsclient.DSSRCH_TYPE_COLL,
        Calendar=dsclient.DSSRCH_TYPE_CALNDR,
        BulletinBoard=dsclient.DSSRCH_TYPE_BBOARD,
        User=dsclient.DSSRCH_TYPE_USER,
        Group=dsclient.DSSRCH_TYPE_GROUP,
        )


@register
class Server(DSContainer):
    """DocuShare Server, or root folder"""

    typenum = dsclient.DSXITEMTYPE_SERVER
    subobject_types = dsclient.DSCONTF_CHILDREN

    def __init__(self, servermap):
        DSContainer.__init__(self, servermap.CreateObject("Server"))
        self._ds = servermap

    def __call__(self, handle, load=True):
        obj = self.CreateObject(handle)
        cls = obj.Type
        try:
            if obj.VersionNum:
                cls = "Version"
        except AttributeError:
            pass
        obj = getclass(cls)(obj)
        if load:
            obj.load()
        return obj

    @property
    def search_properties(self):
        """Returns all property names for search criteria."""
        return sorted(SEARCH_FLAGS.keys() + SEARCH_SETS.keys())

    def search(self, types=None, root=None, mode="OR", maxitems=100, xml=None, **kw):
        gw = self._ds.Open()
        flags = 0
        data = ""
        for type in types or []:
            if type in SELECTION_TYPES:
                flags |= SELECTION_TYPES[type]
            else:
                flags |= dsclient.DSSRCH_AS_TYPE
                data = type
        if root is not None:
            flags |= dsclient.DSSRCH_SCOPE_COLL
            if not isinstance(root, (basestring, int, long, float)):
                root = root.Handle
            if isinstance(root, basestring) and root.startswith("Collection-"):
                    root = root[len("Collection-"):]
            gw.DSCollHandle = int(root)
        mode = mode.upper()
        if mode == "AND":
            flags |= dsclient.DSSRCH_OP_CONJUNCT_AND
        if mode == "NOT":
            flags |= dsclient.DSSRCH_OP_NEGATE
        gw.DSMaxItems = maxitems
        for k, v in kw.items():
            if k in SEARCH_FLAGS:
                flags |= SEARCH_FLAGS[k]
                setattr(gw, "DS" + k, v)
            elif k in SEARCH_SETS:
                flags |= SEARCH_SETS[k]
                data = v
            else:
                flags |= dsclient.DSSRCH_AS_CUSTOM
                gw.DSItemProp = k
                data = v
        if xml:
            flags |= dsclient.DSSRCH_ALREADY_XML
            if "%1" in xml or "%2" in xml or "%3" in xml:
                flags |= dsclient.DSSRCH_USE_TEMPLATE
            data = xml
        try_(gw.Search(flags, data))
        chain = win32com.client.Dispatch("DSITEMENUMLib.EnumObj")
        try_(chain.Load(dsclient.DSCONTF_SEARCHRESULTS, gw.DSItemListFile))
        chain.Reset()
        while chain.NextPos:
            obj = chain.NextItem
            obj = getclass(obj.TypeNum)(self.CreateObject(obj.Handle))
            obj.DSLoadProps()
            yield obj
