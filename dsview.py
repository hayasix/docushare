#!/usr/bin/env python2.7
# vim: fileencoding=cp932 fileformat=dos

import os
import optparse
from ConfigParser import SafeConfigParser

from docushare.client import Client


__version__ = "0.1.3"

DEFAULT_CONF = "~/docushare.ini"
DOCUSHARE_SECTION = "DocuShare"

decode_password = lambda s: (s + "=" * (-len(s) % 4)).decode("base64")
encode_password = lambda s: s.encode("base64").rstrip("=\n")


def main():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--conf", dest="conf", help="read settings from CONF")
    parser.add_option("-a", "--address", dest="address")
    parser.add_option("-y", "--proxy", dest="proxy")
    parser.add_option("-u", "--username", dest="username")
    parser.add_option("-p", "--password", dest="password")
    parser.add_option("-d", "--domain", dest="domain")
    opts, args = parser.parse_args()

    opts.conf = opts.conf or os.path.expanduser(DEFAULT_CONF)
    if os.path.isfile(opts.conf) and opts.conf != "-":
        defaults = dict((k, None) for k
                in "address proxy username password domain".split())
        conf = SafeConfigParser(defaults)
        conf.read(opts.conf)
        opts.address = opts.address or conf.get(DOCUSHARE_SECTION, "address")
        opts.proxy = opts.proxy or conf.get(DOCUSHARE_SECTION, "proxy")
        opts.username = opts.username or conf.get(DOCUSHARE_SECTION, "username")
        opts.password = opts.password or conf.get(DOCUSHARE_SECTION, "password")
        opts.domain = opts.domain or conf.get(DOCUSHARE_SECTION, "domain")

    if not all([opts.address, opts.username, opts.password]):
        raise ValueError("specify address, username and password at least")

    if opts.password.startswith("@@"):
        opts.password = decode_password(opts.password)

    client = Client(opts.address, proxy=opts.proxy, name="DocuShare")
    server = client.connect(opts.username, opts.password, opts.domain)

    for obj in server:
        print u"{handle}: {title}".format(
                handle=obj.Handle, title=obj.Title)


if __name__ == "__main__":
    main()
