#!/usr/bin/env python2.7
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


__all__ = ("DSObject", "DSContainer", "register", "getclass", "customproperty")


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


DSAXES_PROPTYPES = dict(
        bin=dsclient.DSAXES_PROPTYPE_BINARY,
        str=dsclient.DSAXES_PROPTYPE_STRING,
        text=dsclient.DSAXES_PROPTYPE_TEXT,
        url=dsclient.DSAXES_PROPTYPE_URL,
        bool=dsclient.DSAXES_PROPTYPE_BOOLEAN,
        int=dsclient.DSAXES_PROPTYPE_INTEGER,
        float=dsclient.DSAXES_PROPTYPE_FLOAT,
        menu=dsclient.DSAXES_PROPTYPE_MENU,
        date=dsclient.DSAXES_PROPTYPE_DATE,
        email=dsclient.DSAXES_PROPTYPE_EMAIL,
        password=dsclient.DSAXES_PROPTYPE_PASSWORD,
        handle=dsclient.DSAXES_PROPTYPE_HANDLE,
        handlereference=dsclient.DSAXES_PROPTYPE_HANDLEREFERENCE,
        ace=dsclient.DSAXES_PROPTYPE_ACE,
        file=dsclient.DSAXES_PROPTYPE_FILE,
        day=dsclient.DSAXES_PROPTYPE_DAY,
        time=dsclient.DSAXES_PROPTYPE_TIME,
        date_iso8601=dsclient.DSAXES_PROPTYPE_DATE_ISO8601,
        license=dsclient.DSAXES_PROPTYPE_LICENSE,
        handlelist=dsclient.DSAXES_PROPTYPE_HANDLELIST,
        multivalued=dsclient.DSAXES_PROPTYPE_MULTIVALUED,
        )


def customproperty(name, type=dsclient.DSAXES_PROPTYPE_STRING):
    type = DSAXES_PROPTYPES.get(type, type)
    return property(
        #lambda self: self.GetCustomProp(name, type),  # getter
        lambda self: self.Prop(name),  # getter
        lambda self, value: self.SetCustomProp(name, type, value),  # setter
        )


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
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass
        try:
            if STRICT: checkpropertyname(self, name)
            return getattr(object.__getattribute__(self, "_dsobject"), name)
        except AttributeError:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(
                    self.__class__.__name__, name))

    def __setattr__(self, name, value):
        try:
            if STRICT: checkpropertyname(self, name)
            setattr(object.__getattribute__(self, "_dsobject"), name, value)
        except AttributeError:
            pass
        try:
            object.__setattr__(self, name, value)
        except AttributeError:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(
                    self.__class__.__name__, name))

    @property
    def properties(self):
        return sorted(DSOBJECT_PROPERTIES[self.__class__.__name__])

    def delete(self):
        """Delete or unown the DocuShare object."""
        try_(self.DSDelete())

    def load(self):
        """Load property values."""
        self.DSLoadProps()

    def save(self):
        """Save property values."""
        self.DSSaveProps()

    def move(self, dest):
        """Move DocuShare object into a container object.

        dest        (str) desitination DSContainer object handle
                    (DSContainer) destination DSContainer object
        """
        from .server import Server
        server = Server(self.Server)
        if isinstance(dest, basestring):
            dest = server(dest)
        self.DSMove(dest)
        self._dsobject = server(self.Handle)  # dispose cached object

    def copy(self, dest, deep=False):
        """Copy DocuShare object into a container object.

        dest        (str) desitination DSContainer object handle
                    (DSContainer) destination DSContainer object
        deep        (bool) False=reference copy, True=contents copy;
                    valid only for File and Collection instances

        Note that new objects are created only when deep=True.  A reference
        copy, or shallow copy, means just to add a new parent location.

        If deep=True and dest has an File/Document with the same Title as
        self, contents are copied as a new Version.

        CAUTION: In contents copy, only standard properties are copied.
                 Custom properties are NOT copied.
        """
        from .server import Server
        server = Server(self.Server)
        if isinstance(dest, basestring):
            dest = server(dest)
        flags = (dsclient.DSAXES_MODE_COPYCONTENTS |
                 dsclient.DSAXES_MODE_CREATERESULTENUM)
        if deep:
            self.DSGatewayMode |= flags
        else:
            self.DSGatewayMode &= ~ flags
        self.DSCopy(dest)


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

    def dir(self, key="DisplayName"):
        """Show object handles and titles in this container on console.

        key     (str) sort key; DocuShare object attribute name or:
                    'N'=DisplayName (default), 'S'=Length,
                    'C'=TimeCreated, 'M' or 'T'=TimeModified
        """
        if key:
            key = {
                    "A": "TimeAccessed",
                    "C": "TimeCreated",
                    "M": "TimeModified",
                    "N": "DisplayName",
                    "S": "Length",
                    "T": "TimeModified",
                    }.get(key[0].upper(), key)
            for key in [key, "Title", "TimeModified", "TimeCreated"]:
                try:
                    lst = sorted(self, key=lambda member: getattr(member, key))
                    break
                except AttributeError:
                    pass
            else:
                raise AttributeError("can't sort '{0}' objects".format(
                        self.__class__.__name__))
        else:
            lst = self
        for obj in lst:
            print "{0}: {1}".format(obj.Handle, obj.Title)

    def add(self, type=None, **kw):
        """Add a child object.

        type        (str) DocuShare object type; None='File' or 'Collection'
        **kw        (dict) attributes to create object

        Returns the created DocuShare object.

        Each **kw key is a DocuShare object attribute name, e.g. 'Title' or
        'MimeType'.  Note that such attribute names should be capitalized.
        For example, object.Title, object.MimeType and object.Mimetype are
        valid Docushare object attributes.  object.title is a normal Python
        object attribute and may cause AttributeError.
        """
        if "path" in kw:
            if "Name" in kw:
                raise ValueError("path and Name cannot be passed together")
            kw["Name"] = kw["path"]
            del kw["path"]
        if type is None:
            if not ("path" in kw or "Name" in kw):
                raise TypeError("can't determine object type")
            path = kw.get("path", kw.get("Name"))
            type = "Collection" if os.path.isdir(path) else "File"
        type = type.capitalize()
        if type not in DSTYPES:
            raise TypeError("can't add '{0}' object".format(type))
        cls = getclass(type)
        obj = self.CreateObject(type)
        obj.TypeNum = cls.typenum
        obj.ParentHandle = self.Handle
        upload = "Name" in kw
        for k in kw.keys():
            if k in cls.upload_attributes:
                setattr(obj, k, kw[k])
                del kw[k]
        try_(obj.DSUpload() if upload else obj.DSCreate())
        for k in kw:
            setattr(obj, k, kw[k])
        return cls(obj)
