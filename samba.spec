%define enable_japanese 1

%define initdir /etc/rc.d/init.d
%define auth %(test -f /etc/pam.d/system-auth && echo /etc/pam.d/system-auth || echo)
%define jpver ja-1.2a

Summary: Samba SMB server.
Name: samba
Version: 2.0.7
Release: 21sslj1
Copyright: GNU GPL Version 2
Group: System Environment/Daemons
#Source: ftp://us2.samba.org/pub/samba/samba-%{version}.tar.gz
# Source 
Source: http://www.samba.gr.jp/pub/samba-jp/samba-2.0.7-ja/samba-%{version}-%{jpver}.tar.bz2
Source1: samba.log
Source2: samba.xinetd
Patch: samba-makefilepath.patch
Patch1: smbw.patch
Patch2: samba-glibc21.patch
Patch3: samba-2.0.7-fixinit.patch
Patch4: samba-autoconf.patch
Patch5: samba-2.0.5a-gawk.patch
Patch6: samba-smbprint.patch
Patch7: samba-logrotate.patch
Patch8: samba-ia64.patch
Patch9: samba-2.0.7-system-auth.patch
Patch10: samba-2.0.7-smb.conf.rh.patch
Patch11: samba-2.0.7-nocups.patch
Patch12: samba-2.0.7-smbadduser.patch
Patch13: samba-2.0.7-krb5-1.2.patch
Patch14: samba-2.0.7-ssl.patch
# Japanese patch
Patch20: samba-autoconf-jp.patch
Requires: pam >= 0.64 %{auth} samba-common = %{version} 
Requires: logrotate >= 3.4
BuildPrereq: openssl-devel, krb5-devel
BuildRoot: %{_tmppath}/samba-root
Prereq: /sbin/chkconfig /bin/mktemp /usr/bin/killall
Prereq: fileutils sed /etc/init.d 

%description
Samba provides an SMB server which can be used to provide network
services to SMB (sometimes called "Lan Manager") clients, including
various versions of MS Windows, OS/2, and other Linux machines. Samba
uses NetBIOS over TCP/IP (NetBT) protocols and does NOT need NetBEUI
(Microsoft Raw NetBIOS frame) protocol.

Samba-2 features an almost working NT Domain Control capability and
includes the new SWAT (Samba Web Administration Tool) that allows
samba's smb.conf file to be remotely managed using your favourite web
browser. For the time being this is being enabled on TCP port 901 via
xinetd.

Please refer to the WHATSNEW.txt document for fixup information.  This
binary release includes encrypted password support.  Please read the
smb.conf file and ENCRYPTION.txt in the docs directory for
implementation details.

NOTE: Red Hat Linux 5.X Uses PAM which has integrated support for
Shadow passwords. Do NOT recompile with the SHADOW_PWD option
enabled. Red Hat Linux has built in support for quotas in PAM.

%package client
Summary: Samba (SMB) client programs.
Group: Applications/System
Requires: samba-common = %{version}
Obsoletes: smbfs

%description client
The samba-client package provides some SMB clients to complement the
built-in SMB filesystem in Linux. These clients allow access of SMB
shares and printing to SMB printers.

%package common
Summary: Files used by both Samba servers and clients.
Group: Applications/System

%description common
Samba-common provides files necessary for both the server and client
packages of Samba.

%prep
%setup -q -n samba-%{version}-%{jpver}
%patch -p1 -b .makefile
%patch1 -p1 -b .smbw
%patch2 -p1 -b .glibc21
%patch3 -p1 -b .fixinit
%if %{enable_japanese}
%patch20 -p1 -b .autoconf-jp
%else
%patch4 -p1 -b .autoconf
%endif
%patch5 -p1 -b .gawk
%patch6 -p1 -b .smbprint
%patch7 -p1 -b .logrotate
%patch8 -p1 -b .ia64
%patch9 -p1 -b .system-auth
%patch10 -p1 -b .rh
%patch11 -p1 -b .nocups
%patch12 -p1 -b .smbadduser
%patch13 -p1 -b .krb5-1.2
%patch14 -p1 -b .ssl

