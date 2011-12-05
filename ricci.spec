###############################################################################
#
# Copyright (C) 2006-2010 Red Hat, Inc. All rights reserved.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License version 2.
#
###############################################################################

Name: ricci
Version: 0.16.2
Release: 13%{?dist}
License: GPLv2
URL: http://sources.redhat.com/cluster/conga/
Group: System Environment/Base
Summary: Remote Cluster and Storage Management System
Source0: http://people.redhat.com/rmccabe/conga/fedora/src/ricci-0.16.2.tar.gz
Patch0: bz580575.patch
Patch1: bz585126.patch
Patch2: bz587526.patch
Patch3: bz553384.patch
Patch4: bz610042.patch
Patch5: bz612318.patch
Patch6: bz617090.patch
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: libxml2-devel python-devel libcap-devel
BuildRequires: openssl-devel dbus-devel pkgconfig file-devel nss-devel
BuildRequires: cyrus-sasl-devel >= 2.1

ExclusiveArch: i686 x86_64

Requires: oddjob dbus openssl cyrus-sasl >= 2.1 file nss-tools
# modstorage
Requires: parted

Requires(post): chkconfig initscripts
Requires(preun): chkconfig initscripts
Requires(postun): initscripts

%prep
%setup -q
%patch0 -p2
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1 -b .bz610042
%patch5 -p1 -b .bz612318
%patch6 -p1 -b .bz617090

%build
%configure --arch=%{_arch} --docdir=%{_docdir}
make %{?_smp_mflags} ricci

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install_ricci

%clean
rm -rf %{buildroot}

%description
ricci is a cluster and storage management and configuration
daemon. The ricci daemon, dispatches incoming messages to
underlying management modules.

This package contains the listener daemon (dispatcher), as well as
reboot, rpm, storage, service, virtual machine, and log management modules.

