#
# Conditional build:
%bcond_with	bootstrap	# build boostrap
%bcond_without	verbose		# disable verbose build

%define		ver	0.1.9998
%define		svnrev	3598
Summary:	A cross-platform build environment
Summary(pl.UTF-8):	Wieloplatformowe środowisko budowania
Name:		kBuild
Version:	%{ver}.%{svnrev}
Release:	1
Group:		Development/Tools
# Most tools are from NetBSD, some are from FreeBSD, and make and sed are from GNU
License:	BSD and GPL v2+
Source0:	%{name}-r%{svnrev}.tar.bz2
# Source0-md5:	902991c327b2cc93cc6da642e70a08e2
Source1:	get-source.sh
Patch0:		%{name}-0.1.3-escape.patch
Patch1:		%{name}-0.1.5-pthread.patch
Patch2:		x32.patch
Patch3:		%{name}-bison.patch
Patch4:		quote-defs.patch
URL:		http://svn.netlabs.org/kbuild
BuildRequires:	acl-devel
BuildRequires:	bison
BuildRequires:	flex
%if %{with bootstrap}
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake >= 1:1.9
BuildRequires:	gettext-tools >= 0.14
BuildRequires:	texinfo >= 4.0
%else
BuildRequires:	kBuild
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%ifarch %{x8664} x32
%define		kbuild_arch	amd64
%else
%define		kbuild_arch	x86
%endif

%description
This is a GNU make fork with a set of scripts to simplify complex
tasks and portable versions of various UNIX tools to ensure
cross-platform portability.

The goals of the kBuild framework:
- Similar behavior across all supported platforms
- Flexibility, don't create unnecessary restrictions preventing ad-hoc
  solutions
- Makefiles can be simple to write and maintain
- One configuration file for a subtree automatically included
- Target configuration templates as the primary mechanism for makefile
  simplification
- Tools and SDKs for helping out the templates with flexibility
- Non-recursive makefile method by using sub-makefiles

%description -l pl.UTF-8
Ten pakiet to odgałęzienie GNU make'a wraz z zestawem skryptów
upraszczających złożone zadania oraz przenośnych wersji różnych 
narzędzi uniksowych w celu zapewnienia przenośności na wiele platform.

Cele środowiska kBuild to:
- podobne zachowanie na wszystkich obsługiwanych platformach
- elastyczność, unikanie niepotrzebnych ograniczeń blokujących
  rozwiązania doraźne
- proste do napisania i utrzymania pliki Makefile
- automatyczne dołączanie jednego pliku konfiguracyjnego na poddrzewo
- szablony konfiguracji docelowej jako główny mechanizm upraszczający
  pliki Makefile
- narzędzia i SDK wspomagające szablony elastycznością
- nierekurencyjny system wykorzystujący podpliki Makefile

%prep
%setup -qc
mv %{name} .tmp; mv .tmp/* .
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

cat > SvnInfo.kmk << EOF
KBUILD_SVN_REV := %{svnrev}
KBUILD_SVN_URL := http://svn.netlabs.org/repos/kbuild/trunk
EOF

%{__sed} -i -e 's@_LDFLAGS\.%{kbuild_arch}*.*=@& %{rpmldflags}@g' Config.kmk

%ifarch x32
# probably should add full x32 configuration
# but can't find place to submit code upstream, so this will do for now.
# but then again, forcing -m64 is bad and pointless
sed -i -e 's/-m64//' kBuild/tools/GCC64.kmk kBuild/tools/GXX64.kmk tests/Config.kmk Config.kmk
%endif

%build
%define bootstrap_mflags %{?_smp_mflags} %{?with_verbose:KBUILD_VERBOSE=2} \\\
		CC="%{__cc}" TOOL_GCC3_CC="%{__cc}" CFLAGS="%{rpmcflags}"

%define mflags %{bootstrap_mflags} \\\
		NIX_INSTALL_DIR=%{_prefix} \\\
		BUILD_TYPE=release \\\
		MY_INST_MODE=0644 \\\
		MY_INST_BIN_MODE=0755

ver=$(awk '/^KBUILD_VERSION =/{print $3}' Config.kmk)
test "$ver" = %{ver}

%if %{with bootstrap}
cd src/kmk
%{__aclocal} -I config
%{__autoconf}
%{__autoheader}
%{__automake}
cd ../sed
%{__gettextize}
%{__aclocal} -I config
%{__autoconf}
%{__autoheader}
%{__automake}
cd ../..

kBuild/env.sh --full \
	%{__make} -f bootstrap.gmk %{bootstrap_mflags} \
		AUTORECONF=:

kBuild/env.sh kmk clean
%endif

kBuild/env.sh kmk %{mflags} all \
	PATH_INS=$RPM_BUILD_ROOT

%install
rm -rf $RPM_BUILD_ROOT
kBuild/env.sh kmk %{mflags} install \
	PATH_INS=$RPM_BUILD_ROOT

# These are included later in files section
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc ChangeLog
%doc kBuild/doc/COPYING-FDL-1.3 kBuild/doc/QuickReference*
%attr(755,root,root) %{_bindir}/bld_signames
%attr(755,root,root) %{_bindir}/kDepIDB
%attr(755,root,root) %{_bindir}/kDepObj
%attr(755,root,root) %{_bindir}/kDepPre
%attr(755,root,root) %{_bindir}/kObjCache
%attr(755,root,root) %{_bindir}/kmk
%attr(755,root,root) %{_bindir}/kmk_append
%attr(755,root,root) %{_bindir}/kmk_ash
%attr(755,root,root) %{_bindir}/kmk_cat
%attr(755,root,root) %{_bindir}/kmk_chmod
%attr(755,root,root) %{_bindir}/kmk_cmp
%attr(755,root,root) %{_bindir}/kmk_cp
%attr(755,root,root) %{_bindir}/kmk_echo
%attr(755,root,root) %{_bindir}/kmk_expr
%attr(755,root,root) %{_bindir}/kmk_gmake
%attr(755,root,root) %{_bindir}/kmk_install
%attr(755,root,root) %{_bindir}/kmk_ln
%attr(755,root,root) %{_bindir}/kmk_md5sum
%attr(755,root,root) %{_bindir}/kmk_mkdir
%attr(755,root,root) %{_bindir}/kmk_mv
%attr(755,root,root) %{_bindir}/kmk_printf
%attr(755,root,root) %{_bindir}/kmk_redirect
%attr(755,root,root) %{_bindir}/kmk_rm
%attr(755,root,root) %{_bindir}/kmk_rmdir
%attr(755,root,root) %{_bindir}/kmk_sed
%attr(755,root,root) %{_bindir}/kmk_sleep
%attr(755,root,root) %{_bindir}/kmk_test
%attr(755,root,root) %{_bindir}/kmk_time
%attr(755,root,root) %{_bindir}/kmk_touch
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*.kmk
%dir %{_datadir}/%{name}/msgstyles
%{_datadir}/%{name}/msgstyles/*.kmk
%dir %{_datadir}/%{name}/sdks
%{_datadir}/%{name}/sdks/*.kmk
%dir %{_datadir}/%{name}/templates
%{_datadir}/%{name}/templates/*.kmk
%dir %{_datadir}/%{name}/tools
%{_datadir}/%{name}/tools/*.kmk
%dir %{_datadir}/%{name}/units
%{_datadir}/%{name}/units/*.kmk
