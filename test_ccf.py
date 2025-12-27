import unittest
import os
import csv
import struct
from writer import CCFWriter
from reader import CCFReader
from exceptions import CCFError, CCFColumnError
from constants import TYPE_INT, TYPE_FLOAT, TYPE_STRING

class TestCCF(unittest.TestCase):
    def setUp(self):
        self.test_ccf = 'test_suite.ccf'
        self.test_csv = 'test_suite_input.csv'
        
    def tearDown(self):
        if os.path.exists(self.test_ccf):
            os.remove(self.test_ccf)
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def create_csv_data(self, headers, rows):
        with open(self.test_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
    def test_basic_cycle(self):
        headers = ['name', 'age', 'score']
        rows = [
            ['Alice', '30', '95.5'],
            ['Bob', '25', '80.0']
        ]
        
        # Write
        writer = CCFWriter(self.test_ccf)
        writer.write(headers, rows)
        
        # Read
        reader = CCFReader(self.test_ccf)
        self.assertEqual(reader.nrows, 2)
        
        data = reader.read_columns()
        self.assertEqual(data['name'], ['Alice', 'Bob'])
        self.assertEqual(data['age'], [30, 25])
        self.assertEqual(data['score'], [95.5, 80.0])
        
    def test_types(self):
        headers = ['i', 'f', 's']
        rows = [
            ['1', '1.1', 'one'],
            ['2', '2.2', 'two']
        ]
        writer = CCFWriter(self.test_ccf)
        writer.write(headers, rows)
        
        reader = CCFReader(self.test_ccf)
        # Check inferred types
        schema_dict = dict(reader.schema)
        self.assertEqual(schema_dict['i'], TYPE_INT)
        self.assertEqual(schema_dict['f'], TYPE_FLOAT)
        self.assertEqual(schema_dict['s'], TYPE_STRING)
        
        data = reader.read_columns()
        self.assertEqual(data['i'], [1, 2])
        self.assertAlmostEqual(data['f'][0], 1.1)
        
    def test_partial_read(self):
        headers = ['c1', 'c2', 'c3']
        rows = [['a', 'b', 'c']]
        writer = CCFWriter(self.test_ccf)
        writer.write(headers, rows)
        
        reader = CCFReader(self.test_ccf)
        data = reader.read_columns(['c2'])
        self.assertIn('c2', data)
        self.assertNotIn('c1', data)
        self.assertEqual(data['c2'], ['b'])
        
    def test_missing_column(self):
        headers = ['c1']
        rows = [['val']]
        writer = CCFWriter(self.test_ccf)
        writer.write(headers, rows)
        
        reader = CCFReader(self.test_ccf)
        with self.assertRaises(CCFColumnError):
            reader.read_columns(['non_existent'])

    def test_empty_file(self):
        # Header only, no rows
        headers = ['c1']
        rows = []
        writer = CCFWriter(self.test_ccf)
        writer.write(headers, rows)
        
        reader = CCFReader(self.test_ccf)
        self.assertEqual(reader.nrows, 0)
        data = reader.read_columns()
        self.assertEqual(data['c1'], [])

if __name__ == '__main__':
    unittest.main()