%files
%defattr(-,root,root)
%{_bindir}/ccs_sync
%{_mandir}/*/*

# ricci
%config(noreplace)	%{_sysconfdir}/pam.d/ricci
%config(noreplace)	%{_sysconfdir}/oddjobd.conf.d/ricci.oddjob.conf
%config(noreplace)	%{_sysconfdir}/dbus-1/system.d/ricci.systembus.conf
			%{_sysconfdir}/rc.d/init.d/ricci
%attr(-,ricci,ricci)	%{_localstatedir}/lib/ricci
			%{_sbindir}/ricci
%attr(-,root,ricci)	%{_libexecdir}/ricci/
			%{_docdir}/ricci-%{version}/
# modrpm
%config(noreplace)	%{_sysconfdir}/oddjobd.conf.d/ricci-modrpm.oddjob.conf
%config(noreplace)	%{_sysconfdir}/dbus-1/system.d/ricci-modrpm.systembus.conf
			%{_libexecdir}/ricci-modrpm

# modstorage
%config(noreplace)	%{_sysconfdir}/oddjobd.conf.d/ricci-modstorage.oddjob.conf
%config(noreplace)	%{_sysconfdir}/dbus-1/system.d/ricci-modstorage.systembus.conf
			%{_libexecdir}/ricci-modstorage

# modservice
%config(noreplace)	%{_sysconfdir}/oddjobd.conf.d/ricci-modservice.oddjob.conf
%config(noreplace)	%{_sysconfdir}/dbus-1/system.d/ricci-modservice.systembus.conf
			%{_libexecdir}/ricci-modservice

# modlog
%config(noreplace)	%{_sysconfdir}/oddjobd.conf.d/ricci-modlog.oddjob.conf
%config(noreplace)	%{_sysconfdir}/dbus-1/system.d/ricci-modlog.systembus.conf
			%{_libexecdir}/ricci-modlog

# modvirt
%config(noreplace)	%{_sysconfdir}/oddjobd.conf.d/ricci-modvirt.oddjob.conf
%config(noreplace)	%{_sysconfdir}/dbus-1/system.d/ricci-modvirt.systembus.conf
			%{_libexecdir}/ricci-modvirt

%pre
/usr/sbin/groupadd -g 140 ricci 2> /dev/null
/usr/sbin/useradd -u 140 -g 140 -d /var/lib/ricci -s /sbin/nologin -r \
	-c "ricci daemon user" ricci 2> /dev/null
exit 0

%post
DBUS_PID=`cat /var/run/messagebus.pid 2>/dev/null`
/bin/kill -s SIGHUP $DBUS_PID >&/dev/null
/sbin/service oddjobd reload >&/dev/null
/sbin/chkconfig --add ricci
exit 0

%preun
if [ "$1" == "0" ]; then
	/sbin/service ricci stop >&/dev/null
	/sbin/chkconfig --del ricci
fi
exit 0

%postun
if [ "$1" == "0" ]; then
	DBUS_PID=`cat /var/run/messagebus.pid 2>/dev/null`
	/bin/kill -s SIGHUP $DBUS_PID >&/dev/null
	/sbin/service oddjobd reload >&/dev/null
fi
if [ "$1" == "1" ]; then
	/sbin/service ricci condrestart >&/dev/null
fi
exit 0

%changelog
* Mon Jul 26 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-13
- Fix issue with incorrect package/service lists for RHEL6
- Resolves: rhbz#617090

* Thu Jul 08 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-9
- Ricci will now start even if IPv6 is disabled
- Resolves: rhbz#612318

* Wed Jul 07 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-8
- Added a missing man page for ccs_sync
- Resolves: rhbz#610042

* Thu Jun 03 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-7
- Init script should now fully comply with Fedora Guidelines
- Resolves: rhbz#553384

* Tue May 18 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-6
- Init script now complies more closely with Fedora Guidelines
- Passing a bad node to ccs_sync no longer results in a segfault
- Resolves: rhbz#585126 rhbz#587526

* Mon May 17 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-5
- Added static UID/GID for ricci user
- Resolves: rhbz#585987

* Wed May 12 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.16.2-4
- Do not build on ppc and ppc64.
  Resolves: rhbz#591001

* Tue Apr 27 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-3
- An issue with calling 'virsh nodelist' would cause ricci to hang for
  30 seconds during most requests resulting in timeouts to the web interface.
- Resolves: rhbz#580575

* Thu Feb 25 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.16.2-2
- Resolves: rhbz#568013
- Do not build ricci on s390 and s390x.

* Thu Jan 14 2010 Ryan McCabe <rmccabe@redhat.com> - 0.16.2-1
- make the ricci init script exit with status 2 when invalid arguments
  are provided

* Thu Dec 10 2009 Ryan McCabe <rmccabe@redhat.com> - 0.16.1-6
- Add a ricci function to set the cluster version, as it's no longer done
  while syncing the configuration files via ccs_sync.

* Wed Dec 09 2009 Ryan McCabe <rmccabe@redhat.com> - 0.16.1-5
- Don't update the cluster version via cman_set_version

* Wed Sep 16 2009 Tomas Mraz <tmraz@redhat.com> - 0.16.1-4
- Use password-auth common PAM configuration instead of system-auth

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 0.16.1-3
- rebuilt with new openssl

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Apr 16 2009 Ryan McCabe <rmccabe@redhat.com> 0.16.1-1
- More updates for cluster3.

* Tue Apr 07 2009 Ryan McCabe <rmccabe@redhat.com> 0.16.0-2
- Fix memory corruption bug.
- Update package and service list.
- Add missing dependency for nss-tools

* Mon Mar 30 2009 Ryan McCabe <rmccabe@redhat.com> 0.16.0-1
- Update for F11
- Fix build issues uncovered by g++ 4.4
- Remove legacy RHEL4 and RHEL5-specific code.

* Tue Mar 03 2009 Caolán McNamara <caolanm@redhat.com> - 0.15.0-11
- include stdio.h for perror, stdint.h for uint32_t

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.15.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> 0.15.0-9
- rebuild with new openssl

* Wed Oct 22 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-8
- Fix build.

* Wed Oct 22 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-7
- Fix a bug that caused some connections to be dropped prematurely.
- Add better error reporting in the "ccs_sync" tool.

* Wed Oct 15 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-6
- When setting a cluster.conf file with ccs_sync, only try to update the cman cluster version if the node is a member of a cluster.

* Mon Oct 06 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-5
- Generate the ricci NSS certificate database at startup if it doesn't exist
- By default, set the "propagate" attribute to true when setting a new cluster
  configuration file with "ccs_sync"

* Fri Sep 26 2008 Fabio M. Di Nitto <fdinitto@redhat.com> 0.15.0-4
- Drop BuildRequires on cman-devel as it's not required.

* Thu Sep 26 2008 Fabio M. Di Nitto <fdinitto@redhat.com> 0.15.0-3
- Add versioned BR on cman-devel

* Tue Sep 09 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-2
 - Add nss-devel to BuildDepends

* Tue Sep 09 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-1
 - Break circular dependency with cman

* Mon Jun 02 2008 Ryan McCabe <rmccabe@redhat.com> 0.13.0-4
 - No longer need -lgroup with the new cman packages.
 - Recognize F9 by name (Sulphur).

* Wed May 20 2008 Ryan McCabe <rmccabe@redhat.com> 0.13.0-3
 - Initial build

* Wed Mar 26 2008 Chris Feist <cfeist@redhat.com> 0.13.0-2
 - Don't require cap and xml libraries (RPM will find them)
 - Fix buildroot to meet Fedora standard

* Wed Feb 20 2008 Ryan McCabe <rmccabe@redhat.com> 0.13.0-1
 - Initial build.
