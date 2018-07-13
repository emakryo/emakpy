import subprocess
from xml.etree import ElementTree


class NvidiaInfo:
    def __init__(self, filename=None):
        if filename:
            with open(filename) as f:
                self.raw = f.read()
        else:
            command = "nvidia-smi -q -x"
            ret = subprocess.run(command.split(),
                                 stdout=subprocess.PIPE, check=True)
            self.raw = ret.stdout

        self.str = self.raw.decode(
                'unicode_escape').encode().decode('unicode_escape')
        self.info = ElementTree.fromstring(self.str)

    @property
    def n_gpus(self):
        return int(self.info.findall('attached_gpus')[0].text)

    def available(self, gpu_index):
        if gpu_index >= self.n_gpus:
            raise ValueError(
                'Invalid gpu_index: {} >= #GPU(s), {}'.format(
                    gpu_index, self.n_gpus))

        gpu_info = self.info.findall('gpu')[gpu_index]
        return len(gpu_info.find('processes')) == 0
