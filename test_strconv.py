#!/usr/bin/env python

import unittest
import strconv
from datetime import datetime, time


class StrConvTestCase(unittest.TestCase):
    def test_infer_int(self):
        self.assertEqual(strconv.infer('0'), 'int')
        self.assertEqual(strconv.infer('1'), 'int')
        self.assertEqual(strconv.infer('+1'), 'int')
        self.assertEqual(strconv.infer('-1'), 'int')

    def test_infer_float(self):
        self.assertEqual(strconv.infer('0.'), 'float')
        self.assertEqual(strconv.infer('+.0'), 'float')
        self.assertEqual(strconv.infer('-.0'), 'float')
        self.assertEqual(strconv.infer('1.'), 'float')
        self.assertEqual(strconv.infer('+1.'), 'float')
        self.assertEqual(strconv.infer('-1.'), 'float')

    def test_infer_bool(self):
        self.assertEqual(strconv.infer('t'), 'bool')
        self.assertEqual(strconv.infer('true'), 'bool')
        self.assertEqual(strconv.infer('TRUE'), 'bool')
        self.assertEqual(strconv.infer('f'), 'bool')
        self.assertEqual(strconv.infer('false'), 'bool')
        self.assertEqual(strconv.infer('FALSE'), 'bool')
        self.assertEqual(strconv.infer('yes'), 'bool')
        self.assertEqual(strconv.infer('no'), 'bool')

    def test_infer_date(self):
        self.assertEqual(strconv.infer('2013-03-01'), 'date')
        self.assertEqual(strconv.infer('2013-3-1'), 'date')
        self.assertEqual(strconv.infer('3-1-2013'), 'date')
        self.assertEqual(strconv.infer('3/1/2013'), 'date')
        self.assertEqual(strconv.infer('3.1.2013'), 'date')
        self.assertEqual(strconv.infer('Mar 1, 2013'), 'date')

    def test_infer_time(self):
        self.assertEqual(strconv.infer('01:30'), 'time')
        self.assertEqual(strconv.infer('1:30'), 'time')
        self.assertEqual(strconv.infer('1:30:40'), 'time')
        self.assertEqual(strconv.infer('15:30:40'), 'time')
        self.assertEqual(strconv.infer('5:30:40 AM'), 'time')

    # Performs all permutatins of the above date and times
    def test_infer_datetime(self):
        self.assertEqual(strconv.infer('Mar 1, 2013T5:30:40 AM'), 'datetime')
        self.assertEqual(strconv.infer('Mar 1, 2013 5:30:40 AM'), 'datetime')

    def test_convert(self):
        self.assertEqual(strconv.convert('+0.4'), 0.4)
        self.assertEqual(strconv.convert('-3'), -3)
        self.assertEqual(strconv.convert('true'), True)
        self.assertEqual(strconv.convert('5:40 PM'), time(17, 40, 0))
        self.assertEqual(strconv.convert('March 4, 2013 5:40 PM'),
                         datetime(2013, 3, 4, 17, 40, 0))


if __name__ == '__main__':
    unittest.main()
