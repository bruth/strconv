# strconv 

Library for inferring and converting strings into native Python types. The original use case for this was reading CSV data with unknown types and converting it into the inferred types so it be further manipulated.

## Install

```
pip install strconv
```

## Usage

### Conversion

**convert(s, include_type=False)**

Attempts to convert string `s` into a non-string type. If `include_type` is true, the type name is returned as a second value.

```python
>>> import strconv
>>> strconv.convert('1.2')
1.2
>>> strconv.convert('true')
True
>>> strconv.convert('2013-03-01', include_type=True)
(date(2013, 3, 1), 'date')
```

**convert_series(i, include_type=False)**

Takes an interable and returns a generator. Each value will be converted independently. If `include_type` is true, each value will be paired with it's type name.

```python
>>> list(strconv.convert_series(['1', '1.2', 't', '2013-01-01']))
[1, 1.2, True, date(2013, 1, 1)]
```

**convert_matrix(m, include_type=False)**

Takes a matrix (iterable of iterables) and returns a generator. Each value will be converted independently. If `include_type` is true, each value will be paired with it's type name.

_A CSV reader can be directly passed into this function._

```python
>>> import csv
>>> r = csv.reader(open('data.csv', 'rb'))
>>> for row in strconv.convert_matrix(r):
...     ...
```

### Inference

These functions are merely convenience wrappers for the above `convert*` functions to return only the converter type or the converted value's type.

**infer(s, converted=False)**

Returns the converter's type of the string value. If `converted` is true, the type of the converted value will be returned.

```python
>>> strconv.infer('1')
'int'
>>> strconv.infer('1', converted=True)
int
```

**infer_series(i, n=None, size=10)**

Infers the types of a series of values. The original use case for this was to take a column of data and infer all the teypes that exist in the data. This would confirm whether the data contains heterogeneous values.

The output of this is a `Types` instance which stores information and a sample of the values for inspection. If `n` is an integer, only N values will be evaluated. `size` is the number of values per type that will be stored as a sample set for inspection (greater `size` == more memory).

```python
>>> info = strconv.infer_series(['10', '5', '', '-1'])
>>> info
<Types: int=3, unknown=1>
>>> info.most_common(1)
[('int', 3)]
>>> info.types['int'].freq()
0.75
```

**infer_matrix(m, n=None, size=10)**

Same as `infer_series` except it will take a matrix of values. Type information will be stored per column not per row. The output will be a list of `Types` instances of lenght M where `m` is of size NxM.

```python
>>> import csv
>>> r = csv.reader(open('data.csv', 'rb'))
>>> col_types = strconv.infer_matrix(r)
```

## Converters

Converters are registered by some name and are evaluated in order. Converters should be ordered from the most specific + less complex to the least specific + most complex since once a value matches, further evaluation is stopped. Below are the built-in converters listed in order.

- `int`
- `float`
- `bool` - case-insensitive conversion: `t`, `true`, `yes` to `True` and `f`, `false`, `no` to `False`
- `date` - see `strconv.DATE_FORMATS` for the default date formats
- `time` - see `strconv.TIME_FORMATS` for the default time formats
- `datetime` - converts using each combination of the date and time formats with either `T` or a single space as the separate, e.g. '2013-03-20T13:05:32'

## Customize

Type inference of strings is a very difficult thing to generalize. Often times there is subtle nuances to the data that require domain knowledge in order to infer the correct type. `strconv` makes it as simple as possible to customize the behavior of the inference and conversion.

**Register Converter**

```python
>>> def convert_none(s):
...     if s.upper() in ('\N', 'NA', 'N/A', '', 'UNK'):
...         return
...     raise ValueError
...
>>> strconv.register_converter('none', convert_none, priority=0)
>>> list(strconv.convert_series(['\N', '', 'na', 'unk']))
[None, None, None, None]
```
