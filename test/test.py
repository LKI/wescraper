import subprocess
import json
import unittest
import os.path as op

class TestWeScraper(unittest.TestCase):
    scraper =  op.join(op.dirname(op.dirname(op.realpath(__file__))), 'wechat-scraper', 'scraper.py')

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
