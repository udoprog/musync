import mutagen.mp4;
import mutagen.id3;

# |      '<A9>nam' -- track title
# |      '<A9>alb' -- album
# |      '<A9>ART' -- artist
# |      'aART' -- album artist
# |      '<A9>wrt' -- composer
# |      '<A9>day' -- year
# |      '<A9>cmt' -- comment
# |      'desc' -- description (usually used in podcasts)
# |      'purd' -- purchase date
# |      '<A9>grp' -- grouping
# |      '<A9>gen' -- genre
# |      '<A9>lyr' -- lyrics
# |      'purl' -- podcast URL
# |      'egid' -- podcast episode GUID
# |      'catg' -- podcast category
# |      'keyw' -- podcast keywords
# |      '<A9>too' -- encoded by
# |      'cprt' -- copyright
# |      'soal' -- album sort order
# |      'soaa' -- album artist sort order
# |      'soar' -- artist sort order
# |      'sonm' -- title sort order
# |      'soco' -- composer sort order
# |      'sosn' -- show sort order
# |      'tvsh' -- show name

import meta;

class MP4TagsMetaFile(meta.MetaFile):
    __translate__ = {
        '\xa9nam': "title",
        '\xa9alb': "album",
        '\xa9ART': "artist",
        'aART': "artist",
        #'sonm': "track",
        'trkn': "track",
        'purd': "year",
        '\xa9day': "year",
    };
    
    def __init__(self, f, tags):
        meta.MetaFile.__init__(self, f, tags);

        if self.track:
            self.track = self.track[0];
        
        # mp4 is not documented, but it seems to have the same format as
        # ID3TimeStamp (subset of ISO 8601)
        if self.year:
            self.year = mutagen.id3.ID3TimeStamp(self.year).year;
