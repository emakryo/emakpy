import pathlib
import unittest
import emakpy.nvidia


class TestNvidiaInfo(unittest.TestCase):
    def setUp(self):
        self.xml_path = pathlib.Path(__file__).resolve().parent / 'ns.xml'
        self.nvi = emakpy.nvidia.NvidiaInfo(self.xml_path)

    def test_n_gpus(self):
        self.assertEqual(self.nvi.n_gpus, 1)

    def test_is_available_0(self):
        self.assertFalse(self.nvi.is_available(0))

    def test_is_available_1(self):
        with self.assertRaises(ValueError):
            self.nvi.is_available(1)
