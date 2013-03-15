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
from .server import Server
from .error import try_


__all__ = ("Version", "File")


@register
class Version(DSObject):
    """DocuShare File Version"""

    typenum = dsclient.DSXITEMTYPE_DOCVERSION
    upload_attributes = ("Name", "Comment")

    def checkout(self, path=None):
        """Lock file and download it.

        path        (unicode) pathname to download file

        Returns the actual pathname of downloaded file.
        """
        flags = dsclient.DSAXES_FLAG_DOWNLOADVERSION
        self.Name = path
        try_(self.DSDownload(flags))
        self.load()  # Refresh properties.
        return self.Name

    download = checkout


@register
class File(DSContainer):
    """DocuShare File"""

    typenum = dsclient.DSXITEMTYPE_DOCUMENT
    subobject_types = dsclient.DSCONTF_VERSIONS
    upload_attributes = ("Name", "Title", "Summary", "Description",
                         "Keywords", "Author", "MaxVersions", "MimeType")

    def download(self, path=None, version=0, lock=False):
        """Download file content.

        path        (unicode) pathname to download file
        version     (int) version; 0=representative version
        lock        (bool) lock file

        Returns the actual pathname of downloaded file.
        Currently only the representative
        """
        flags = 0
        if path:
            self.Name = path
        if lock:
            flags |= dsclient.DSAXES_FLAG_DOWNLOADLOCKED
        try_(self.DSDownload(flags))
        path = self.Name
        self.load()  # Refresh properties.
        return path

    def checkout(self, path=None):
        """Download file content and lock it.

        path        (unicode) pathname to download file

        Returns the actual pathname of downloaded file.
        """
        return download(path=path, lock=True)

    def lock(self, lock=True):
        """Lock file.

        lock        (bool) lock file
        """
        try_(self.DSLock(lock))
        self.load()  # Refresh properties.

    def unlock(self):
        """Unlock file."""
        try_(self.DSLock(False))
        self.load()  # Refresh properties.

    def add(self, path, **kw):
        """Add a version of File/Document.

        path        (unicode) pathname of file to upload content
        **kw        (dict) attributes to create object, e.g. 'Comment'
        """
        self.Name = path
        for k in kw.keys():
            if k in Version.upload_attributes:
                setattr(self, k, kw[k])
                del kw[k]
        try_(self.DSUpload())
        version = Server(self.Server)("{0}/{1}".format(
                self.Handle, self.HighestVersionUsed))
        for k in kw:
            setattr(self, k, kw[k])
        return version

    def delete(self, version):
        """Delete a Version of File/Document.

        version     (int) version number

        NOTE: this method is not supported yet, because DSClient does not
        support it.  DocuShare UI supports it, so we'll be able to do it
        in the future.
        """
        raise NotImplementedError("deleting Versions is not supported")
