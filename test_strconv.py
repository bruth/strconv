#!/usr/bin/env python

import unittest
import strconv
from datetime import datetime, date, time


class ConvertTestCase(unittest.TestCase):
    def test_convert(self):
        self.assertEqual(strconv.convert('-3'), -3)
        self.assertEqual(strconv.convert('+0.4'), 0.4)
        self.assertEqual(strconv.convert('true'), True)
        self.assertEqual(strconv.convert('3/20/2013'), date(2013, 3, 20))
        self.assertEqual(strconv.convert('5:40 PM'), time(17, 40, 0))
        self.assertEqual(strconv.convert('March 4, 2013 5:40 PM'),
                         datetime(2013, 3, 4, 17, 40, 0))

    def test_convert_series(self):
        self.assertEqual(list(strconv.convert_series(['+0.4'])), [0.4])

    def test_convert_matrix(self):
        self.assertEqual(list(strconv.convert_matrix([['+0.4']])), [(0.4,)])


class InferTestCase(unittest.TestCase):
    def test_infer(self):
        self.assertEqual(strconv.infer('-3'), 'int')
        self.assertEqual(strconv.infer('+0.4'), 'float')
        self.assertEqual(strconv.infer('true'), 'bool')
        self.assertEqual(strconv.infer('3/20/2013'), 'date')
        self.assertEqual(strconv.infer('5:40 PM'), 'time')
        self.assertEqual(strconv.infer('March 4, 2013 5:40 PM'), 'datetime')

    def test_infer_series(self):
        info = strconv.infer_series(['+0.4', '1.0', '0.'])
        self.assertEqual(info.most_common(), [('float', 3)])
        self.assertEqual(info.types['float'].freq(), 1.0)

    def test_infer_matrix(self):
        info1, info2, info3 = strconv.infer_matrix([['+0.4', 'true', '50']])
        self.assertEqual(info1.most_common(), [('float', 1)])
        self.assertEqual(info1.types['float'].freq(), 1.0)


class ConverterTestCase(unittest.TestCase):
    def test_convert_int(self):
        self.assertEqual(strconv.convert_int('0'), 0)
        self.assertEqual(strconv.convert_int('1'), 1)
        self.assertEqual(strconv.convert_int('+1'), 1)
        self.assertEqual(strconv.convert_int('-1'), -1)

    def test_convert_float(self):
        self.assertEqual(strconv.convert_float('0.'), 0.0)
        self.assertEqual(strconv.convert_float('+.0'), 0.0)
        self.assertEqual(strconv.convert_float('-.0'), 0.0)
        self.assertEqual(strconv.convert_float('1.'), 1.0)
        self.assertEqual(strconv.convert_float('+1.'), 1.0)
        self.assertEqual(strconv.convert_float('-1.'), -1.0)

    def test_convert_bool(self):
        self.assertEqual(strconv.convert_bool('t'), True)
        self.assertEqual(strconv.convert_bool('true'), True)
        self.assertEqual(strconv.convert_bool('yes'), True)
        self.assertEqual(strconv.convert_bool('f'), False)
        self.assertEqual(strconv.convert_bool('false'), False)
        self.assertEqual(strconv.convert_bool('no'), False)

    def test_convert_date(self):
        self.assertEqual(strconv.convert_date('2013-03-01'), date(2013, 3, 1))
        self.assertEqual(strconv.convert_date('2013-3-1'), date(2013, 3, 1))
        self.assertEqual(strconv.convert_date('3-1-2013'), date(2013, 3, 1))
        self.assertEqual(strconv.convert_date('3/1/2013'), date(2013, 3, 1))
        self.assertEqual(strconv.convert_date('3.1.2013'), date(2013, 3, 1))
        self.assertEqual(strconv.convert_date('Mar 1, 2013'), date(2013, 3, 1))

    def test_convert_time(self):
        self.assertEqual(strconv.convert_time('01:30'), time(1, 30, 0))
        self.assertEqual(strconv.convert_time('1:30'), time(1, 30, 0))
        self.assertEqual(strconv.convert_time('1:30:40'), time(1, 30, 40))
        self.assertEqual(strconv.convert_time('15:30:40'), time(15, 30, 40))
        self.assertEqual(strconv.convert_time('5:30:40 AM'), time(5, 30, 40))

    def test_convert_datetime(self):
        self.assertEqual(strconv.convert_datetime('Mar 1, 2013T5:30:40 AM'),
                         datetime(2013, 3, 1, 5, 30, 40))
        self.assertEqual(strconv.convert_datetime('Mar 1, 2013 5:30:40 AM'),
                         datetime(2013, 3, 1, 5, 30, 40))



if __name__ == '__main__':
    unittest.main()
