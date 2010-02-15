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

s_[ÀÁÂÃÄÅÅÄĀĂĄ]_A_g
s_Æ_AE_g
s_æ_ae_g

s_̈́[åäāăą]_a_g

s_[ÇĆĈĊČ]_C_g
s_[ćĉċč]_c_g

s_[ĎĐ]_D_g
s_[ďđ]_d_g

s_[ÈÉÊËĒĔĖĘĚ]_E_g
s_[èéêëēĕėęě]_e_g

s_[ĜĞĠĢ]_g_g
s_[ĝğġģ]_g_g

s_[ĤĦ]_h_g
s_[ĥħ]_h_g

s_[ĨĪĬĮİÌÍÎÏ]_I_g
s_[ĩīĭįıìíîï]_i_

s_Ĳ_IJ_g
s_ĳ_ij_g

s_Ĵ_J_g
s_ĵ_j_g

s_[Ķĸ]_K_g
s_[ķ]_k_g

s_[ĹĻĽĿŁ]_L_g
s_[ĺļľŀł]_l_g

s_[ŃŅŇŊ]_N_g
s_[ńņňŉŋ]_n_g

s_[ŌŎŐÒÓÔÕÖØ]_O_g
s_[ōŏőòóôõöø]_o_g

s_Œ_CE_g
s_œ_oe_g

s_[ŔŖŘ]_R_g
s_[ŕŗř]_r_g

s_[ŚŜŞŠ]_S_g
s_[śŝşš]_s_g

s_[ŢŤŦ]_T_g
s_[ţťŧ]_t_g

s_[ŨŪŬŮŰŲÙÚÛÜ]_U_g
s_[ũūŭůűųùúûü]_u_g

s_[Ŵ]_W_g
s_[ŵ]_w_g

s_[ŶŸÝ]_Y_g
s_[ŷÿý]_y_g

s_[ŹŻŽ]_Z_g
s_[źżž]_z_g

s_ſ_f_g

#whitespacespace to underscore
# first character is a nobr-space
s/[  \t\n]/_/g

s_[✝†]_cross_g
s_™_tm_g
s_©_c_g
s_®_r_g
s_«_<<_g
s_»_>>_g
s_¹_1_g
s_²_2_g
s_³_3_g
s_&_n_g
#string to lowercase
s_([A-Z])_\l\1_g
# / with -
s_\/_\-_g
# remove multiple underscores
s/_+/_/g
# remove multiple dots
s/\.+//g
#replace with nothing
s_(%|'|"|`|,|:|;|\(|\)|\[|\]|\+|\?|\*|~|\!)__g
#Remove 'whitespace' in the beginning and in the end
s/_+$//
s/^_+//
