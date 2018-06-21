"""
Tests for Fadapa.
"""

import sys
import unittest
try:
    from StringIO import StringIO
except:
    from io import StringIO


from fadapa import Fadapa, FastqcDataError
import warnings

class TestFadapa(object):

    def test_summary(self):
        summary = self.p_data.summary()
        self.assertEqual(summary[0], ['Module Name', 'Status'])

    def test_content(self):
        sys.stdout = StringIO()
        self.p_data.content()
        self.assertEqual(sys.stdout.getvalue()[:8], '##FastQC')

    def test_raw_data(self):
        data = self.p_data.raw_data('Basic Statistics')
        self.assertEqual(data[-1], '>>END_MODULE')

    def test_cleaned_data(self):
        data = self.p_data.clean_data('Basic Statistics')
        self.assertEqual(data[0][0], 'Measure')

class TestFadapaTxt(unittest.TestCase, TestFadapa) :

    def setUp(self):
        self.p_data = Fadapa('tests/fastqc_data.txt')

class TestFadapaZip(unittest.TestCase, TestFadapa) :

    def setUp(self):
        self.p_data = Fadapa('tests/fastqc.zip')

class TestFadapaEmptyZip(unittest.TestCase) :

    def test_fastqc_data_not_found(self):
        with self.assertRaises(FastqcDataError) :
            Fadapa('tests/empty.zip')

class TestFadapaMultipleDataZip(unittest.TestCase) :

    def test_multi_data(self):
        with warnings.catch_warnings(record=True) as w :
            warnings.simplefilter('always')
            Fadapa('tests/fastqc_multiple.zip')
            self.assertEqual(len(w),1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertTrue('Multiple files' in str(w[-1].message))
            self.assertTrue('Choosing one_fastqc_data.txt' in str(w[-1].message))
            self.assertTrue('Choosing two_fastqc_data.txt' not in str(w[-1].message))

class TestFadapaFp(unittest.TestCase, TestFadapa) :

    def setUp(self):
        with open('tests/fastqc_data.txt') as fp :
            self.p_data = Fadapa(fp)
