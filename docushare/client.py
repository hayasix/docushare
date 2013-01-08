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

from .server import Server


__all__ = ("Client",)


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
        server = ds.CreateObject("Server")
        self.connected = True
        return Server(server)
