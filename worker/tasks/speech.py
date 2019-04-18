from pathlib import Path
from shutil import rmtree
from subprocess import run, STDOUT, CalledProcessError
from tempfile import mkdtemp, NamedTemporaryFile

from worker.config import logger, speech_tools_path


def run_tool(tool_name: str, wav_file: Path, aux_file: Path, output_file: Path, work_dir: Path):
    tmp_dir = Path(mkdtemp(dir=work_dir))

    cmd = ['bash', f'tools/{tool_name}/run.sh', '--dist-path', str(speech_tools_path / 'dist'),
           '--tmp-path', str(tmp_dir), str(wav_file)]
    if aux_file:
        cmd.append(str(aux_file))
    cmd.append(str(output_file))

    with open(str(output_file) + '_log.txt', 'w') as log:
        logger.info(f'Running {" ".join(cmd)}')
        try:
            run(cmd, stdout=log, stderr=STDOUT, check=True, cwd=speech_tools_path)
        except CalledProcessError:
            raise RuntimeError(f'error running script for {output_file}')
        # finally:
        #     rmtree(str(tmp_dir))

    if not output_file.exists():
        raise RuntimeError(f'{output_file} missing')


def get_temp_file(dir, suffix):
    with NamedTemporaryFile(dir=dir, suffix=suffix, delete=False) as f:
        return Path(f.name)


def forcealign(work_dir: Path, audio: str, txt: str) -> Path:
    output = get_temp_file(work_dir, '.ctm')
    try:
        run_tool('ForcedAlign', work_dir / audio, work_dir / txt, output, work_dir)
    except RuntimeError:
        logger.warn('Forced align failed! Retrying with Segment...')
        return segmentalign(work_dir, audio, txt)
    return output


def segmentalign(work_dir: Path, audio: str, txt: str) -> Path:
    output = get_temp_file(work_dir, '.ctm')
    run_tool('SegmentAlign', work_dir / audio, work_dir / txt, output, work_dir)
    return output


def recognize(work_dir: Path, audio: str) -> Path:
    output = get_temp_file(work_dir, '.txt')
    run_tool('Recognize', work_dir / audio, None, output, work_dir)
    return output


def diarize(work_dir: Path, audio: str) -> Path:
    output = get_temp_file(work_dir, '.ctm')
    run_tool('SpeakerDiarization', work_dir / audio, None, output, work_dir)
    return output


def vad(work_dir: Path, audio: str) -> Path:
    output = get_temp_file(work_dir, '.ctm')
    run_tool('SpeechActivityDetection', work_dir / audio, None, output, work_dir)
    return output


def kws(work_dir: Path, audio: str, keywords: str) -> Path:
    output = get_temp_file(work_dir, '.txt')
    run_tool('KeywordSpotting', work_dir / audio, work_dir / keywords, output, work_dir)
    return output
