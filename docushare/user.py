#!/usr/bin/env python2.7
# vim: fileencoding=cp932 fileformat=dos

"""user  -  DochShare User

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from . import dsclient
from .object import DSObject, register, customproperty


__all__ = ("User",)


@register
class User(DSObject):

    typenum = dsclient.DSXITEMTYPE_USER

    FirstName = customproperty("first_name")
    LastName = customproperty("last_name")
    Email = customproperty("email")
    MailStop = customproperty("mailstop")
    Phone = customproperty("phone")
    Password = customproperty("password")
    LastLogin = customproperty("last_login")
    Homepage = customproperty("homepage")

    UseUploadHelper = customproperty(
            "use_upload_helper", dsclient.DSAXES_PROPTYPE_MENU)
