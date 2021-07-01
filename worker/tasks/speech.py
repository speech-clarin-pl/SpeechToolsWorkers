from pathlib import Path
from typing import Dict

from worker.config import logger, work_dir
from worker.tasks.tools import run_tool, get_temp_file


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
