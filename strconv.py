# strconv.py
# Copyright (c) 2013 Byron Ruth
# BSD License
from __future__ import unicode_literals, print_function

__version__ = '0.1.0'

import re
from datetime import datetime

true_re = re.compile(r'^(t(rue)?|yes)$', re.I)
false_re = re.compile(r'^(f(alse)?|no)$', re.I)

TYPES = (
    'int',
    'float',
    'bool',
    'date',
    'datetime',
    'time',
    'unicode',
)

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


class TypeInfo(object):
    def __init__(self, t, size=None, total=None):
        self.type = t
        self.count = 0
        self.sample = []
        self.size = size
        self.total = total
        self.sample_set = set()

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
            return 100 * self.size / float(self.total)

    def __repr__(self):
        return '<{0}: {1} n={2}>'.format(self.__class__.__name__, self.type,
                                         self.count)


class Types(object):
    def __init__(self, size=None, total=None):
        self.size = size
        self.total = None
        self.types = {}

    def incr(self, t, n=1):
        self.types.setdefault(t, TypeInfo(t, self.size, self.total))
        self.types[t].incr(n)

    def add(self, t, i, value):
        self.types.setdefault(t, TypeInfo(t, self.size, self.total))
        self.types[t].add(i, value)

    def set_total(self, total):
        self.total = total
        for k in self.types:
            self.types[k].total = total

    def most_common(self, n=None):
        if n is None:
            n = len(self.types)
        types = [(t, i) for t, i in self.types.items()][:n]
        types.sort(key=lambda x: x[1].count, reverse=True)
        return types

    def __bytes_(self):
        return '\n'.join(self.summary())

    def __repr__(self):
        types = self.most_common()
        label = ', '.join(['{0}={1}'.format(t, i.count) for t, i in types])
        return '<{0}: {1}>'.format(self.__class__.__name__, label)


class Detector(object):
    def __init__(self, types=TYPES, date_formats=DATE_FORMATS,
                 time_formats=TIME_FORMATS, empties=('',)):

        self.types = types
        self.date_formats = date_formats
        self.time_formats = time_formats
        self.empties = empties

        # methods
        self._converters = {}
        for t in types:
            self._converters[t] = getattr(self, 'to_{0}'.format(t))

    def to_int(self, v):
        return int(v)

    def to_float(self, v):
        return float(v)

    def to_bool(self, v):
        if true_re.match(v):
            return True
        if false_re.match(v):
            return False
        raise ValueError

    def to_datetime(self, v):
        for df in self.date_formats:
            for tf in self.time_formats:
                for sep in (' ', 'T'):
                    f = '{0}{1}{2}'.format(df, sep, tf)
                    try:
                        return datetime.strptime(v, f)
                    except ValueError:
                        pass
        raise ValueError

    def to_date(self, v):
        for f in self.date_formats:
            try:
                return datetime.strptime(v, f).date()
            except ValueError:
                pass
        raise ValueError

    def to_time(self, v):
        for f in self.time_formats:
            try:
                return datetime.strptime(v.upper(), f).time()
            except ValueError:
                pass
        raise ValueError

    def to_unicode(self, v):
        return unicode(v)

    def convert(self, value):
        for _t in self.types:
            try:
                return self._converters[_t](value)
            except ValueError:
                pass
        return value

    def infer(self, value, real=False):
        for _t in self.types:
            try:
                _value = self._converters[_t](value)
                if real:
                    return type(_value)
                else:
                    return _t
            except ValueError:
                pass

    def infer_series(self, iterable, n=None, size=10, empties=None):
        info = Types(size)

        # Empty values are marked as empty types
        if empties is None:
            empties = self.empties
        elif not isinstance(empties, (list, tuple)):
            empties = (empties,)

        for i, value in enumerate(iterable):
            if n and i > n:
                break

            if value in empties:
                t = '_'
            else:
                t = self.infer(value)

            info.incr(t)
            info.add(t, i, value)

        info.set_total(i)
        return info

    def infer_matrix(self, matrix, n=None, size=10, empties=None):
        infos = []

        # Empty values are marked as empty types
        if empties is None:
            empties = self.empties
        elif not isinstance(empties, (list, tuple)):
            empties = (empties,)

        for i, iterable in enumerate(matrix):
            if n and i > n:
                break

            for j, value in enumerate(iterable):
                if i == 0:
                    infos.append(Types(size))
                info = infos[j]

                if value in empties:
                    t = '_'
                else:
                    t = self.infer(value)

                info.incr(t)
                info.add(t, i, value)

        for info in infos:
            info.set_total(i)
        return infos


def summary(info):
    types = info.most_common()
    lines = []
    for t, i in types:
        lines.append('type: {0}'.format(t))
        lines.append('count: {0} ({1:.2f}%)'.format(i.count, i.freq()))
        lines.append('example: {0}'.format(i.sample[0][1]))
        lines.append('')
    lines.pop()
    return lines


def print_summary(infos):
    summaries = [summary(x) for x in infos]

    height = max(len(s) for s in summaries)
    width = max(len(l) for block in summaries for l in block) + 2

    for j in xrange(height):
        line = []
        for s in summaries:
            if j < len(s):
                line.append(s[j].ljust(width))
            else:
                line.append('')
        print(''.join(line))


detector = Detector()
infer = detector.infer
infer_series = detector.infer_series
infer_matrix = detector.infer_matrix
convert = detector.convert
