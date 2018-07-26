import sys
from pathlib import Path
import emakpy.git


def save_dir(base_dir, make_dir=True):
    h = emakpy.git.hash()
    c = '_'.join(sys.argv).replace('/', '%')
    path = Path(base_dir) / (h + '_' + c)
    if make_dir:
        path.mkdir(parents=True)
    return path
