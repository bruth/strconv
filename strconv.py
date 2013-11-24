# strconv.py
# Copyright (c) 2013 Byron Ruth
# BSD License
from __future__ import print_function

__version__ = '0.2.0'

from collections import Counter


class TypeInfo(object):
    "Sampling and frequency of a type for a sample of values."
    def __init__(self, type_name, size=None, total=None):
        self.type_name = type_name
        self.count = 0
        self.sample = []
        self.size = size
        self.total = total
        self.sample_set = set()

    def __repr__(self):
        return '<{0}: {1} n={2}>'.format(self.__class__.__name__,
                                         self.type_name, self.count)

    def incr(self, n=1):
        self.count += n

    def add(self, i, value):
        if self.size is None or len(self.sample) < self.size:
            # No dupes
            if value not in self.sample_set:
                self.sample_set.add(value)
                self.sample.append((i, value))

    def freq(self):
        if self.total:
            return self.count / float(self.total)
        return 0.


class Types(object):
    "Type information for a sample of values."
    def __init__(self, size=None, total=None):
        self.size = size
        self.total = None
        self.types = {}

    def __repr__(self):
        types = self.most_common()
        label = ', '.join(['{0}={1}'.format(t, i.count) for t, i in types])
        return '<{0}: {1}>'.format(self.__class__.__name__, label)

    def incr(self, t, n=1):
        if t is None:
            t = 'unknown'
        if t not in self.types:
            self.types[t] = TypeInfo(t, self.size, self.total)
        self.types[t].incr(n)

    def add(self, t, i, value):
        if t is None:
            t = 'unknown'
        if t not in self.types:
            self.types[t] = TypeInfo(t, self.size, self.total)
        self.types[t].add(i, value)

    def set_total(self, total):
        self.total = total
        for k in self.types:
            self.types[k].total = total

    def most_common(self, n=None):
        if n is None:
            n = len(self.types)
        c = Counter()
        for t in self.types:
            c[t] = self.types[t].count
        return c.most_common(n)


converters = {}
converters_order = []


def register_converter(type_name, func, priority=None):
    if type_name is None:
        raise ValueError('type name cannot be None')
    if not callable(func):
        raise ValueError('converter functions must be callable')

    converters[type_name] = func

    if type_name in converters_order:
        converters_order.remove(type_name)

    if priority is not None and priority < len(converters_order):
        converters_order.insert(priority, type_name)
    else:
        converters_order.append(type_name)


def unregister_converter(type_name):
    if type_name in converters_order:
        converters_order.remove(type_name)
    if type_name in converters:
        del converters[type_name]


def get_converter(type_name):
    if type_name not in converters:
        raise KeyError('no converter for type "{0}"'.format(type_name))
    return converters[type_name]


def convert(s, include_type=False):
    if isinstance(s, basestring):
        for t in converters_order:
            func = converters[t]
            try:
                v = func(s)
                if include_type:
                    return v, t
                return v
            except ValueError:
                pass
    if include_type:
        return s, None
    return s


def convert_series(iterable, include_type=False):
    c = convert
    for s in iterable:
        yield c(s, include_type=include_type)


def convert_matrix(matrix, include_type=False):
    c = convert
    for r in matrix:
        yield tuple(c(s, include_type=include_type) for s in r)


def infer(s, converted=False):
    v, t = convert(s, include_type=True)
    if t and converted:
        return type(v)
    return t


def infer_series(iterable, n=None, size=10):
    info = Types(size=size)
    i = -1

    for i, value in enumerate(iterable):
        if n and i > n:
            i = n
            break

        t = infer(value)
        info.incr(t)
        info.add(t, i, value)
    else:
        i += 1

    info.set_total(i)
    return info


def infer_matrix(matrix, n=None, size=10):
    infos = []
    i = -1

    for i, iterable in enumerate(matrix):
        if n and i > n:
            i = n
            break

        for j, value in enumerate(iterable):
            if i == 0:
                infos.append(Types(size=size))
            info = infos[j]

            t = infer(value)
            info.incr(t)
            info.add(t, i, value)
    else:
        i += 1

    for info in infos:
        info.set_total(i)
    return infos


# Built-in converters

import re
from datetime import datetime

DATE_FORMATS = (
    '%Y-%m-%d',
    '%m-%d-%Y',
    '%m/%d/%Y',
    '%m.%d.%Y',
    '%m-%d-%y',
    '%B %d, %Y',
    '%B %d, %y',
    '%b %d, %Y',
    '%b %d, %y',
)

TIME_FORMATS = (
    '%H:%M:%S',
    '%H:%M',
    '%I:%M:%S %p',
    '%I:%M %p',
    '%I:%M',
)


true_re = re.compile(r'^(t(rue)?|yes)$', re.I)
false_re = re.compile(r'^(f(alse)?|no)$', re.I)


def convert_int(s):
    return int(s)


def convert_float(s):
    return float(s)


def convert_bool(s):
    if true_re.match(s):
        return True
    if false_re.match(s):
        return False
    raise ValueError


def convert_datetime(s, date_formats=DATE_FORMATS, time_formats=TIME_FORMATS):
    for df in date_formats:
        for tf in time_formats:
            for sep in (' ', 'T'):
                f = '{0}{1}{2}'.format(df, sep, tf)
                try:
                    return datetime.strptime(s, f)
                except ValueError:
                    pass
    raise ValueError


def convert_date(s, date_formats=DATE_FORMATS):
    for f in date_formats:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise ValueError


def convert_time(s, time_formats=TIME_FORMATS):
    for f in time_formats:
        try:
            return datetime.strptime(s.upper(), f).time()
        except ValueError:
            pass
    raise ValueError


register_converter('int', convert_int)
register_converter('float', convert_float)
register_converter('bool', convert_bool)
register_converter('date', convert_date)
register_converter('time', convert_time)
register_converter('datetime', convert_datetime)
