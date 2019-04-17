import json
import shutil
from pathlib import Path
from tempfile import mkdtemp

from bson import ObjectId

from worker.config import logger
from worker.tasks.emu.Config import get_config
from worker.tasks.emu.feat import run_feat
from worker.tasks.emu.segmentation import segmentation_to_emu_annot
from worker.tasks.emu.zip import make_archive


def get_file(db, file_id: str, work_dir: Path) -> Path:
    input_res = db.clarin.resources.find_one({'_id': ObjectId(file_id)})
    if 'file' in input_res and input_res['file']:
        return work_dir / input_res['file']
    else:
        return None


feats = ['forest', 'ksvF0', 'rmsana']


def package(work_dir: Path, project_id: str, db) -> Path:
    proj = db.clarin.emu.find_one({'_id': ObjectId(project_id)})
    if not proj:
        raise RuntimeError('project not found')

    if 'deleted' in proj:
        raise RuntimeError('project deleted')

    dir = Path(mkdtemp(suffix='_emuDB', dir=work_dir))
    proj_name = str(dir.name)[:-6]

    logger.info(f'Saving CTM in {dir} (zip)...')

    config = get_config(proj_name, feats)
    with open(dir / f'{proj_name}_DBconfig.json', 'w') as f:
        json.dump(config, f, indent=4)

    sessions = {}
    for bundle_id, bundle in proj['bundles'].iteritems():
        if 'audio' not in bundle or 'seg' not in bundle:
            continue

        b = {'name': bundle['name'], 'audio': get_file(db, bundle['audio'], work_dir),
             'ctm': get_file(db, bundle['seg'], work_dir)}

        if not b['audio'] or not b['ctm']:
            continue

        sess = bundle['session']
        if sess not in sessions:
            sessions[sess] = []
        sessions[sess].append(b)

    for sess, bndls in sessions.items():
        sess_dir = dir / f'{sess}_ses'
        sess_dir.mkdir()
        for bndl in bndls:
            bndl_dir = sess_dir / f'{bndl["name"]}_bndl'
        bndl_dir.mkdir()
        bndl_basnam = bndl_dir / bndl['name']
        shutil.copy(bndl['audio'], bndl_basnam.with_suffix('.wav'))
        # save_annot(bndl['ctm'], bndl_basnam + u'_annot.json', bndl['name'])
        annot = segmentation_to_emu_annot(bndl['ctm'], bndl['name'])
        with open(bndl_basnam.with_suffix('_annot.json'), 'w') as f:
            json.dump(annot, f, indent=4)
        run_feat(feats, bndl_basnam.with_suffix('.wav'))

    make_archive(dir, dir.with_suffix('.zip'))
    shutil.rmtree(dir)
    return dir.with_suffix('.zip')
