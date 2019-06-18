from pathlib import Path
from shutil import rmtree
from subprocess import run, STDOUT, CalledProcessError
from tempfile import mkdtemp, NamedTemporaryFile
from typing import Dict

from worker.config import logger, speech_tools_path, work_dir, tmp_dir


def run_tool(tool_name: str, wav_file: Path, aux_file: any, output_file: Path):
    tmp_subdir = Path(mkdtemp(dir=tmp_dir))

    cmd = ['bash', str(speech_tools_path / 'tools' / tool_name / 'run.sh'), '--dist-path',
           str(speech_tools_path / 'dist'),
           '--tmp-path', str(tmp_subdir), str(wav_file)]
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


def forcealign(task: Dict[str, any]) -> Path:
    audio = work_dir / task['input']['audio']
    txt = work_dir / task['input']['text']
    output = get_temp_file(work_dir, '.ctm')
    try:
        run_tool('ForcedAlign', audio, txt, output)
    except RuntimeError:
        logger.warn('Forced align failed! Retrying with Segment...')
        return segmentalign(task)
    return output.relative_to(work_dir)


def segmentalign(task: Dict[str, any]) -> Path:
    audio = work_dir / task['input']['audio']
    txt = work_dir / task['input']['text']
    output = get_temp_file(work_dir, '.ctm')
    run_tool('SegmentAlign', audio, txt, output)
    return output.relative_to(work_dir)


def recognize(task: Dict[str, any]) -> Path:
    audio = work_dir / task['input']
    output = get_temp_file(work_dir, '.txt')
    run_tool('Recognize', audio, None, output)
    return output.relative_to(work_dir)


def diarize(task: Dict[str, any]) -> Path:
    audio = work_dir / task['input']
    output = get_temp_file(work_dir, '.ctm')
    run_tool('SpeakerDiarization', audio, None, output)
    return output.relative_to(work_dir)


def vad(task: Dict[str, any]) -> Path:
    audio = work_dir / task['input']
    output = get_temp_file(work_dir, '.ctm')
    run_tool('SpeechActivityDetection', audio, None, output)
    return output.relative_to(work_dir)


def kws(task: Dict[str, any]) -> Path:
    audio = work_dir / task['input']['audio']
    keywords = work_dir / task['input']['keywords']
    output = get_temp_file(work_dir, '.txt')
    run_tool('KeywordSpotting', audio, keywords, output)
    return output.relative_to(work_dir)