%build
cd source
autoconf
CPPFLAGS="-I/usr/include/openssl -I/usr/kerberos/include"; export CPPFLAGS
LIBS="-L/usr/kerberos/lib"; export LIBS
%configure --libdir=/etc/samba \
  --with-lockdir=/var/lock/samba --with-privatedir=/etc/samba \
  --with-swatdir=/usr/share/swat --with-smbmount --with-automount \
  --with-ssl --with-krb5=/usr/kerberos \
  --with-pam --with-mmap --with-quotas
make CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE" all

%install
rm -rf $RPM_BUILD_ROOT

cd source

mkdir -p $RPM_BUILD_ROOT/sbin
mkdir -p $RPM_BUILD_ROOT/usr/{sbin,bin}
mkdir -p $RPM_BUILD_ROOT%{initdir}
mkdir -p $RPM_BUILD_ROOT/etc/{pam.d,logrotate.d}
mkdir -p $RPM_BUILD_ROOT/var/{lock,log,spool}/samba
mkdir -p $RPM_BUILD_ROOT/usr/share/swat/using_samba

%makeinstall \
       BINDIR=$RPM_BUILD_ROOT%{_bindir} \
       BASEDIR=$RPM_BUILD_ROOT%{_prefix} \
       SBINDIR=$RPM_BUILD_ROOT%{_sbindir} \
       LOCKDIR=$RPM_BUILD_ROOT/var/lock/samba \
       PRIVATEDIR=$RPM_BUILD_ROOT/etc/samba \
       LIBDIR=$RPM_BUILD_ROOT/etc/samba \
       MANDIR=$RPM_BUILD_ROOT%{_mandir} \
       VARDIR=$RPM_BUILD_ROOT/var/log/samba \
       SWATDIR=$RPM_BUILD_ROOT/usr/share/swat \
       SAMBABOOK=$RPM_BUILD_ROOT/usr/share/swat/using_samba \
       install

cd ..

# Install other stuff
install -m644 packaging/RedHat/smb.conf $RPM_BUILD_ROOT/etc/samba/smb.conf
install -m755 source/script/mksmbpasswd.sh $RPM_BUILD_ROOT/usr/bin
install -m644 packaging/RedHat/smbusers $RPM_BUILD_ROOT/etc/samba/smbusers
install -m755 packaging/RedHat/smbprint $RPM_BUILD_ROOT%{_bindir}
install -m755 packaging/RedHat/smbadduser $RPM_BUILD_ROOT%{_bindir}
install -m755 packaging/RedHat/findsmb $RPM_BUILD_ROOT%{_bindir}
install -m755 packaging/RedHat/smb.init $RPM_BUILD_ROOT%{initdir}/smb
install -m755 packaging/RedHat/smb.init $RPM_BUILD_ROOT%{_sbindir}/samba
install -m644 packaging/RedHat/samba.pamd $RPM_BUILD_ROOT/etc/pam.d/samba
install -m644 $RPM_SOURCE_DIR/samba.log $RPM_BUILD_ROOT/etc/logrotate.d/samba
ln -s ../%{_bindir}/smbmount $RPM_BUILD_ROOT/sbin/mount.smb
ln -s ../%{_bindir}/smbmount $RPM_BUILD_ROOT/sbin/mount.smbfs
echo 127.0.0.1 localhost > $RPM_BUILD_ROOT/etc/samba/lmhosts

mkdir -p $RPM_BUILD_ROOT/etc/xinetd.d
install -m644 %{SOURCE2} $RPM_BUILD_ROOT/etc/xinetd.d/swat

mkdir -p $RPM_BUILD_ROOT/etc/X11/applnk/System
cat > $RPM_BUILD_ROOT/etc/X11/applnk/System/swat.desktop <<EOF
[Desktop Entry]
Name=Samba Configuration
Type=Application
Comment=The Swat Samba Administration Tool
Exec=netscape http://localhost:901/
Terminal=false
EOF

# remove this or it ends up in %doc
rm -rf docs/htmldocs/using_samba

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add smb

