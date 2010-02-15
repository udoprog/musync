#
# Musync meta - used to handle music-files metadata.
#
# author: John-John Tedro
# version: 2008.1
# Copyright (C) 2007 Albin Stjerna, John-John Tedro
#
#    This file is part of Musync.
#
#    Musync is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Musync is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Musync.  If not, see <http://www.gnu.org/licenses/>.

#imports
import traceback;

#partials
from mutagen.easyid3 import EasyID3;
from mutagen.id3 import ID3FileType;
from mutagen.apev2 import APEv2File;
from mutagen.oggvorbis import OggFileType;
from mutagen.mp3 import MP3;
from mutagen.mp4 import MP4;
from mutagen.flac import FLAC;

from musync.errors import WarningException
from musync.errors import FatalException;
from musync.opts import Settings;
from musync.subp import sanitize_with_filter;
from mutagen import File;

#emergency stuff
from mutagen.id3 import TXXX;
from mutagen.id3 import TDOR;

# 
#
#
#
#

blankmeta = {
        'artist': None,
        'album': None,
        'track': None,
        'date': None,
        'title': None
    };

def easyapev2(f):
    """
    takes an apev2 tagged file and returns something that is not insane.
    """

    global blankmeta;

    dictionary = {
        "year": "date"
    };

    ameta = blankmeta.copy();

    # check all keys in lowercase and match against template.
    for k in f:
        if k.lower() in ameta.keys():
            ameta[k.lower()] = [unicode(f[k])];
    
    return ameta;

def easytags(f):
    """
    get sane metadata from an insane file type.
    """
    dictionary = {
        "\xa9art": "artist",
        "\xa9alb": "album",
        "\xa9day": "date",
        "\xa9nam": "title",
        "trkn": "track",
        "year": "date"
    };

    ameta = blankmeta.copy();
    
    for k in f.tags.keys():
        key = k.lower();
        # dictionary replace all keys
        if key in dictionary:
            key = dictionary[key];

        # set keys in template
        if key in ameta.keys():
            if type(f.tags[k]) == list:
                ameta[key] = f.tags[k];
            else:
                ameta[k.lower()] = [unicode(f[k])];
    
    if ameta["track"] is not None:
        # nice hack to workaround the fact that the retarded file _often_
        # contains a tuple.
        if type(ameta["track"][0]) == tuple: 
            ameta["track"] = [unicode(ameta["track"][0][0])];
    
    print ameta;
    return ameta;

def extractkey(p, key):
    """
    this is bugbug
    """

    for v in p.tags.values():
        if isinstance(v, TXXX):
            if v.desc.lower() == key:
                return v.text;
        elif key == "date" and isinstance(v, TDOR):
            return v.text;
    
    return None;

def openaudio(p):
    """
    Opens audiofiles in an attempt to read their metadata.
    @param p musync.commons.Path object describing the file.
    @throws WarningException when file-extension of p is unsupported.
    """
    audio = None;

    #check before to simplify exception throwing.
    #these are the hardcoded extensions that mutagen supports.
    #if p.ext not in ["flac","ogg","mp3"]:
    #    raise WarningException( "unknown extension '%s' - %s"%(p.ext, p.path) );

    ameta = {
        'artist': None,
        'album': None,
        'track': None,
        'tracknumber': None,
        'date': None,
        'title': None
    };

    translate = {
        'tracknumber': 'track'
    };
    
    f = File(p.path);
    
    if f is None:
        raise WarningException("Unknown file type: %s"%(p.path));

    if isinstance(f, ID3FileType):
        audio = EasyID3(p.path);
        if "audio/mp3" in f.mime:
            p.ext = "mp3";
        else:
            raise WarningException("unimplemented file type %s: [%s]"%(type(f), f.mime));
    elif isinstance(f, OggFileType):
        audio = f;
        if "audio/vorbis" in f.mime:
            p.ext = "ogg";
        else:
            raise WarningException("unimplemented file type %s: [%s]"%(type(f), f.mime));
    elif isinstance(f, FLAC):
        audio = f;
        p.ext = "flac";
    elif isinstance(f, MP4):
        audio = easytags(f);
        p.ext = "mp4";
    elif isinstance(f, APEv2File):
        audio = easyapev2(f);
        if "audio/ape" in f.mime:
            p.ext = "ape";
        else:
            raise WarningException("unimplemented file type %s: [%s]"%(type(f), f.mime));
    else:
        raise WarningException("unsupported file type %s: [%s]"%(type(f), f.mime));

    #this is not good.
    if audio is None:
        raise FatalException("file contains no metadata");
    
    for k in  ameta.keys():
        if k in audio.keys():
            ameta[k] = audio[k];

    # translate brainfucked keys.
    for k in translate.keys():
        if ameta[k] is not None:
            ameta[translate[k]] = ameta[k];
            del(ameta[k]);

    # try to force the data out of the retard file.
    for k in ameta:
        if ameta[k] is None:
            ameta[k] = extractkey(f, k);
    
    if Settings["debug"]:
        print ameta;
    
    return ameta;

def readmeta(p):
    """
    Makes an attempt to read metadata from a file.
    @param p musync.commons.Path object describing the file.
    """

    meta={"album":None, "artist":None, "title":None, "track":None, "year":0};
    audio = openaudio(p);

    for key in audio.keys():
        if audio[key] is None:
            continue;

        to_key = key;
        from_key = key;
        # corrections go here
        if key in ["date"]:
            to_key = "year";
        
        # these are the keys that we can use
        if to_key not in meta.keys():
            continue;

        # try to read from file.
        try:
            meta[to_key] = audio[from_key][0];
        except Exception, e:
            raise FatalException("metadata corrupt - %s"%(p.path));

    # apply modifications
    for k in Settings["modify"]:
        if Settings["modify"][k]:
            meta[k] = Settings["modify"][k];
    
    for field in ["album", "artist", "title", "track", "year"]:
        if meta[field] is None:
            if Settings["no-fixme"]:
                meta[field] = unicode("");
            else:
                raise WarningException("fixme - %s"%(p.path));
    
    return meta;

def cleanmeta(meta):
    """
    Cleans up metadata and makes it ready for expansion.
    @param meta Dictionary containing all metadata keys.
    """
    
    try:
        track = meta["track"];
        #some tags like to be track/#of tracks, take care of them here
        if track.find('/') > -1:
            meta["track"] = int(
                track[ 0 : track.find('/') ]
            );
        else:
            meta["track"] = int(track);
    except Exception, e:
        raise FatalException("cannot use tracknumber");
    
    nomatch = True;

    for date in Settings["dateformat"].split("|"):
        import time;
        
        try:
            d = time.strptime(meta["year"], date);
        except Exception, e:
            continue;
        
        nomatch = False;
        meta["year"] = d[0];
        break;

    if nomatch:
        meta["year"] = 0;
    
    # no plan for this section yet, keep along...
    #sanitize all strings
    for key in ["artist","album","title"]:
        meta[key] = sanitize_with_filter(meta[key], key);
        # FIXME: clean meta
        #meta[key] = "cleaned!";
    return meta;

