# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

inherit subversion distutils

DESCRIPTION="a music syncronizer"
HOMEPAGE="http://sourceforge.net/projects/musync"
#SRC_URI="svn://ostcon.org/musync/trunk"

LICENSE=""
SLOT="0"
KEYWORDS=""
IUSE=""

DEPEND="
>=dev-lang/python-2.3
>=media-libs/mutagen-1.12
"
RDEPEND=""

ESVN_REPO_URI="https://musync.svn.sourceforge.net/svnroot/trunk"
S=${WORKDIR}/trunk
SRC_URI="${COMMON_URI}"

src_unpack() {
	subversion_src_unpack
}

pkg_postinst() {
	echo
	echo "Please look into /usr/share/musync for auxilliary files"
	echo
}
