# -*- coding: utf-8 -*-
# Copyright 2016 Nick Boultbee
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

import os
from datetime import datetime
from gi.repository import Gtk

from quodlibet import print_d

DEFAULT_BITRATE = 128
EPOCH = datetime(1970, 1, 1)
SITE_URL = "http://soundcloud.com"
IMAGE_DIR = 'quodlibet/images/branding/soundcloud'


def _local_image(filename):
    """
    Get a local branding image from disk
    TODO: load these from the web (and cache)
    """
    return Gtk.Image.new_from_file(os.path.join(IMAGE_DIR, filename))


LOGO_IMAGE_BLACK = _local_image('soundcloud-logo-black-104x16.png')
LOGIN_IMAGES = [_local_image('btn-%s-l.png'
                             % ('disconnect' if online else 'connect'))
                for online in (False, True)]


class Wrapper(object):
    """Object-like wrapper for read-only dictionaries"""

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        if name in self.data:
            return self.data.get(name)
        raise AttributeError(name)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        raise NotImplementedError

    def get(self, name, default=None):
        return self.data.get(name, default)

    def __str__(self):
        return "<Wrapped: %s>" % self.data


def json_callback(wrapped):
    """Decorator for `download_json` callbacks, handling common errors"""

    def _callback(self, message, json, data):
        if json is None:
            print_d('Invalid JSON ({message.status_code}): '
                    '{message.response_body.data} (request: {data})'
                    .format(**locals()))
            return
        if 'errors' in json:
            raise ValueError("Got HTTP %d (%s)" % (message.status_code,
                                                   json['errors']))
        if 'error' in json:
            raise ValueError("Got HTTP %d (%s)" % (message.status_code,
                                                   json['error']))
        return wrapped(self, json)

    return _callback


def clamp(val, low, high):
    intval = int(val or 0)
    return max(low, min(high, intval))