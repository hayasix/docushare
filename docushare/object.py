#!/usr/bin/env python2.6
# vim: fileencoding=cp932 fileformat=dos

"""object - DochShare object

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

import os
import datetime
import csv

from .dsclient import *


__all__ = ("DSObject", "register", "getclass")


DSTYPES = dict()
DSOBJECT_PROPERTIES = dict()
PROPERTY_DESCRIPTION = dict()
PROPERTY_TABLE = os.path.join(os.path.split(__file__)[0], "properties.csv")
METHOD_TABLE = os.path.join(os.path.split(__file__)[0], "methods.csv")
STRICT = False

def _read_property_table(path):
    objtypes = ("Server Collection File Document Version SavedQuery Calendar"
                " BulletinBoard Bulletin Weblog WeblogEntry Wiki WikiPage"
                " URL User Group").split()
    with open(path) as f:
        reader = csv.reader(f)
        header = reader.next()
        typepos = dict()
        for pos, name in enumerate(header):
            if name in objtypes:
                typepos[name] = pos
                if name not in DSOBJECT_PROPERTIES:
                    DSOBJECT_PROPERTIES[name] = []
        for row in reader:
            propname = row[0]
            #datatype = row[1]
            #writable = (row[2] == "R/W")
            #loadable = (row[3] == "A")
            #savable = (row[4] == "A")
            for typename, pos in typepos.items():
                if row[pos] == "A":
                    DSOBJECT_PROPERTIES[typename].append(propname)
            PROPERTY_DESCRIPTION[propname] = row[-1]
_read_property_table(PROPERTY_TABLE)
_read_property_table(METHOD_TABLE)


def register(klass):
    DSTYPES[klass.__name__] = klass
    return klass


def getclass(type):
    return DSTYPES[type]


def checkpropertyname(obj, name):
    if name not in DSOBJECT_PROPERTIES[obj.__class__.__name__]:
        raise AttributeError("{0} has no attribute '{1}'".format(
                obj.__class__.__name__, name))


class DSObject(object):
    """DocuShare Object"""

    def __init__(self, obj):
        self._dsobject = obj

    def __repr__(self):
        return self.Handle

    def __str__(self):
        return u"{0}({1})".format(self.Handle, self.Title)

    def __getattribute__(self, name):
        if name[0].isupper():
            if STRICT: checkpropertyname(self, name)
            return getattr(object.__getattribute__(self, "_dsobject"), name)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name[0].isupper():
            if STRICT: checkpropertyname(self, name)
            setattr(object.__getattribute__(self, "_dsobject"), name, value)
        object.__setattr__(self, name, value)

    def properties(self):
        return sorted(DSOBJECT_PROPERTIES[self.__class__.__name__])

    def add(self,
            type="File",
            title="Untitled",
            parent=None,
            **kw):
        """Add a child object.

        type        (str) DocuShare object type e.g. 'Collection', 'File'
        title       (unicode) title of created object; default='Untitled'
        parent      (None, str or DocuShare object) parent object; None=self
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

            new_object = DSObject.add(path=r'C:\UploadFiles\example.doc')
        """
        if type not in DSTYPES:
            raise TypeError("illegal DocuShare object type '{0}'".format(type))
        obj = self.CreateObject(type)
        obj = DSTYPES[type](obj)
        obj.Title = title
        parent = parent or self.Handle  # Put it as a child of this object.
        if not isinstance(parent, basestring):
            parent = parent.Handle
        obj.ParentHandle = parent
        if "path" in kw:
            kw["name"] = kw["path"]
            del kw["path"]
        for (k, v) in kw.items():
            setattr(obj, k.capitalize(), v)
        if "name" in kw:
            status = obj.DSUpload()
        else:
            status = obj.DSCreate()
        return obj.Handle
