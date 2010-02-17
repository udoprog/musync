import mutagen
import mutagen.id3
import mutagen.flac;

import musync.formats.id3;
import musync.formats.oggvorbis;
import musync.formats.mp4;

def open(path, **kw):
    f = mutagen.File(path);
    
    if not f:
        return None;

    tags = f.tags;
    o = None;
    
    if isinstance(tags, mutagen.id3.ID3):
        o = musync.formats.id3.ID3MetaFile(f, tags);
    elif isinstance(tags, mutagen.oggvorbis.OggVCommentDict):
        o = musync.formats.oggvorbis.OggVCommentMetaFile(f, tags);
    elif isinstance(tags, mutagen.flac.VCFLACDict):
        o = musync.formats.oggvorbis.VCFLACMetaFile(f, tags);
    elif isinstance(tags, mutagen.mp4.MP4Tags):
        o = musync.formats.mp4.MP4TagsMetaFile(f, tags);
    else:
        return None;
    
    for k in kw.keys():
        if kw[k] is None:
            continue;
        
        setattr(o, k, kw[k]);
    
    return o;
