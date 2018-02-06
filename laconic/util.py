"""
Utility datastructures and functions

...

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

import bisect
import json
import re


class Config(dict):
    """
    Config dict - contains app configuration options. Difference from dict -
    when an item isn't present, won't raise a KeyError, but will return None.
    """

    def __missing__(self, key):
        return None


class AttributeScope:
    """
    Nested attribute scope - provides a dict-like interface, with the difference
    that an element not present in this scope can be retrieved from the parent
    scope.
    """

    def __init__(self, _parent=None, **kwargs):
        self.data = kwargs
        self._parent = _parent

    def __getitem__(self, key):
        if key in self.data:
            return self.data
        return self._parent[key] if self._parent is not None else None

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]


class SortedList:
    # def __init__(self, *args):
    #     self._items = sorted(args)

    # def add(self, item):
    #     """Add an element to the sorted list, which remains sorted afterwards"""
    #     bisect.insort(self._items, item)

    # def remove(self, item):
    #     """Remove an element from the sorted list"""
    #     self._items.remove(item)

    # def __repr__(self):
    #     return 'SortedList(%s)' % (', '.join(repr(i) for i in self._items))
    pass


class SortedPriorityList:
    # """
    # A list of values sorted by their priority and insertion order.
    # Not too fast implementation as of yet.
    # """

    # def __init__(self):
    #     self.elems = []
    #     self.counter = 0

    # def add(self, priority, item):
    #     """Add an element to the sorted list, which remains sorted afterwards"""
    #     bisect.insort(self.elems, (-priority, self.counter, item))
    #     self.counter += 1

    # def remove(self, item):
    #     """Remove an element from the sorted list"""
    #     for i, elem in enumerate(self.elems):
    #         if elem[2] == item:
    #             del self.elems[i]
    #             break

    # def __iter__(self):
    #     for elem in self.elems:
    #         yield elem[2]

    # def __repr__(self):
    #     pass
    pass


class CombinedDict:
    """
    Read-only combined dict which allows retrieval of values from any of the
    contained dicts, in order they were passed into the constructor.
    If the key isn't present, retrieval will return None.
    """

    def __init__(self, dicts):
        self.dicts = [d for d in dicts if d is not None]

    def __getitem__(self, key):
        for dct in self.dicts:
            if key in dct:
                return dct[key]

    def __setitem__(self, key, value):
        raise TypeError('Cannot modify contents of a CombinedDict')


class Namespace:
    """A simple namespace for storing arbitrary data"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def url_join(*urls):
    """Join a list of URL fragments into a single URL"""
    if len(urls) == 0:
        raise ValueError('No URLs to join!')
    elif len(urls) == 1:
        return urls[0]
    else:
        return (urls[0].rstrip('/') + '/' +
                '/'.join([u.strip('/') for u in urls[1:-1]]) +
                '/' + urls[-1].lstrip('/'))


def make_json(data_dict):
    """Return JSON representation of Python `data_dict` dictionary."""
    return json.dumps(data_dict, indent=4, sort_keys=True, separators=(',', ': '))


# def exc_type_compare(exc_type1, exc_type2):
#     """Compare two exception types"""
#     if issubclass(exc_type1, exc_type2):
#         return -1
#     elif issubclass(exc_type2, exc_type1):
#         return 1
#     else:
#         sc_depth1 = len(exc_type1.__mro__)
#         sc_depth2 = len(exc_type2.__mro__)

#         if sc_depth1 == sc_depth2:
#             return -1 if exc_type1.__name__ < exc_type2.__name__ else 1
#         else:
#             return -1 if sc_depth1 < sc_depth2 else 1