%preun
if [ $1 = 0 ] ; then
    /sbin/chkconfig --del smb
    rm -rf /var/log/samba/* /var/lock/samba/*
    %{initdir}/smb stop >/dev/null 2>&1
fi

%postun
if [ "$1" -ge "1" ]; then
	%{initdir}/smb condrestart >/dev/null 2>&1
fi	

%triggerpostun -- samba < 1.9.18p7
if [ $1 != 0 ]; then
    /sbin/chkconfig --add smb
fi

%triggerpostun -- samba < 2.0.5a-3
if [ $1 != 0 ]; then
    [ ! -d /var/lock/samba ] && mkdir -m 0755 /var/lock/samba
    [ ! -d /var/spool/samba ] && mkdir -m 1777 /var/spool/samba
    chmod 644 /etc/services /etc/inetd.conf
fi

%files
%defattr(-,root,root)
%doc README COPYING Manifest Read-Manifest-Now
%doc WHATSNEW.txt Roadmap
%doc docs
%doc examples
%{_sbindir}/smbd
%{_sbindir}/nmbd
%{_sbindir}/swat
%{_bindir}/addtosmbpass
%{_bindir}/mksmbpasswd.sh
%{_bindir}/smbstatus
%{_bindir}/smbpasswd
%{_bindir}/convert_smbpasswd
%{_bindir}/smbadduser
/usr/share/swat
%config(noreplace) /etc/samba/smbusers
%config %{_sbindir}/samba
%attr(755,root,root) %config %{initdir}/smb
%config /etc/logrotate.d/samba
%config /etc/pam.d/samba
/etc/X11/applnk/System/swat.desktop
%config(noreplace) /etc/xinetd.d/swat
%{_mandir}/man1/smbstatus.1*
%{_mandir}/man5/smbpasswd.5*
%{_mandir}/man7/samba.7*
%{_mandir}/man8/smbd.8*
%{_mandir}/man8/nmbd.8*
%{_mandir}/man8/smbpasswd.8*
%{_mandir}/man8/swat.8*

%dir /var/lock/samba
%attr(0700,root,root)   %dir /var/log/samba
%attr(1777,root,root)	%dir /var/spool/samba

%files client
%defattr(-,root,root)
/sbin/mount.smb
/sbin/mount.smbfs
%{_bindir}/smbmount
%{_bindir}/smbmnt
%{_bindir}/smbumount
%{_mandir}/man8/smbmnt.8*
%{_mandir}/man8/smbmount.8*
%{_mandir}/man8/smbumount.8*
%{_mandir}/man8/smbspool.8*
%{_bindir}/nmblookup
%{_bindir}/findsmb
%{_bindir}/smbclient
%{_bindir}/smbprint
%{_bindir}/smbspool
%{_bindir}/smbtar
%{_mandir}/man1/smbtar.1*
%{_mandir}/man1/smbclient.1*
%{_mandir}/man1/nmblookup.1*

%files common
%defattr(-,root,root)
%{_bindir}/make_smbcodepage
%{_bindir}/testparm
%{_bindir}/testprns
%{_bindir}/make_printerdef
%config(noreplace) /etc/samba/smb.conf
%config(noreplace) /etc/samba/lmhosts
%dir /etc/samba/codepages
%config /etc/samba/codepages/*
%{_mandir}/man1/make_smbcodepage.1*
%{_mandir}/man1/testparm.1*
%{_mandir}/man1/testprns.1*
%{_mandir}/man5/smb.conf.5*
%{_mandir}/man5/lmhosts.5*

%changelog
* Thu Aug 31 2000 Yukihiro Nakai <ynakai@redhat.com>
- Use Japanized samba from http://www.samba.gr.jp/

* Mon Aug 14 2000 Bill Nottingham <notting@redhat.com>
- add smbspool back in (#15827)
- fix absolute symlinks (#16125)

* Sun Aug 6 2000 Philipp Knirsch <pknirsch@redhat.com>
- bugfix for smbadduser script (#15148)

* Mon Jul 31 2000 Matt Wilson <msw@redhat.com>
- patch configure.ing (patch11) to disable cups test
- turn off swat by default

* Fri Jul 28 2000 Bill Nottingham <notting@redhat.com>
- fix condrestart stuff

* Fri Jul 21 2000 Bill Nottingham <notting@redhat.com>
- add copytruncate to logrotate file (#14360)
- fix init script (#13708)

* Sat Jul 15 2000 Bill Nottingham <notting@redhat.com>
- move initscript back
- remove 'Using Samba' book from %%doc 
- move stuff to /etc/samba (#13708)
- default configuration tweaks (#13704)
- some logrotate tweaks

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Tue Jul 11 2000 Bill Nottingham <notting@redhat.com>
- fix logrotate script (#13698)

* Thu Jul  6 2000 Bill Nottingham <notting@redhat.com>
- fix initscripts req (prereq /etc/init.d)

* Wed Jul 5 2000 Than Ngo <than@redhat.de>
- add initdir macro to handle the initscript directory
- add a new macro to handle /etc/pam.d/system-auth

* Thu Jun 29 2000 Nalin Dahyabhai <nalin@redhat.com>
- enable Kerberos 5 and SSL support
- patch for duplicate profile.h headers

* Thu Jun 29 2000 Bill Nottingham <notting@redhat.com>
- fix init script

* Tue Jun 27 2000 Bill Nottingham <notting@redhat.com>
- rename samba logs (#11606)

* Mon Jun 26 2000 Bill Nottingham <notting@redhat.com>
- initscript munging

* Fri Jun 16 2000 Bill Nottingham <notting@redhat.com>
- configure the swat stuff usefully
- re-integrate some specfile tweaks that got lost somewhere

* Thu Jun 15 2000 Bill Nottingham <notting@redhat.com>
- rebuild to get rid of cups dependency

* Wed Jun 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- tweak logrotate configurations to use the PID file in /var/lock/samba

* Sun Jun 11 2000 Bill Nottingham <notting@redhat.com>
- rebuild in new environment

* Thu Jun  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- change PAM setup to use system-auth

* Mon May  8 2000 Bill Nottingham <notting@redhat.com>
- fixes for ia64

* Sat May  6 2000 Bill Nottingham <notting@redhat.com>
- switch to %%configure

* Wed Apr 26 2000 Nils Philippsen <nils@redhat.de>
- version 2.0.7

* Sun Mar 26 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- simplify preun

* Thu Mar 16 2000 Bill Nottingham <notting@redhat.com>
- fix yp_get_default_domain in autoconf
- only link against readline for smbclient
- fix log rotation (#9909)

* Fri Feb 25 2000 Bill Nottingham <notting@redhat.com>
- fix trigger, again.

* Mon Feb  7 2000 Bill Nottingham <notting@redhat.com>
- fix trigger.

* Fri Feb  4 2000 Bill Nottingham <notting@redhat.com>
- turn on quota support

* Mon Jan 31 2000 Cristian Gafton <gafton@redhat.com>
- rebuild to fox dependencies
- man pages are compressed

* Fri Jan 21 2000 Bill Nottingham <notting@redhat.com>
- munge post scripts slightly

* Wed Jan 19 2000 Bill Nottingham <notting@redhat.com>
- turn on mmap again. Wheee.
- ship smbmount on alpha

* Mon Dec  6 1999 Bill Nottingham <notting@redhat.com>
- turn off mmap. ;)

* Wed Dec  1 1999 Bill Nottingham <notting@redhat.com>
- change /var/log/samba to 0700
- turn on mmap support

* Thu Nov 11 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.6

* Fri Oct 29 1999 Bill Nottingham <notting@redhat.com>
- add a %defattr for -common

* Tue Oct  5 1999 Bill Nottingham <notting@redhat.com>
- shift some files into -client
- remove /home/samba from package.

* Tue Sep 28 1999 Bill Nottingham <notting@redhat.com>
- initscript oopsie. killproc <name> -HUP, not other way around.

* Sat Sep 26 1999 Bill Nottingham <notting@redhat.com>
- script cleanups. Again.

* Wed Sep 22 1999 Bill Nottingham <notting@redhat.com>
- add a patch to fix dropped reconnection attempts

* Mon Sep  6 1999 Jeff Johnson <jbj@redhat.com>
- use cp rather than mv to preserve /etc/services perms (#4938 et al).
- use mktemp to generate /etc/tmp.XXXXXX file name.
- add prereqs on sed/mktemp/killall (need to move killall to /bin).
- fix trigger syntax (i.e. "samba < 1.9.18p7" not "samba < samba-1.9.18p7")

* Mon Aug 30 1999 Bill Nottingham <notting@redhat.com>
- sed "s|nawk|gawk|" /usr/bin/convert_smbpasswd

* Sat Aug 21 1999 Bill Nottingham <notting@redhat.com>
- fix typo in mount.smb

* Fri Aug 20 1999 Bill Nottingham <notting@redhat.com>
- add a %trigger to work around (sort of) broken scripts in
  previous releases

* Mon Aug 16 1999 Bill Nottingham <notting@redhat.com>
- initscript munging

* Mon Aug  9 1999 Bill Nottingham <notting@redhat.com>
- add domain parsing to mount.smb

* Fri Aug  6 1999 Bill Nottingham <notting@redhat.com>
- add a -common package, shuffle files around.

* Fri Jul 23 1999 Bill Nottingham <notting@redhat.com>
- add a chmod in %postun so /etc/services & inetd.conf don't become unreadable

* Wed Jul 21 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.5
- fix mount.smb - smbmount options changed again.........
- fix postun. oops.
- update some stuff from the samba team's spec file.

* Fri Jun 18 1999 Bill Nottingham <notting@redhat.com>
- split off clients into separate package
- don't run samba by default

* Mon Jun 14 1999 Bill Nottingham <notting@redhat.com>
- fix one problem with mount.smb script
- fix smbpasswd on sparc with a really ugly kludge

* Thu Jun 10 1999 Dale Lovelace <dale@redhat.com>
- fixed logrotate script

* Tue May 25 1999 Bill Nottingham <notting@redhat.com>
- turn of 64-bit locking on 32-bit platforms

* Thu May 20 1999 Bill Nottingham <notting@redhat.com>
- so many releases, so little time
- explicitly uncomment 'printing = bsd' in sample config

* Tue May 18 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.4a
- fix mount.smb arg ordering

* Fri Apr 16 1999 Bill Nottingham <notting@redhat.com>
- go back to stop/start for restart (-HUP didn't work in testing)

* Fri Mar 26 1999 Bill Nottingham <notting@redhat.com>
- add a mount.smb to make smb mounting a little easier.
- smb filesystems apparently don't work on alpha. Oops.

* Thu Mar 25 1999 Bill Nottingham <notting@redhat.com>
- always create codepages

* Tue Mar 23 1999 Bill Nottingham <notting@redhat.com>
- logrotate changes

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 3)

* Fri Mar 19 1999 Preston Brown <pbrown@redhat.com>
- updated init script to use graceful restart (not stop/start)

* Tue Mar  9 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.3

* Thu Feb 18 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.2

* Mon Feb 15 1999 Bill Nottingham <notting@redhat.com>
- swat swat

* Tue Feb  9 1999 Bill Nottingham <notting@redhat.com>
- fix bash2 breakage in post script

* Fri Feb  5 1999 Bill Nottingham <notting@redhat.com>
- update to 2.0.0

* Mon Oct 12 1998 Cristian Gafton <gafton@redhat.com>
- make sure all binaries are stripped

* Thu Sep 17 1998 Jeff Johnson <jbj@redhat.com>
- update to 1.9.18p10.
- fix %triggerpostun.

* Tue Jul 07 1998 Erik Troan <ewt@redhat.com>
- updated postun triggerscript to check $0
- clear /etc/codepages from %preun instead of %postun

* Mon Jun 08 1998 Erik Troan <ewt@redhat.com>
- made the %postun script a tad less agressive; no reason to remove
  the logs or lock file (after all, if the lock file is still there,
  samba is still running)
- the %postun and %preun should only exectute if this is the final
  removal
- migrated %triggerpostun from Red Hat's samba package to work around
  packaging problems in some Red Hat samba releases

* Sun Apr 26 1998 John H Terpstra <jht@samba.anu.edu.au>
- minor tidy up in preparation for release of 1.9.18p5
- added findsmb utility from SGI package

* Wed Mar 18 1998 John H Terpstra <jht@samba.anu.edu.au>
- Updated version and codepage info.
- Release to test name resolve order

* Sat Jan 24 1998 John H Terpstra <jht@samba.anu.edu.au>
- Many optimisations (some suggested by Manoj Kasichainula <manojk@io.com>
- Use of chkconfig in place of individual symlinks to /etc/rc.d/init/smb
- Compounded make line
- Updated smb.init restart mechanism
- Use compound mkdir -p line instead of individual calls to mkdir
- Fixed smb.conf file path for log files
- Fixed smb.conf file path for incoming smb print spool directory
- Added a number of options to smb.conf file
- Added smbadduser command (missed from all previous RPMs) - Doooh!
- Added smbuser file and smb.conf file updates for username map

