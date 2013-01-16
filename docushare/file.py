#!/usr/bin/env python2.6
# vim: fileencoding=cp932 fileformat=dos

"""file  -  DochShare File object

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


__all__ = ("Version", "File")


@register
class Version(DSObject):
    """DocuShare File Version"""

    pass


@register
class File(DSContainer):
    """DocuShare File"""

    subobject_types = dsclient.DSCONTF_VERSIONS

    def checkout(self, path=None, lock=True):
        """Lock file and download it.

        path        (str) pathname of downloaded file

        Returns the actual pathname of downloaded file.
        """
        if path:
            self.Name = path
        self.DSDownload(dsclient.DSAXES_FLAG_DOWNLOADLOCKED)
        return self.Name

    def update(self, path=None):
        """Update the file of DocuShare File object.

        path        (str) pathname to upload file
        """
        self.DSUpload()
