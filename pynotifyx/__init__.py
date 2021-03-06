# Copyright (c) 2005 Manuel Amador
# Copyright (c) 2009-2011 Forest Bond
# Copyright (c) 2017 Joe Isca

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os

try:
    from pynotifyx import binding
except Exception:
    pass

__version__ = (0, 3, 7)

try:
    constants = {}

    for name in dir(binding):
        if name.startswith('IN_'):
            globals()[name] = constants[name] = getattr(binding, name)

    init = binding.init
    rm_watch = binding.rm_watch
    add_watch = binding.add_watch
except Exception:
    pass


class InotifyEvent(object):
    '''
    InotifyEvent(wd, mask, cookie, name)

    A representation of the inotify_event structure.  See the inotify
    documentation for a description of these fields.
    '''

    wd = None
    mask = None
    cookie = None
    name = None

    def __init__(self, wd, mask, cookie, name):
        self.wd = wd
        self.mask = mask
        self.cookie = cookie
        self.name = name

    def __str__(self):
        return '%s: %s' % (self.wd, self.get_mask_description())

    def __repr__(self):
        return '%s(%s, %s, %s, %s)' % (
            self.__class__.__name__,
            repr(self.wd),
            repr(self.mask),
            repr(self.cookie),
            repr(self.name),
        )

    def get_mask_description(self):
        '''
        Return an ASCII string describing the mask field in terms of
        bitwise-or'd IN_* constants, or 0.  The result is valid Python code
        that could be eval'd to get the value of the mask field.  In other
        words, for a given event:

        >>> from pynotifyx import *
        >>> assert (event.mask == eval(event.get_mask_description()))
        '''

        parts = []
        for name, value in constants.items():
            if self.mask & value:
                parts.append(name)
        if parts:
            return '|'.join(parts)
        return '0'


def get_events(fd, *args):
    '''
    get_events(fd[, timeout])

    Return a list of InotifyEvent instances representing events read from
    inotify.  If timeout is None, this will block forever until at least one
    event can be read.  Otherwise, timeout should be an integer or float
    specifying a timeout in seconds.  If get_events times out waiting for
    events, an empty list will be returned.  If timeout is zero, get_events
    will not block.
    '''
    return [
        InotifyEvent(wd, mask, cookie, name)
        for wd, mask, cookie, name in binding.get_events(fd, *args)
    ]


def main():
    import sys

    if len(sys.argv) == 1:
        sys.stderr.write("usage: %s path [path ...]\n" % (sys.argv[0]))
        sys.exit(1)

    paths = sys.argv[1:]

    fd = init()

    wd_to_path = {}

    try:
        for path in paths:
            wd = add_watch(fd, path)
            wd_to_path[wd] = path

        try:
            while True:
                events = get_events(fd)
                for event in events:
                    path = wd_to_path[event.wd]
                    parts = [event.get_mask_description()]
                    if event.name:
                        parts.append(event.name)
                    print('%s: %s' % (path, ' '.join(parts)))
        except KeyboardInterrupt:
            pass

    finally:
        os.close(fd)
