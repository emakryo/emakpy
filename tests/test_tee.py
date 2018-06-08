import unittest
from emakpy import Tee

class TestTee(unittest.TestCase):
    def test_tee(self):
        tmpfile = "a.txt"

        print("pohe")
        with Tee(tmpfile):
            print("hoge")

        print("foo")

        with open(tmpfile) as f:
            self.assertEqual(f.readline().strip(), "hoge")
            self.assertEqual(f.readline(), "")
