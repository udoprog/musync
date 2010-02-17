import mutagen.id3;

import meta;

class ID3MetaFile(meta.MetaFile):
    __translate__ = {
        'TALB': "album",
        'TDOR': "year",
        'TDRC': "year",
        'TXXX': "year",
        'TRCK': "track",
        'TPE1': "artist",
        'TIT2': "title",
    };
    
    def __init__(self, f, tags):
        meta.MetaFile.__init__(self, f, tags);

        if isinstance(self.year, mutagen.id3.ID3TimeStamp):
            self.year = self.year.year;
        
        if self.track:
            if "/" in self.track:
                self.track = int(self.track.split("/")[0]);
            else:
                self.track = int(self.track);
