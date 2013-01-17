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

import os.path
#from pywintypes import Time as PyTime
import win32com.client

from . import dsclient
from .error import try_


__all__ = ("DSObject", "DSContainer", "register", "getclass")


DSTYPES = dict()
DSOBJECT_PROPERTIES = dict()
PROPERTY_DESCRIPTION = dict()
PROPERTY_TABLE = "properties.csv"
METHOD_TABLE = "methods.csv"
STRICT = False


def _read_property_tables(*paths):
    import csv
    objtypes = ("Server Collection File Document Version SavedQuery Calendar"
                " BulletinBoard Bulletin Weblog WeblogEntry Wiki WikiPage"
                " URL User Group").split()
    for path in paths:
        path = os.path.join(os.path.split(__file__)[0], path)
        with open(path) as table:
            reader = csv.reader(table)
            header = reader.next()
            typepos = dict()
            for pos, typename in enumerate(header):
                if typename in objtypes:
                    typepos[typename] = pos
                    if typename not in DSOBJECT_PROPERTIES:
                        DSOBJECT_PROPERTIES[typename] = []
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
_read_property_tables(PROPERTY_TABLE, METHOD_TABLE)
del _read_property_tables

DSNUMTYPE = dict(enumerate((
        "Root Server Collection File Version "
        "Calendar BulletinBoard URL Bulletin SavedQuery "
        "Event Rendition DocVersion Subscription User "
        "Group Unknown Object ContElem MailMessage "
        "Workspace Wiki Weblog"
        ).split()))
DSNUMTYPE[34] = "WikiPage"
DSNUMTYPE[35] = "WeblogEntry"
DSTYPENUM = dict((n, p) for (p, n) in enumerate(DSNUMTYPE))


def register(klass):
    DSTYPES[klass.__name__] = klass
    return klass


def getclass(type):
    if isinstance(type, basestring):
        return DSTYPES[type]
    if isinstance(type, (int, long, float)):
        return DSTYPES.get(DSNUMTYPE[type], DSObject)
    raise ValueError("illegal type '{0}'".format(repr(type)))


def checkpropertyname(obj, propname):
    if propname not in DSOBJECT_PROPERTIES[obj.__class__.__name__]:
        raise AttributeError("{0} has no attribute '{1}'".format(
                obj.__class__.__name__, propname))


class DSObject(object):
    """DocuShare Object"""

    def __init__(self, obj):
        self._dsobject = obj

    def __repr__(self):
        if hasattr(self, "Handle"):
            return self.Handle
        return "<DSObject at 0x{0:x}>".format(id(self))

    def __str__(self):
        if hasattr(self, "Handle"):
            return u"{0}({1})".format(self.Handle, self.Title)
        return "<DSObject at {0:x}>".format(id(self))

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

    @property
    def properties(self):
        return sorted(DSOBJECT_PROPERTIES[self.__class__.__name__])


class DSContainer(DSObject):
    """Base class for DocuShare object container like Collection"""

    subobject_types = dsclient.DSCONTF_CHILDREN

    def __iter__(self):
        try_(self.DSLoadChildren())
        chain = self.EnumObjects(self.__class__.subobject_types)
        chain.Reset()
        while chain.NextPos:
            obj = chain.NextItem
            yield getclass(obj.TypeNum)(obj)

    def dir(self):
        """Show object handles and titles in this container on console."""
        for obj in self:
            print "{0}: {1}".format(obj.Handle, obj.Title)

    def add(self, type="File", title="Untitled", parent=None, **kw):
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
        type = type.capitalize()
        if type not in DSTYPES:
            raise TypeError("illegal DocuShare object type '{0}'".format(type))
        if "path" in kw:
            if type != "File":
                raise ValueError("type='File' required, '{0}' given")
            obj = self.CreateObject("File")
            kw["Name"] = kw["path"]
            del kw["path"]
        else:
            obj = self.CreateObject(type)
        obj.TypeNum = getclass(type).typenum
        obj.Title = title
        if parent is None:
            parent = self.Handle
        elif not isinstance(parent, basestring):
            parent = parent.Handle
        obj.ParentHandle = parent
        for k, v in kw.items():
            setattr(obj, k.capitalize(), v)
        if "Name" in kw:
            try_(obj.DSUpload())
        else:
            try_(obj.DSCreate())
        return obj
