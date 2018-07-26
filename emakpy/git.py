import subprocess


def hash(full=False):
    if full:
        command = "git rev-parse HEAD"
    else:
        command = "git rev-parse --short HEAD"

    return subprocess.run(
         command.split(), stdout=subprocess.PIPE).stdout.decode().strip()
