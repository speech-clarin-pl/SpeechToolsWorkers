from collections import OrderedDict
from uuid import uuid1

features = {'forest': {'name': 'Formants',
                       'columnName': 'fm',
                       'fileExtension': 'fms'},
            'ksvF0': {'name': 'Pitch',
                      'columnName': 'F0',
                      'fileExtension': 'f0'},
            'mhsF0': {'name': 'Pitch',
                      'columnName': 'F0',
                      'fileExtension': 'f0'},
            'rmsana': {'name': 'RMS',
                       'columnName': 'rms',
                       'fileExtension': 'rms'},
            'zcrana': {'name': 'ZeroCross',
                       'columnName': 'zcr',
                       'fileExtension': 'zcr'}
            }


def get_perspective(name, feats):
    perspective = OrderedDict()

    perspective['name'] = name

    sig_cnv = OrderedDict()
    perspective['signalCanvases'] = sig_cnv

    sig_cnv['order'] = ['OSCI', 'SPEC']
    sig_cnv['assign'] = []
    sig_cnv['contourLims'] = []

    if 'forest' in feats:
        assign_spec = OrderedDict()
        assign_spec['signalCanvasName'] = 'SPEC'
        assign_spec['ssffTrackName'] = 'Formants'

        formant_colors = OrderedDict()
        formant_colors['ssffTrackName'] = 'Formants'
        formant_colors['colors'] = ['rgb(255,100,100)', 'rgb(100,255,100)', 'rgb(100,100,255)', 'rgb(100,255,255)']

        sig_cnv['assign'].append(assign_spec)
        sig_cnv['contourColors'] = [formant_colors]

    if 'ksvF0' in feats or 'mhsF0' in feats:
        sig_cnv['order'].append('Pitch')

    if 'rmsana' in feats:
        sig_cnv['order'].append('RMS')

    if 'zcr' in feats:
        sig_cnv['order'].append('ZeroCross')

    lev_cnv = OrderedDict()
    perspective['levelCanvases'] = lev_cnv

    lev_cnv['order'] = ['Word', 'Phoneme']

    twodim_cnv = OrderedDict()
    perspective['twoDimCanvases'] = twodim_cnv

    twodim_cnv['order'] = []

    return perspective


def get_default_emu_config(feats):
    if not feats:
        feats = []

    config = OrderedDict()

    perspectives = []
    config['perspectives'] = perspectives

    perspectives.append(get_perspective('default', []))
    perspectives.append(get_perspective('full', feats))

    restrictions = OrderedDict()
    config['restrictions'] = restrictions

    restrictions['showPerspectivesSidebar'] = True

    buttons = OrderedDict()
    config['activeButtons'] = buttons

    buttons['saveBundle'] = True
    buttons['showHierarchy'] = True

    return config


def getLevel(name, labelname, itemtype='SEGMENT', labeltype='STRING'):
    level = OrderedDict()

    level['name'] = name
    level['type'] = itemtype

    attrs = []
    level['attributeDefinitions'] = attrs

    if not type(labelname) is list:
        labelname = [labelname]

    for label in labelname:
        attr = OrderedDict()
        attrs.append(attr)

        attr['name'] = label
        attr['type'] = labeltype

    return level


def getLink(from_level, to_level, type='ONE_TO_MANY'):
    link = OrderedDict()
    link['type'] = type
    link['superlevelName'] = from_level
    link['sublevelName'] = to_level
    return link


def get_config(name, feats):
    config = OrderedDict()

    config['name'] = name
    config['UUID'] = str(uuid1())
    config['mediafileExtension'] = 'wav'

    tracks = []
    config['ssffTrackDefinitions'] = tracks

    if feats:
        for feat in feats:
            if feat in features:
                tracks.append(features[feat])
            else:
                print 'Warning: feature not recognized -- {}'.format(feat)

    levels = []
    config['levelDefinitions'] = levels

    levels.append(getLevel('Utterance', 'Utterance', itemtype='ITEM'))
    levels.append(getLevel('Word', 'Word'))
    # levels.append(getLevel('Syllable', ['Syllable', 'Stress'], itemtype='ITEM'))
    # levels.append(getLevel('Phonetic Syllable', ['Syllable', 'Stress'], itemtype='ITEM'))
    levels.append(getLevel('Phoneme', ['Phoneme', 'SAMPA', 'IPA']))

    links = []
    config['linkDefinitions'] = links

    links.append(getLink('Utterance', 'Word'))
    # links.append(getLink('Word', 'Syllable'))
    # links.append(getLink('Word', 'Phonetic Syllable'))
    # links.append(getLink('Syllable', 'Phoneme'))
    # links.append(getLink('Phonetic Syllable', 'Phoneme'))
    links.append(getLink('Word', 'Phoneme'))

    config['EMUwebAppConfig'] = get_default_emu_config(feats)

    return config
