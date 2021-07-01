from pathlib import Path
from shutil import rmtree
from subprocess import STDOUT, run, CalledProcessError
from tempfile import mkdtemp, NamedTemporaryFile

from worker.config import speech_tools_path, tmp_dir, logger


def run_tool(tool_name: str, main_file: Path, aux_file: any, output_file: Path):
    tmp_subdir = Path(mkdtemp(dir=tmp_dir))

    cmd = ['bash', str(speech_tools_path / 'tools' / tool_name / 'run.sh'), '--dist-path',
           str(speech_tools_path / 'dist'),
           '--tmp-path', str(tmp_subdir), str(main_file)]
    if aux_file:
        cmd.append(str(aux_file))
    cmd.append(str(output_file))

    with open(str(output_file) + '_log.txt', 'w') as log:
        logger.info(f'Running {" ".join(cmd)}')
        try:
            run(cmd, stdout=log, stderr=STDOUT, check=True, cwd=speech_tools_path)
        except CalledProcessError:
            raise RuntimeError(f'error running script for {output_file}')
        finally:
            if tmp_subdir.exists():
                rmtree(str(tmp_subdir))

    if not output_file.exists():
        raise RuntimeError(f'{output_file} missing')


def get_temp_file(dir, suffix):
    with NamedTemporaryFile(dir=dir, suffix=suffix, delete=False) as f:
        return Path(f.name)
