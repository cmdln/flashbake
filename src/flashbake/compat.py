#    copyright 2009-2011 Thomas Gideon, Jason Penney
#
#    This file is part of flashbake.
#
#    flashbake is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    flashbake is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with flashbake.  If not, see <http://www.gnu.org/licenses/>.


'''   compat.py - compatability layer for different versions of python '''

import os.path
import __builtin__
import sys

__all__ = [ 'relpath', 'next_', 'iglob', 'MIMEText' ]

relpath = None
next_ = None

try:
    from glob import iglob
except ImportError:
    from glob import glob as iglob

try:
    import cPickle as pickle
except ImportError:
    import pickle

# Import the email modules we'll need
if sys.hexversion < 0x2050000:
    from email.MIMEText import MIMEText #@UnusedImport
else:
    from email.mime.text import MIMEText #@Reimport

def __fallback_relpath(path, start='.'):
    """Returns a relative version of the path."""
    path = os.path.realpath(path)
    start = os.path.realpath(start)
    if not path.startswith(start):
        raise Exception("unable to calculate paths")
    if os.path.samefile(path, start):
        return "."

    if not start.endswith(os.path.sep):
        start += os.path.sep
    return path[len(start):]

def __fallback_next(*args):
    """next_(iterator[, default])
    
    Return the next item from the iterator. If default is given and 
    the iterator is exhausted, it is returned instead of 
    raising StopIteration."""

    args_len = len(args)
    if (args_len < 1):
        raise TypeError("expected at least 1 argument, got %d" %
                        args_len)
    if (args_len > 2):
        raise TypeError("expected at most 2 arguments, got %d" %
                        args_len)
    iterator = args[0]

    try:
        if hasattr(iterator, '__next__'):
            return iterator.__next__()
        elif hasattr(iterator, 'next'):
            return iterator.next()
        else:
            raise TypeError('%s object is not an iterator' 
                            % type(iterator).__name__)
    except StopIteration:
        if args_len == 2:
            return args[1]
        raise

# relpath
if hasattr(os.path, "relpath"):
    relpath = os.path.relpath
else:
    try:
        import pathutils #@UnresolvedImport
        relpath = pathutils.relative
    except:
        relpath = __fallback_relpath
    
#next_
if hasattr(__builtin__, 'next'):
    next_=__builtin__.next
else:
    next_ = __fallback_next

