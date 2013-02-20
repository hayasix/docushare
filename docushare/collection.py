#!/usr/bin/env python2.6
# vim: fileencoding=cp932 fileformat=dos

"""collection  -  DochShare Collection

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from . import dsclient
from .object import DSContainer, register


__all__ = ("Collection",)


@register
class Collection(DSContainer):
    """DocuShare Collection"""

    typenum = dsclient.DSXITEMTYPE_COLLECTION
    subobject_types = dsclient.DSCONTF_CHILDREN
    subobject_typenames = ("Collection", "File", "BulletinBoard", "Weblog", "Wiki")

    def add(self, type="File", title=None, **kw):
        """Add a child object in the collection.

        type        (str) 'Collection' | 'File' | 'BulletinBoard' | 'Weblog' |
                          'Wiki'
        title       (unicode or None) title of created object; None='Untitled';
                    if `path=' is given, None=(basename of path)
        **kw        (dict) attributes of created object; case is ignored but
                    recommended to be capitalized in each attribute name

        Returns the handle of created Docushare object.

        Each **kw key is a DocuShare object attribute name, e.g. 'Title' or
        'MimeType'.  Note that such attribute names should be capitalized.
        For example, object.Title, object.MimeType and object.Mimetype are
        valid Docushare object attributes.  object.title is a normal Python
        object attribute and may cause AttributeError.

        You can add a new File/Document object by uploading an existing local
        file.  To do so, place an keyword argument `path='.  For example:

            new_object = self.add(path=r'C:\UploadFiles\example.doc')
        """
        type = type.capitalize()
        if type not in subobject_typenames:
            raise TypeError("illegal DocuShare object type '{0}'".format(type))
        if "path" in kw:
            if type != "File":
                raise ValueError(
                        "type='File' required, '{0}' given".format(type))
            obj = self.CreateObject(type)
            kw["Name"] = kw["path"]
            title = title or os.path.basename(kw["path"])
            del kw["path"]
        else:
            obj = self.CreateObject(type)
        obj.TypeNum = getclass(type).typenum
        obj.Title = title or u"Untitled"
        obj.ParentHandle = self.Handle
        for k, v in kw.items():
            setattr(obj, k.capitalize(), v)
        if "Name" in kw:
            try_(obj.DSUpload())
        else:
            try_(obj.DSCreate())
        return obj.Handle
