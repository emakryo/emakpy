import contextlib
import os
import pathlib
import subprocess
import time
from xml.etree import ElementTree
import psutil
from filelock import FileLock


class NvidiaInfo:
    def __init__(self, filename=None):
        self.filename = filename

    def update(self):
        if self.filename:
            with open(self.filename) as f:
                self.str = f.read()
        else:
            command = "nvidia-smi -q -x"
            ret = subprocess.run(command.split(),
                                 stdout=subprocess.PIPE, check=True)
            self.str = ret.stdout.decode(
                    'unicode_escape').encode().decode('unicode_escape')

        self.info = ElementTree.fromstring(self.str)

    @property
    def n_gpus(self):
        self.update()
        return int(self.info.find('attached_gpus').text)

    def is_available(self, gpu_index):
        self.update()
        if gpu_index >= self.n_gpus:
            raise ValueError(
                'Invalid gpu_index: {} >= #GPU(s), {}'.format(
                    gpu_index, self.n_gpus))

        gpu_info = self.info.findall('gpu')[gpu_index]
        return len(gpu_info.find('processes')) == 0


class WorkQueue:
    def __init__(self, dirname='~/.nv_que'):
        self.workdir = pathlib.Path(dirname).expanduser()
        self.workdir.mkdir(exist_ok=True)
        self.queuefile = self.workdir / 'que'
        self.queuefile.touch()
        self.lockfile = self.workdir / 'lock'
        self.lock = FileLock(self.lockfile)
        self.polling_interval = 10

    def count(self):
        self.eliminate_non_exist()
        with self.lock:
            return len(self.queuefile.read_text().split())

    def eliminate_non_exist(self):
        with self.lock:
            que = self.queuefile.read_text().split()
            que_exists = [pid for pid in que if psutil.pid_exists(int(pid))]
            if len(que) > len(que_exists):
                self.queuefile.write_text('\n'.join(que_exists))

            for i in range(NvidiaInfo().n_gpus):
                current = self.workdir / str(i)
                if not current.exists():
                    continue

                pid = current.read_text()
                if not pid:
                    continue

                if not psutil.pid_exists(int(pid)):
                    current.write_text('')

    @contextlib.contextmanager
    def get_device(self):
        with self.lock:
            with self.queuefile.open(mode='a') as f:
                f.write('{}\n'.format(os.getpid()))

        wait = False
        while True:
            if wait:
                time.sleep(self.polling_interval)
                wait = True

            self.eliminate_non_exist()
            with self.lock:
                que = self.queuefile.read_text().split()
                print(os.getpid(), que, flush=True)
                if int(que[0]) != os.getpid():
                    continue

            nv = NvidiaInfo()
            available_id = None
            for i in range(nv.n_gpus):
                if nv.is_available(i):
                    available_id = i
                    break

            if available_id is None:
                continue

            with self.lock:
                current = self.workdir / str(available_id)
                if current.exists() and current.read_text():
                    continue

                que = self.queuefile.read_text().split()
                self.queuefile.write_text('\n'.join(que[1:]))
                current.write_text(str(os.getpid()))
                break

        yield available_id

        with self.lock:
            current.write_text("")
