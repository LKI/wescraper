import json
import os.path
import subprocess
import unittest

class TestWeScraper(unittest.TestCase):
    scraper = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'scraper.py')

    def test_test(self):
        self.assertEqual(1, 1)

    def test_account(self):
        p = subprocess.Popen(["python", self.scraper, "liriansu"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        a = json.loads(out)
        self.assertLess(8, len(a))
        self.assertEqual(7, len(a[0].keys()))
        self.assertIn(u'account', a[1].keys())
        self.assertEqual(u'\u82cf\u5b50\u5cb3', a[0][u'account'])

    def test_keyword(self):
        p = subprocess.Popen(["python", self.scraper, "all",  "liriansu"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        a = json.loads(out)
        self.assertEqual(10, len(a))
        self.assertEqual(7, len(a[0].keys()))
        self.assertIn(u'account', a[1].keys())

if __name__ == '__main__':
    unittest.main()
