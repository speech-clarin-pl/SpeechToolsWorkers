from pathlib import Path
from subprocess import run


def make_archive(dir: Path, archive: Path):
    cmd = ['zip', '-r', archive, dir.name]
    run(cmd, cwd=dir.parent, check=True)
