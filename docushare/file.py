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
from .error import try_


__all__ = ("Version", "File")


@register
class Version(DSObject):
    """DocuShare File Version"""

    typenum = dsclient.DSXITEMTYPE_DOCVERSION


@register
class File(DSContainer):
    """DocuShare File"""

    typenum = dsclient.DSXITEMTYPE_DOCUMENT
    subobject_types = dsclient.DSCONTF_VERSIONS

    def checkout(self, lock=True):
        """Lock file and download it.

        lock        (bool) lock file

        Returns the actual pathname of downloaded file.
        Currently only the representative version of file can be acquired.
        """
        flags = dsclient.DSAXES_FLAG_DOWNLOADREPR  # Representative version.
        if lock:
            flags |= dsclient.DSAXES_FLAG_DOWNLOADLOCKED
        self.DSDownload(flags)
        self.load()  # Refresh properties.
        return self.Name

    def download(self):
        """Download file, i.e. checkout without locking.

        Returns the actual pathname of downloaded file.
        """
        return self.checkout(lock=False)

    def update(self, unlock=True):
        """Update the file of DocuShare File object.

        unlock      (bool) release file lock
        """
        self.DSUpload()
        if unlock:
            self.unlock()
        self.load()  # Refresh properties.

    def lock(self, lock=True):
        """Lock file.

        lock        (bool) lock file
        """
        self.DSLock(lock)
        self.load()  # Refresh properties.

    def unlock(self):
        """Unlock file."""
        self.DSLock(False)
        self.load()  # Refresh properties.

    def add(self, path, **kw):
        """Add a new Version of File/Document.

        path        (unicode) pathname of the file to upload
        **kw        (dict) attributes of created Version; case is ignored but
                    recommended to be capitalized in each attribute name

        Returns the alias of created Version handle such as `File-1234/8'.
        Digits following '/' represents the (maximum) version number.
        You can get the created Version object by Server.__call__() as:

            version_handle_alias = self.add(path='...')
            version = server(version_handle_alias)
        """
        if not path:
            raise ValueError("pathname is required")
        self.Name = path
        for k, v in kw.items():
            setattr(self, k.capitalize(), v)
        try_(self.DSUpload())
        return max(self, key=lambda v: v.VersionNum).Handle
