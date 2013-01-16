#!/usr/bin/env python2.6
# vim: fileencoding=cp932 fileformat=dos

"""error  -  DochShare Client (DSAXES) error names

Copyright (C) 2012 HAYASI Hideki <linxs@linxs.org>  All rights reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.
"""

from . import dsclient


__all__ = ("DSError", "errmsg", "try_")


ERRORNAMES = dict((v, k) for (k, v) in dsclient.__dict__.items()
                                    if k.startswith("DSAXES_E_"))

def errmsg(n):
    return ERRORNAMES.get(n, "UNDEFINED_ERROR")


class DSError(Exception):
    pass


def try_(rc):
    if rc < 0:
        raise DocuShareError(errmsg(rc))
    return rc
