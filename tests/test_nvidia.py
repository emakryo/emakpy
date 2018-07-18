import datetime
import multiprocessing
import os
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


class TestWorkQueue(unittest.TestCase):
    def test_empry(self):
        que = emakpy.nvidia.WorkQueue()
        self.assertEqual(que.count(), 0)

    def test_get_device(self):
        que = emakpy.nvidia.WorkQueue()
        with que.get_device() as gpu:
            self.assertEqual(gpu, 0)

        self.assertEqual(que.count(), 0)

    def test_multiple_process(self):
        n_process = 3
        q = multiprocessing.Queue()
        ps = [multiprocessing.Process(
                target=f, args=(i, q)) for i in range(n_process)]
        for p in ps:
            p.start()

        for p in ps:
            p.join()

        a = q.get()
        for _ in range(n_process-1):
            b = q.get()
            self.assertGreater((b-a).total_seconds(), 5)
            a = b


def f(i, queue):
    with emakpy.nvidia.WorkQueue().get_device():
        queue.put(datetime.datetime.now())


if __name__ == "__main__":
    unittest.main()
