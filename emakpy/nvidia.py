import contextlib
import os
import pathlib
import subprocess
import time
from xml.etree import ElementTree
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
        self.lockfile = self.workdir / 'lock'
        self.polling_interval = 60

    @contextlib.contextmanager
    def get_device(self):
        with FileLock(self.lockfile):
            with self.queuefile.open(mode='a') as f:
                f.write('{}\n'.format(os.getpid()))

        while True:
            time.sleep(self.polling_interval)
            with FileLock(self.lockfile):
                que = self.queuefile.read_text().split()
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

            with FileLock(self.lockfile):
                current = self.workdir / str(available_id)
                if current.exists() and current.read_text():
                    continue

                self.queuefile.write_text('\n'.join(que[1:]))
                current.write_text(str(os.getpid()))
                break

        yield available_id

        with FileLock(self.lockfile):
            current.write_text("")
