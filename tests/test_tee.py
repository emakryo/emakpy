import os
import tempfile
import unittest
from emakpy import Tee

class TestTee(unittest.TestCase):
    def test_tee(self):

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfilename = os.path.join(tmpdir, "a.txt")

            print("pohe")
            with Tee(tmpfilename):
                print("hoge", flush=True)

            print("foo")

            with open(tmpfilename) as f:
                self.assertEqual(f.readline().strip(), "hoge")
                self.assertEqual(f.readline(), "")
