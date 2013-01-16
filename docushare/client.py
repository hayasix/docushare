#!/usr/bin/env python2.6
# vim: fileencoding=cp932 fileformat=dos

"""client  -  DochShare Client

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import win32com.client

from .dsclient import *
from .error import try_
from .object import DSObject, getclass
from .server import Server


__all__ = ("Client",)


SEARCH_FLAGS = dict(
        DisplayName=DSSRCH_BY_TITLE,
        FileName=DSSRCH_BY_FILENAME,
        FileType=DSSRCH_BY_MIMETYPE,
        Content=DSSRCH_BY_CONTENT,
        Keywords=DSSRCH_BY_KEYWORD,
        Owner=DSSRCH_BY_OWNER,
        CreatedTimeFrom=DSSRCH_BY_CREATTIME,
        CreatedTimeTo=DSSRCH_BY_CREATTIME,
        ModifiedTimeFrom=DSSRCH_BY_MODIFTIME,
        ModifiedTimeTo=DSSRCH_BY_MODIFTIME,
        )
SEARCH_SETS = dict(
        Summary=DSSRCH_AS_SUMMARY,
        Description=DSSRCH_AS_DESCRIPTN,
        Author=DSSRCH_AS_AUTHOR,
        LastUser=DSSRCH_AS_LASTUSER,
        )
SELECTION_TYPES = dict(
        File=DSSRCH_TYPE_FILE,
        Collection=DSSRCH_TYPE_COLL,
        Calendar=DSSRCH_TYPE_CALNDR,
        BulletinBoard=DSSRCH_TYPE_BBOARD,
        User=DSSRCH_TYPE_USER,
        Group=DSSRCH_TYPE_GROUP,
        )


class Client(object):
    """DocuShare Client"""

    def __init__(self, address=None, proxy=None, name="DocuShare"):
        """Initiator"""
        ds = win32com.client.Dispatch("DSServerMap.Server")
        ds.DocuShareAddress = address
        if proxy:
            ds.UseProxy = True
            ds.ProxyAddress = proxy
        ds.Name = name
        self._ds = ds

    def connect(self, username, password, domain="DocuShare"):
        ds = self._ds
        ds.UserName = username
        ds.Password = password
        ds.Domain = domain
        server = Server(ds.CreateObject("Server"))
        iter(server).next()  # Login actually.
        self.connected = True
        return server

    @property
    def search_properties(self):
        """Returns all property names for search criteria."""
        return sorted(SEARCH_FLAGS.keys() + SEARCH_SETS.keys())

    def search(self, types=None, root=None, mode="OR", maxitems=100, xml=None, **kw):
        self._gw = DSObject(self._ds.Open())
        flags = 0
        data = ""
        for type in types or []:
            if type in SELECTION_TYPES:
                flags |= SELECTION_TYPES[type]
            else:
                flags |= DSSRCH_AS_TYPE
                data = type
        if root is not None:
            flags |= DSSRCH_SCOPE_COLL
            if isinstance(root, basestring) and root.startswith("Collection-"):
                root = root[len("Collection-"):]
            self._gw.DSCollHandle = int(root)
        mode = mode.upper()
        if mode == "AND":
            flags |= DSSRCH_OP_CONJUNCT_AND
        if mode == "NOT":
            flags |= DSSRCH_OP_NEGATE
        self._gw.DSMaxItems = maxitems
        for k, v in kw.items():
            if k in SEARCH_FLAGS:
                flags |= SEARCH_FLAGS[k]
                setattr(self._gw, "DS" + k, v)
            elif k in SEARCH_SETS:
                flags |= SEARCH_SETS[k]
                data = v
            else:
                flags |= DSSRCH_AS_CUSTOM
                self._gw.DSItemProp = k
                data = v
        if xml:
            flags |= DSSRCH_ALREADY_XML
            if "%1" in xml or "%2" in xml or "%3" in xml:
                flags |= DSSRCH_USE_TEMPLATE
            data = xml
        try_(self._gw.Search(flags, data))
        chain = win32com.client.Dispatch("DSITEMENUMLib.EnumObj")
        try_(chain.Load(DSCONTF_SEARCHRESULTS, self._gw.DSItemListFile))
        chain.Reset()
        while chain.NextPos:
            obj = chain.NextItem
            yield getclass(obj.TypeNum)(obj)
