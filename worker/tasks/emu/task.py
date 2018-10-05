import codecs
import json
import os
import shutil
from tempfile import mkdtemp

from bson import ObjectId

from worker.config import logger
from worker.tasks.emu.Config import get_config
from worker.tasks.emu.feat import run_feat
from worker.tasks.emu.segmentation import segmentation_to_emu_annot
from worker.tasks.emu.zip import make_archive


def get_file(db, file_id):
    input_res = db.clarin.resources.find_one({'_id': ObjectId(file_id)})
    if 'file' in input_res and input_res['file']:
        return input_res['file']
    else:
        return None


feats = ['forest', 'ksvF0', 'rmsana']


def package(work_dir, project_id, db):
    proj = db.clarin.emu.find_one({'_id': ObjectId(project_id)})
    if not proj:
        raise RuntimeError('project not found')

    if 'deleted' in proj:
        raise RuntimeError('project deleted')

    dir = mkdtemp(suffix='_emuDB', dir=work_dir)
    proj_name = os.path.basename(dir)[:-6]

    logger.info(u'Saving CTM in {} (zip)...'.format(dir))

    config = get_config(proj_name, feats)
    with codecs.open(os.path.join(dir, u'{}_DBconfig.json'.format(proj_name)), mode='w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

    sessions = {}
    for bundle_id, bundle in proj['bundles'].iteritems():
        if 'audio' not in bundle or 'seg' not in bundle:
            continue

        b = {'name': bundle['name'], 'audio': os.path.join(work_dir, get_file(db, bundle['audio'])),
             'ctm': os.path.join(work_dir, get_file(db, bundle['seg']))}

        if not b['audio'] or not b['ctm']:
            continue

        sess = bundle['session']
        if sess not in sessions:
            sessions[sess] = []
        sessions[sess].append(b)

    for sess, bndls in sessions.items():
        sess_dir = os.path.join(dir, u'{}_ses'.format(sess))
        os.mkdir(sess_dir)
        for bndl in bndls:
            bndl_dir = os.path.join(sess_dir, u'{}_bndl'.format(bndl['name']))
            os.mkdir(bndl_dir)
            bndl_basnam = os.path.join(bndl_dir, bndl['name'])
            shutil.copy(bndl['audio'], os.path.join(bndl_dir, bndl_basnam + u'.wav'))
            # save_annot(bndl['ctm'], bndl_basnam + u'_annot.json', bndl['name'])
            annot = segmentation_to_emu_annot(bndl['ctm'], bndl['name'])
            with codecs.open(bndl_basnam + u'_annot.json', mode='w', encoding='utf-8') as f:
                json.dump(annot, f, indent=4)
            run_feat(feats, bndl_basnam + u'.wav')

    make_archive(dir, dir + u'.zip')
    shutil.rmtree(dir)
    return dir + u'.zip'
