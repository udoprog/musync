#this file is to be edited freely to suit your needs
#
# If you are interested in adding patching the the Musync project, please try to be as international as possible in your replacings.
# As you might just notice this file is only suited for utf-8 tags, you can fix that too!
#
# All strings are unicode, the goal is to get everyone accepted into ascii-land.
#
# this is done trough making sure that the string only consists of chars beginning with \x00
#
# If you ever stumble upon a filename looking like: test_is_we0x000x60rdest!
# look up the char at: http://jrgraphix.net/research/unicode_blocks.php
# then figure out the best way to treat it here.
#
# Note that the order of the bytes has been swapped to allow better overview here.
#

# ae and such
s_\x00(\xC0|\xC1|\xC2|\xC3|\xC4|\xC5|\xC6)_\x00A_g
s_\x00(\xE0|\xE1|\xE2|\xE3|\xE4|\xE5|\xE6)_\x00a_g
# oe
s_\x00(\xD2|\xD3|\xD4|\xD5|\xD6)_\x00O_g
s_\x00(\xF2|\xF3|\xF4|\xF5|\xF6)_\x00o_g
#e
s_\x00(\xC8|\xC9|\xCA|\xCB)_\x00E_g
s_\x00(\xE8|\xE9|\xEA|\xEB)_\x00e_g
#u
s_\x00(\xD9|\xDA|\xDB|\xDC)_\x00U_g
s_\x00(\xF9|\xFA|\xFB|\xFC)_\x00u_g
#whitespacespace to underscore
s_\x00(\x20|\xA0)_\x00\__g
# 

# cross
s_(\x00\x86|\x20\x20)_\x00c\x00r\x00o\x00s\x00s_g
# ^2
s_\x00\xB2_\x002_g
#replace with nothing
s_\x00('|"|`|,|:|;|\(|\)|\[|\]|\+|\?|\*|~|\!)__g
# and
s_\x00&_\x00n_g
#string to lowercase
s_\x00([A-Z])_\x00\l\1_g
# / with -
s_\x00\/_\x00-_g
# remove multiple underscores
s/(\x00\_)+/\x00\_/g
# remove multiple dots
s/(\x00\.)+//g
#Remove 'whitespace' in the beginning and in the end
s/(\x00_)*$//
s/^(\x00_)*//

