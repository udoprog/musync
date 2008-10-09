# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

inherit subversion distutils

DESCRIPTION="A sleek music synchronizer written in python"
HOMEPAGE="http://sf.net/projects/musync"
#SRC_URI="https://musync.svn.sf.net/svnroot/musync/trunk"

IUSE="bash-completion"
LICENSE="GPL-3"
SLOT="0"
KEYWORDS="M~"

DEPEND="
>=dev-lang/python-2.3
>=media-libs/mutagen-1.12
"
RDEPEND="
	>=dev-lang/python-2.3
	|| ( >=dev-lang/python-2.5 >=dev-python/ctypes-0.9 )
	>=media-libs/mutagen-1.12"

DEPEND="${RDEPEND}"

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
