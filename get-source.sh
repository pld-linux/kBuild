#!/bin/sh
# Usage:
# ./get-source.sh
# Author: Elan Ruusamäe <glen@pld-linux.org>

p=kBuild
svn=http://svn.netlabs.org/repos/kbuild/trunk

revno=$1
specfile=$p.spec

set -e
svn co $svn${revno:+@$revno} $p
svnrev=$(svnversion $p)
tar=$p-r$svnrev.tar.bz2
tar -cjf $tar --exclude-vcs --exclude kBuild/bin $p
../dropin $tar

sed -i -e "
	s/^\(%define[ \t]\+svnrev[ \t]\+\)[0-9]\+\$/\1$svnrev/
" $specfile
../md5 $p.spec
