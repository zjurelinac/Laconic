"""Utility datastructures and functions

This module provides various utility functions and datastructures for the
Laconic framework.

Classes:
    Config - Dict-like object for storing app configuration
    Namespace - Simple namespace for storing arbitrary data.
    AttributeScope - Dict which allows searching for keys in parent scopes
    ImmutableOrderedList - Immutable ordered list of objects of any kind

    DispatchParam - Description of a single Dispatchable object's parameter
    Dispatchable - Callable wrapper containing info about all its parameters
    ExceptionHandler - Exception handler wrapper class

Decorators:
    dispatchable - For manual definition of callable's params and return type

Functions:
    join_urls(*urls) - Join a sequence of URLs together in a single URL
    exc_type_cmp(et1, et2) - Compare two exception types
    camel_case_split - Split a camelcase-capitalized string

Note:
    Parts of the source code of Config class were borrowed from the Flask project.

Copyright:  (c) Zvonimir Jurelinac 2018
License:    MIT, see LICENSE for more details
"""

# import bisect

import functools
import operator
import os
import re
import types

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from inspect import signature, Signature


# Generic sentinel value representing missing parameter/attribute
_MISSING = object()


# Generic datastructures

class Config(MutableMapping):
    """Simple dictionary storing app configuration.

    This class differs from builtin Python dict in that when a key is not
    present in the dictionary, attempting to get it won't result in a KeyError,
    but will return None. Also, it supports several utility methods for
    loading configuration parameters from different sources - from Python files
    or objects. When doing so, it will treat only the uppercase keys as config
    parameters, and ignore all others.

    Attributes:
        _base_path (str): Starting point in the filesystem from where Python
            files will be looked for (in `from_pyfile` method)
    """

    __slots__ = ['_data', '_base_path']

    def __init__(self, base_path: str=None, **defaults):
        self._data = defaults or {}
        self._base_path = base_path

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def from_pyfile(self, filename: str) -> None:
        """Load configuration from a Python file.

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

    def from_object(self, obj: object) -> None:
        """Load configuration from an object.

        Args:
            obj (object): Any object containing uppercase-named attributes which
                should be set as configuration parameters
        """
        for key in dir(obj):
            if key.isupper():
                self._data[key] = getattr(obj, key)

    def from_dict(self, obj: dict) -> None:
        """Load configuration from a Python dict
        
        Args:
            obj (dict): A dict whose uppercase-named keys should be set as
                configuration parameters
        """
        for key in obj:
            if key.isupper():
                self._data[key] = obj[key]

    @classmethod
    def create(cls, obj, defaults=None, base_path=None):
        """Create a Config object from passed arguments.
        
        Args:
            obj (any): Either a string containing filename of the Python file,
                a dictionary, or an object, from which the config parameters
                should be read
            defaults (optional, dict): Default config values which can be
                overriden with those from `obj`
            base_path (optional, str): Base filesystem path, location of a
                starting point from which Python files will be looked for
                (in `from_pyfile` method)
        """
        cfg = cls(base_path=base_path, **(defaults or {}))

        if isinstance(obj, str):
            cfg.from_pyfile(obj)
        elif isinstance(obj, dict):
            cfg.from_dict(obj)
        else:
            cfg.from_object(obj)

        return cfg

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self._data)


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


class AttributeScope(Mapping):
    """Nested attribute scope which allows searching for keys in parent scopes.

    Provides a dict-like interface, with the difference that a key missing in
    this scope can be retrieved from any of the parent scopes (if it's there).
    It is also immutable.

    Methods (additional):
        all(self, key) - Return all values this key maps to from the whole
            scope hierarchy
    """

    __slots__ = ['_data', '_parent']

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

    def __len__(self):
        return len(self._combine())

    def __iter__(self):
        return iter(self._combine())

    def __repr__(self):
        return '<%s %s, parent=%s>' % (self.__class__.__name__, self._data, self._parent)

    def all(self, key) -> list:
        """Return all values this key maps to from the whole scope hierarchy

        Returns a list of all values corresponding to the given key in the whole
        scope hierarchy, ordered bottop-up
        """
        scope, result = self, []
        while scope is not None:
            if key in scope:
                result.append(scope[key])
            scope = scope._parent
        return result

    def _combine(self):
        ds, t = [], self
        while t is not None:
            ds.append(t._data)
            t = t._parent

        rd = {}
        for d in reversed(ds):
            rd.update(d)

        return rd


class ImmutableDict(Mapping):
    """Immutable variant of builtin dictionary"""
    __slots__ = ['_data']

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 arguments, got %d'
                            % (self.__class__.__name__, len(args)))
        self._data = dict(args, **kwargs)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self._data)


class ImmutableOrderedList(Sequence):
    """Immutable ordered list of objects of any kind."""

    __slots__ = ['_items']

    def __init__(self, iterable, cmp=None, reverse=False):
        """ImmutableOrderedList constructor.

        Creates an immutable ordered list from the given iterable. Ordering can
        be performed either with default or with a custom comparator, and either
        in normal or reversed order.

        Args:
            iterable (Iterable): Iterable sequence of items to build the
                immutable ordered list from
            cmp (optional, Callable): Custom comparator for ordering of items
            reverse (optional, bool): Should the items be reversed, default: False
        """
        key = functools.cmp_to_key(cmp) if cmp is not None else None
        self._items = sorted(iterable, key=key, reverse=reverse)

    def __getitem__(self, key):
        return self._items[key]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self._items)


# Dispatching structures

class DispatchParam:
    """Self-contained description of a single Dispatchable object's parameter.

    Attributes:
        name (str): Parameter name
        type_ (type): Parameter type
        default (optional, type): Parameter's default value, if any
            (default: _MISSING, which is a sentinel meaning: No default is set)
        **extras: Arbitrary extra info about the parameter
    """
    __slots__ = ['name', 'type_', 'default', 'extras']

    def __init__(self, name: str, type_: type, default: type=_MISSING, **extras):
        """DispatchParam constructor."""
        self.name = name
        self.type_ = type_
        self.default = default
        self.extras = extras

    @classmethod
    def from_signature(cls, signature: Signature, type_required: bool=False, **extras):
        """Construct a DispatchParam from inspect.Signature object.

        Args:
            signature (Signature):
            type_required (optional, bool):
            **extras:
        """
        if type_required and signature.annotation is Signature.empty:
            raise Exception('Untyped parameter')  # TODO: Specify which exception
        default = signature.default if signature.default is not None else _MISSING
        return cls(signature.name, signature.annotation, default, **extras)

    def __repr__(self):
        if self.default == _MISSING:
            return '<%s %s: %s>' % (self.__class__.__name__, self.name, self.type_)
        else:
            return '<%s %s: %s = %s>' % (self.__class__.__name__, self.name,
                                         self.type_, self.default)


class Dispatchable(Callable):
    """Callable wrapper containing info about all its parameters.

    A Dispatchable object is a wrapper around any Python callable containing
    info about its parameters - their names, types, default values..., and
    return type.

    Attributes:
        callable (Callable) - Actual callable being wrapped
        parameters (List[DispatchParam]) - Descriptions of callable's parameters
        return_type (type) - Return type of the callable
    """

    __slots__ = ['callable', 'parameters', 'return_type']

    def __init__(self, callable: Callable, parameters: list, return_type: type):
        self.callable = callable
        self.parameters = parameters
        self.return_type = return_type

    @classmethod
    def from_signature(cls, callable: Callable):
        if not isinstance(callable, Callable):
            raise TypeError('Object is not a callable: %s' % callable)

        call_sign = signature(callable)
        parameters = {
            k: DispatchParam.from_signature(v, type_required=True)
                for k, v in call_sign.parameters.items()
        }

        return_type = call_sign.return_annotation

        return cls(callable, parameters, return_type)

    def __call__(self, *args, **kwargs):
        return self.callable(args, kwargs)

    def __repr__(self):
        return '<%s (%s) %s -> %s>' % (self.__class__.__name__, self.callable,
                                       self.parameters, self.return_type)


class ExceptionHandler(Dispatchable):
    """Exception handler wrapper class.

    An ExceptionHandler is a wrapper around any Python callable chosen to handle
    exceptions of a certain type. It contains info about all the handler's
    parameters - their names, types, default values etc., as well as type of
    exceptions it should handle and additional arbitrary configuration
    parameters that can be used to further specify details of exception handling.

    Attributes:
        exc_type (type) - Type of exceptions the handler handles
        attrs (AttributeScope) - Arbitrary configuration parameters for
            the exception handler
        parameters (List[DispatchParam]) - Descriptions of exception handler
            callable' parameters
        return_type (type) - Return type of exception handler
        _callable (Callable) - Actual callable which will handle the exception
    """

    __slots__ = ['exc_type', 'attrs']

    def __init__(self, exc_type: type, exc_handler: Callable,
                 config_params: AttributeScope):
        self.callable = exc_handler
        self.exc_type = exc_type
        self.attrs = config_params
        
        disp = super().from_signature(exc_handler)

        self.parameters = disp.parameters
        self.return_type = disp.return_type

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __ne__(self, other):
        return self._cmp(other) != 0

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __repr__(self):
        return '<%s for %s (%s -> %s)>' % (self.__class__.__name__, self.exc_type,
                                          self.parameters, self.return_type)

    def _cmp(self, other) -> int:
        tcmp = _util_cmp(self.exc_type, other.exc_type)
        return tcmp if tcmp != 0 else _util_cmp(self.callable, other.callable)


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


# Decorators


def dispatchable(parameters: list=None, return_type: type=None):
    """Decorator for manual definition of callable's params and return type.
    
    Takes the decorated callable and wraps it into a Dispatchable, recording the
    expected parameters and return type definitions. Callable's parameters
    should be specified as a list of tuples:
        `(param_name, param_type, [default_value])`

    Args:
        parameters (List[Tuple]) - Descriptions of callable's parameters
        return_type (type) - Return type of the callable
    """
    processed_params = []
    for name, type_, *default in parameters:
        processed_params.append(DispatchParam(name, type_, default or _MISSING))
    
    def decorator(f: Callable) -> Dispatchable:
        return Dispatchable(f, processed_params, return_type)
    return decorator


# Utility functions

def join_urls(*urls) -> str:
    """Join multiple URL fragments together.

    Args:
        urls (List[str]): List of URL fragments to join

    Returns:
        str: URL joining result
    """
    if len(urls) == 0:
        raise ValueError('No URLs to join')

    leading = '\\' if urls[0][0] == '\\' else ''
    trailing = '\\' if urls[-1][-1] == '\\' else ''

    return leading + ('/'.join(u.strip('/') for u in urls)) + trailing


def exc_type_cmp(exc_type1: type, exc_type2: type):
    """Compare two exception types.

    Standard comparison function returning -1, 0 or 1. Tests if one type is a
    subclass of the other, then which one is more specific (lower in hierarchy),
    and if still a tie, which has lexicographically smaller name.
    """

    if issubclass(exc_type1, exc_type2):
        return -1
    elif issubclass(exc_type2, exc_type1):
        return 1

    # Comparison of exception types' depths in class hierarchy
    #   (= number of superclasses of each)
    dcmp = _util_cmp(len(exc_type1.__mro__), len(exc_type2.__mro__))

    return dcmp if dcmp != 0 else _util_cmp(exc_type1.__name__, exc_type2.__name__)


def _util_cmp(x, y):
    """Utility compare function, standard format"""
    return 0 if x == y else (-1 if x < y else 1)


def camel_case_split(identifier: str) -> list:
    """Split a camelcase-capitalized string into its sections"""
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]
