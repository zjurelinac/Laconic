"""Utility datastructures and functions

This module provides various utility functions and datastructures for the
Laconic framework.

Classes:
    Config - Dict-like object for storing app configuration
    Namespace - Simple namespace for storing arbitrary data.
    AttributeScope - Dict which allows searching for keys in parent scopes
    NestedList -

    # ImmutableDict - ?
    # CombinedDict - ?
    # SortedList - ?
    # SortedPriorityList - ?


Functions:
    url_join - Join a sequence of URLs together in a single hierarchical URL

Note:
    Parts of the source code of Config class were borrowed from the Flask project.

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

# import bisect
# import json
# import re

import collections.abc
import os
import types

class Config(dict):
    """Simple dictionary storing app configuration.

    This class differs from builtin Python dict in that when a key is not
    present in the dictionary, attempting to get it won't result in a KeyError,
    but will return None. Also, it supports several utility methods for
    loading configuration parameters from different sources - from Python files
    or objects. When doing so, it will treat only the uppercase keys as config
    parameters, and ignore all others.
    """

    def __init__(self, base_path:str = None, defaults=None):
        super().__init__(defaults or {})
        self._base_path = base_path

    def __missing__(self, key):
        return None

    def from_pyfile(self, filename: str):
        """Load configuration parameters from a Python file.

        Args:
            filename (str): A path (relative to `self.base_path`) to the Python
                file containing configuration parameters.

        Raises:
            IOError: If the configuration file cannot be loaded
        """
        filename = os.path.join(self._base_path, filename)
        d = types.ModuleType('config')
        d.__file__ = filename
        try:
            with open(filename, mode='rb') as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)

    def from_object(self, obj: object):
        """Load configuration parameters from an object.

        Args:
            obj (object): Any object containing uppercase-named attributes which
                should be set as configuration parameters
        """
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, super().__repr__())


class Namespace:
    """Simple namespace for storing arbitrary data."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class AttributeScope(collections.abc.MutableMapping):
    """Nested attribute scope which allows searching for keys in parent scopes.

    Provides a dict-like interface, with the difference that a key missing in
    this scope can be retrieved from any of the parent scopes (if it's there).
    """

    def __init__(self, _parent=None, **items):
        self._data = items
        self._parent = _parent

    def __getitem__(self, key):
        if key in self._data:
            return self._data[key]
        elif self._parent is not None:
            return self._parent[key]
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __len__(self):
        return len(self._combine())

    def __iter__(self):
        return iter(self._combine())

    def __repr__(self):
        return '<%s %s, parent=%s>' % (self.__class__.__name__, self._data, self._parent)

    def _combine(self):
        ds, t = [], self
        while t is not None:
            ds.append(t._data)
            t = t._parent

        rd = {}
        for d in reversed(ds):
            rd.update(d)

        return rd


# class SortedList:
#     # def __init__(self, *args):
#     #     self._items = sorted(args)

#     # def add(self, item):
#     #     """Add an element to the sorted list, which remains sorted afterwards"""
#     #     bisect.insort(self._items, item)

#     # def remove(self, item):
#     #     """Remove an element from the sorted list"""
#     #     self._items.remove(item)

#     # def __repr__(self):
#     #     return 'SortedList(%s)' % (', '.join(repr(i) for i in self._items))
#     pass


# class SortedPriorityList:
#     # """
#     # A list of values sorted by their priority and insertion order.
#     # Not too fast implementation as of yet.
#     # """

#     # def __init__(self):
#     #     self.elems = []
#     #     self.counter = 0

#     # def add(self, priority, item):
#     #     """Add an element to the sorted list, which remains sorted afterwards"""
#     #     bisect.insort(self.elems, (-priority, self.counter, item))
#     #     self.counter += 1

#     # def remove(self, item):
#     #     """Remove an element from the sorted list"""
#     #     for i, elem in enumerate(self.elems):
#     #         if elem[2] == item:
#     #             del self.elems[i]
#     #             break

#     # def __iter__(self):
#     #     for elem in self.elems:
#     #         yield elem[2]

#     # def __repr__(self):
#     #     pass
#     pass


# import collections

# class ImmutableDict(collections.Mapping):
#     """Don't forget the docstrings!!"""

#     def __init__(self, *args, **kwargs):
#         self._d = dict(*args, **kwargs)
#         self._hash = None

#     def __iter__(self):
#         return iter(self._d)

#     def __len__(self):
#         return len(self._d)

#     def __getitem__(self, key):
#         return self._d[key]

#     def __hash__(self):
#         # It would have been simpler and maybe more obvious to
#         # use hash(tuple(sorted(self._d.iteritems()))) from this discussion
#         # so far, but this solution is O(n). I don't know what kind of
#         # n we are going to run into, but sometimes it's hard to resist the
#         # urge to optimize when it will gain improved algorithmic performance.
#         if self._hash is None:
#             self._hash = 0
#             for pair in self.iteritems():
#                 self._hash ^= hash(pair)
#         return self._hash

# class CombinedDict:
#     """
#     Read-only combined dict which allows retrieval of values from any of the
#     contained dicts, in order they were passed into the constructor.
#     If the key isn't present, retrieval will return None.
#     """

#     def __init__(self, dicts):
#         self.dicts = [d for d in dicts if d is not None]

#     def __getitem__(self, key):
#         for dct in self.dicts:
#             if key in dct:
#                 return dct[key]

#     def __setitem__(self, key, value):
#         raise TypeError('Cannot modify contents of a CombinedDict')


# def url_join(*urls):
#     """Join a list of URL fragments into a single URL"""
#     if len(urls) == 0:
#         raise ValueError('No URLs to join!')
#     elif len(urls) == 1:
#         return urls[0]
#     else:
#         return (urls[0].rstrip('/') + '/' +
#                 '/'.join([u.strip('/') for u in urls[1:-1]]) +
#                 '/' + urls[-1].lstrip('/'))


# def make_json(data_dict):
#     """Return JSON representation of Python `data_dict` dictionary."""
#     return json.dumps(data_dict, indent=4, sort_keys=True, separators=(',', ': '))


# # def exc_type_compare(exc_type1, exc_type2):
# #     """Compare two exception types"""
# #     if issubclass(exc_type1, exc_type2):
# #         return -1
# #     elif issubclass(exc_type2, exc_type1):
# #         return 1
# #     else:
# #         sc_depth1 = len(exc_type1.__mro__)
# #         sc_depth2 = len(exc_type2.__mro__)

# #         if sc_depth1 == sc_depth2:
# #             return -1 if exc_type1.__name__ < exc_type2.__name__ else 1
# #         else:
# #             return -1 if sc_depth1 < sc_depth2 else 1
