Summary: The Samba Suite of programs
Name: samba
Epoch: 0
Version: 3.0.25a
Release: 2%{?dist}
License: GPL
Group: System Environment/Daemons
URL: http://www.samba.org/

#TAG: change for non-pre
#Source: http://www.samba.org/samba/ftp/rc/%{name}-%{version}rc3.tar.gz
Source: http://www.samba.org/samba/ftp/samba/%{name}-%{version}.tar.gz

# Red Hat specific replacement-files
Source1: samba.log
Source2: samba.xinetd
Source3: swat.desktop
Source4: samba.sysconfig
Source5: smb.init
Source6: samba.pamd
Source7: smbprint
Source8: winbind.init
Source9: smb.conf.default
Source10: nmb.init
Source11: pam_winbind.conf

# Don't depend on Net::LDAP
Source999: filter-requires-samba.sh

# upstream patches.  Applied first so that they'll break our patches rather
# than the other way around
# (none right now)

# generic patches
#Patch101: samba-2.2.0-smbw.patch
Patch102: samba-3.0.0beta1-pipedir.patch
#Patch103: samba-3.0.23-logfiles.patch
Patch104: samba-3.0.0rc3-nmbd-netbiosname.patch
#Patch105: samba-3.0.23-smb.conf.patch
#Patch106: samba-3.0.23d-man.patch
# The passwd part has been applied, but not the group part
Patch107: samba-3.0.23rc3-passwd.patch
#Patch108: samba-3.0.8-non-ascii-domain.patch
Patch110: samba-3.0.21pre1-smbspool.patch
Patch111: samba-3.0.13-smbclient.patch
#Patch112: samba-3.0.15pre2-bug106483.patch
#Patch113: samba-3.0.21-warnings.patch
Patch200: samba-3.0.25rc1-inotifiy.patch
Patch201: samba-3.0.25a-pam_smbpass.patch


Requires(pre): samba-common = %{epoch}:%{version}-%{release}
Requires: pam >= 0:0.64
Requires: logrotate >= 0:3.4
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires(post): /sbin/chkconfig, /sbin/service
Requires(preun): /sbin/chkconfig, /sbin/service
BuildRequires: pam-devel, readline-devel, ncurses-devel, libacl-devel, krb5-devel, openldap-devel, openssl-devel, cups-devel
BuildRequires: autoconf

# Working around perl dependency problem from docs
%define __perl_requires %{SOURCE999}


%description

Samba is the suite of programs by which a lot of PC-related machines
share files, printers, and other information (such as lists of
available files and printers). The Windows NT, OS/2, and Linux
operating systems support this natively, and add-on packages can
enable the same thing for DOS, Windows, VMS, UNIX of all kinds, MVS,
and more. This package provides an SMB/CIFS server that can be used to
provide network services to SMB/CIFS clients.
Samba uses NetBIOS over TCP/IP (NetBT) protocols and does NOT
need the NetBEUI (Microsoft Raw NetBIOS frame) protocol.


%package client
Summary: Samba client programs
Group: Applications/System
Requires: samba-common = %{epoch}:%{version}-%{release}
Obsoletes: smbfs

%description client
The samba-client package provides some SMB/CIFS clients to complement
the built-in SMB/CIFS filesystem in Linux. These clients allow access
of SMB/CIFS shares and printing to SMB/CIFS printers.


%package common
Summary: Files used by both Samba servers and clients
Group: Applications/System
Requires(pre): /usr/sbin/groupadd
Requires(post): /sbin/chkconfig, /sbin/service, coreutils
Requires(preun): /sbin/chkconfig, /sbin/service

%description common
Samba-common provides files necessary for both the server and client
packages of Samba.


%package swat
Summary: The Samba SMB server Web configuration program
Group: Applications/System
Requires: samba = %{epoch}:%{version}-%{release}, xinetd

%description swat
The samba-swat package includes the new SWAT (Samba Web Administration
Tool), for remotely managing Samba's smb.conf file using your favorite
Web browser.


%package doc
Summary: Documentation for the Samba suite
Group: Documentation
Requires: samba-common = %{epoch}:%{version}-%{release}

%description doc
The samba-doc package includes all the non-manpage documentation for the
Samba suite.


%package -n libsmbclient
Summary: The SMB client library
Group: Applications/System

%description -n libsmbclient
The libsmbclient contains the SMB client library from the Samba suite.

%package -n libsmbclient-devel
Summary: Developer tools for the SMB client library
Group: Development
Requires: libsmbclient = %{epoch}:%{version}-%{release}

%description -n libsmbclient-devel
The libsmbclient-devel package contains the header files and libraries needed to
develop programs that link against the SMB client library in the Samba suite.


%prep
# TAG: change for non-pre
#%setup -q -n samba-3.0.25rc3
%setup -q 

# copy Red Hat specific scripts
mkdir packaging/Fedora
cp packaging/RHEL/setup/smbusers packaging/Fedora/
cp %{SOURCE5} packaging/Fedora/
cp %{SOURCE6} packaging/Fedora/
cp %{SOURCE7} packaging/Fedora/
cp %{SOURCE8} packaging/Fedora/winbind.init
cp %{SOURCE9} packaging/Fedora/
cp %{SOURCE10} packaging/Fedora/
cp %{SOURCE11} packaging/Fedora/

# Upstream patches
#(none)
# generic patches
#%patch101 -p1 -b .smbw
%patch102 -p1 -b .pipedir
#%patch103 -p1 -b .logfiles
%patch104 -p1 -b .nmbd-netbiosname
#%patch105 -p1 -b .upstream
#%patch106 -p1 -b .man
%patch107 -p1 -b .passwd
#%patch108 -p1 -b .non-ascii-domain
%patch110 -p1 -b .smbspool
%patch111 -p1 -b .smbclient
#%patch112 -p1 -b .bug106483
#%patch113 -p1 -b .warnings
%patch200 -p0 -b .inotify
%patch201 -p0 -b .pam_smbpass

# crap
rm -f examples/VFS/.cvsignore
mv source/VERSION source/VERSION.orig
sed -e 's/SAMBA_VERSION_VENDOR_SUFFIX=$/&\"%{release}\"/' < source/VERSION.orig > source/VERSION
cd source
script/mkversion.sh
cd ..


%build
cd source
sh autogen.sh
%ifarch i386 sparc
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -D_FILE_OFFSET_BITS=64"
%endif
%ifarch ia64
#libtoolize --copy --force     # get it to recognize IA-64
#autoheader                                               
#autoconf
EXTRA="-D_LARGEFILE64_SOURCE"
%endif
CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -DLDAP_DEPRECATED" %configure \
	--with-acl-support \
	--with-automount \
	--with-libsmbclient \
	--with-mmap \
	--with-pam \
	--with-pam_smbpass \
	--with-quotas \
	--with-syslog \
	--with-utmp \
	--with-vfs \
	--without-smbwrapper \
	--with-lockdir=/var/lib/samba \
	--with-piddir=/var/run \
	--with-mandir=%{_mandir} \
	--with-privatedir=/var/lib/samba/private \
	--with-logfilebase=/var/log/samba \
	--with-libdir=%{_libdir}/samba \
	--with-configdir=%{_sysconfdir}/samba \
	--with-pammodulesdir=%{_lib}/security \
	--with-swatdir=%{_datadir}/swat \
	--with-shared-modules=idmap_ad,idmap_rid \


make  CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -DLDAP_DEPRECATED" \
	proto

make  CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -DLDAP_DEPRECATED" %{?_smp_mflags} \
	all nsswitch/libnss_wins.so modules test_pam_modules test_nss_modules

make  CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE" \
	debug2html

make  CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE" \
	smbfilter

( cd client ; gcc -o mount.cifs $RPM_OPT_FLAGS -Wall -O -D_GNU_SOURCE -D_LARGEFILE64_SOURCE mount.cifs.c )
( cd client ; gcc -o umount.cifs $RPM_OPT_FLAGS -Wall -O -D_GNU_SOURCE -D_LARGEFILE64_SOURCE umount.cifs.c )



%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/sbin
mkdir -p $RPM_BUILD_ROOT/usr/{sbin,bin}
mkdir -p $RPM_BUILD_ROOT/%{_initrddir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/{pam.d,logrotate.d,security}
mkdir -p $RPM_BUILD_ROOT/%{_lib}/security
mkdir -p $RPM_BUILD_ROOT/var/{log,spool}/samba
mkdir -p $RPM_BUILD_ROOT/var/lib/samba
mkdir -p $RPM_BUILD_ROOT/var/lib/samba/private
mkdir -p $RPM_BUILD_ROOT/var/lib/samba/winbindd_privileged
mkdir -p $RPM_BUILD_ROOT/var/lib/samba/scripts
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/swat/using_samba
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/samba/codepages 
mkdir -p $RPM_BUILD_ROOT/var/run/winbindd

cd source

%makeinstall \
	BINDIR=$RPM_BUILD_ROOT%{_bindir} \
	BASEDIR=$RPM_BUILD_ROOT%{_prefix} \
	SBINDIR=$RPM_BUILD_ROOT%{_sbindir} \
	DATADIR=$RPM_BUILD_ROOT%{_datadir} \
	LOCKDIR=$RPM_BUILD_ROOT/var/lib/samba \
	PRIVATEDIR=$RPM_BUILD_ROOT%{_sysconfdir}/samba \
	LIBDIR=$RPM_BUILD_ROOT%{_libdir}/samba \
	CONFIGDIR=$RPM_BUILD_ROOT%{_sysconfdir}/samba \
	PAMMODULESDIR=$RPM_BUILD_ROOT/%{_lib}/security \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	VARDIR=$RPM_BUILD_ROOT/var/log/samba \
	CODEPAGEDIR=$RPM_BUILD_ROOT%{_datadir}/samba/codepages \
	SWATDIR=$RPM_BUILD_ROOT%{_datadir}/swat \
	SAMBABOOK=$RPM_BUILD_ROOT%{_datadir}/swat/using_samba \
	PIDDIR=$RPM_BUILD_ROOT/var/run

cd ..

# Install other stuff
install -m644 packaging/Fedora/smb.conf.default $RPM_BUILD_ROOT%{_sysconfdir}/samba/smb.conf
install -m755 source/script/mksmbpasswd.sh $RPM_BUILD_ROOT%{_bindir}
install -m644 packaging/Fedora/smbusers $RPM_BUILD_ROOT%{_sysconfdir}/samba/smbusers
install -m755 packaging/Fedora/smbprint $RPM_BUILD_ROOT%{_bindir}
install -m755 packaging/Fedora/smb.init $RPM_BUILD_ROOT%{_initrddir}/smb
install -m755 packaging/Fedora/nmb.init $RPM_BUILD_ROOT%{_initrddir}/nmb
install -m755 packaging/Fedora/winbind.init $RPM_BUILD_ROOT%{_initrddir}/winbind
install -m644 packaging/Fedora/pam_winbind.conf $RPM_BUILD_ROOT%{_sysconfdir}/security
#ln -s ../..%{_initrddir}/smb  $RPM_BUILD_ROOT%{_sbindir}/samba
install -m644 packaging/Fedora/samba.pamd $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/samba
install -m644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/samba
echo 127.0.0.1 localhost > $RPM_BUILD_ROOT%{_sysconfdir}/samba/lmhosts
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/openldap/schema
install -m644 examples/LDAP/samba.schema $RPM_BUILD_ROOT%{_sysconfdir}/openldap/schema/samba.schema

# winbind
mkdir -p $RPM_BUILD_ROOT%{_libdir}
install -m 755 source/nsswitch/libnss_winbind.so $RPM_BUILD_ROOT/%{_lib}/libnss_winbind.so.2
ln -sf /%{_lib}/libnss_winbind.so.2  $RPM_BUILD_ROOT%{_libdir}/libnss_winbind.so
install -m 755 source/nsswitch/libnss_wins.so $RPM_BUILD_ROOT/%{_lib}/libnss_wins.so.2
ln -sf /%{_lib}/libnss_wins.so.2  $RPM_BUILD_ROOT%{_libdir}/libnss_wins.so

# libsmbclient

# make install puts libsmbclient.so in the wrong place on x86_64
rm -f $RPM_BUILD_ROOT%{_libdir}/samba/libsmbclient.so $RPM_BUILD_ROOT%{_libdir}/samba/libsmbclient.a $RPM_BUILD_ROOT/usr/lib || true
mkdir -p $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_includedir}
install -m 755 source/bin/libsmbclient.so $RPM_BUILD_ROOT%{_libdir}/libsmbclient.so.0
/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}/
ln -s libsmbclient.so.0 $RPM_BUILD_ROOT%{_libdir}/libsmbclient.so
#install -m 644 source/bin/libsmbclient.a $RPM_BUILD_ROOT%{_libdir}/libsmbclient.a
install -m 644 source/include/libsmbclient.h $RPM_BUILD_ROOT%{_includedir}

# various libs we currently remove
# TODO: evaluate how to make them back by extracting the correct .h files

#this lib is not really useful or usable (libmsrpc.h requires the samba source)
#so better to remove it until upstream fixes it
rm -f $RPM_BUILD_ROOT%{_libdir}/samba/libmsrpc.so
rm -f $RPM_BUILD_ROOT%{_includedir}/libmsrpc.h

rm -f $RPM_BUILD_ROOT%{_libdir}/samba/libsmbsharemodes.so

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d
install -m644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d/swat

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/samba
install -m755 source/client/mount.cifs $RPM_BUILD_ROOT/sbin/mount.cifs
install -m755 source/client/umount.cifs $RPM_BUILD_ROOT/sbin/umount.cifs

rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/editreg.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/log2pcap.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/smbsh.1*
#rm -f $RPM_BUILD_ROOT%{_mandir}/man1/smbget.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/smbgetrc.5*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/vfstest.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/testprns.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/smbmount.8*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/smbmnt.8*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/smbumount.8*

# why are these getting installed in the wrong place?
rm -f $RPM_BUILD_ROOT%{_sbindir}/{u,}mount.cifs


%clean
rm -rf $RPM_BUILD_ROOT

#%pre

%post
/sbin/chkconfig --add smb
/sbin/chkconfig --add nmb
if [ "$1" -ge "1" ]; then
	/sbin/service smb condrestart >/dev/null 2>&1 || :
	/sbin/service nmb condrestart >/dev/null 2>&1 || :
fi
exit 0

%preun
if [ $1 = 0 ] ; then
    /sbin/service smb stop >/dev/null 2>&1 || :
    /sbin/service nmb stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del smb
    /sbin/chkconfig --del nmb
fi
exit 0

#%postun


%pre common
/usr/sbin/groupadd -g 88 wbpriv >/dev/null 2>&1 || :

%post common
/sbin/chkconfig --add winbind
/sbin/ldconfig

# This script must be run always on installs or upgrades
# it checks if a previous installation have created files
# under /var/cache/samba and move them in that case as the
# new package wants them to be under /var/lib/samba for
# FHS compliance
#
# - we must stop the dameon if running and restart it
#   after the script if it was
# - we do not overwrite newer files
# - even if /etc/init.d/smb is in samba and not
#   samba-common we need to stop smbd/nmbd, if they
#   are running, here as well, or we will mess up
#   shared (between winbindd and smbd/nmbd) tdbs

OLDPATH="/var/cache/samba"
NEWPATH="/var/lib/samba"

eval ls $OLDPATH/*.tdb >/dev/null 2>&1
if [ $? = 0 ]; then

	#Stop daemons before we move the files around

	#this is what condrestart checks as well
	if [ -f /var/lock/subsys/winbindd ]; then
		/sbin/service winbind stop >/dev/null 2>&1 || :
		# Use a dirty trick to fool condrestart later
		touch /var/lock/subsys/winbindd
	fi

	if [ -f /var/lock/subsys/smb ]; then
		/sbin/service smb stop >/dev/null 2>&1 || :
		# We need to stop smbd here as we are moving also smbd owned files
		# but we can't restart it until the new server is installed.
		# Use a dirty trick to fool condrestart later
		touch /var/lock/subsys/smb
	fi

	if [ -f /var/lock/subsys/nmb ]; then
		/sbin/service nmb stop >/dev/null 2>&1 || :
		# We need to stop smbd here as we are moving also smbd owned files
		# but we can't restart it until the new server is installed.
		# Use a dirty trick to fool condrestart later
		touch /var/lock/subsys/nmb
	fi

	eval ls $NEWPATH/*.tdb >/dev/null 2>&1
	if [ $? = 0 ]; then
		#something strange here, lets backup this stuff and avoid just wiping it

		mkdir $NEWPATH.pkgbkp
		mv -f $NEWPATH/*.tdb $NEWPATH.pkgbkp/ >/dev/null 2>&1
		mv -f $NEWPATH/*.dat $NEWPATH.pkgbkp/ >/dev/null 2>&1
		mv -f $NEWPATH/perfmon $NEWPATH.pkgbkp/ >/dev/null 2>&1
		mv -f $NEWPATH/printing $NEWPATH.pkgbkp/ >/dev/null 2>&1
	fi

	mv -f $OLDPATH/*.tdb $NEWPATH/ >/dev/null 2>&1
	mv -f $OLDPATH/*.dat $NEWPATH/ >/dev/null 2>&1
	mv -f $OLDPATH/perfmon $NEWPATH/ >/dev/null 2>&1
	mv -f $OLDPATH/printing $NEWPATH/ >/dev/null 2>&1
fi

# We also moved private files from /etc/samba to
# /var/lib/samba/private so we need to migrate these as well

#secrets.tdb
if [ -f %{_sysconfdir}/samba/secrets.tdb ]; then
	if [ -f /var/lib/samba/private/secrets.tdb ]; then
		mv -f /var/lib/samba/private/secrets.tdb /var/lib/samba/private/secrets.tdb.old
	fi
	mv -f %{_sysconfdir}/samba/secrets.tdb /var/lib/samba/private/secrets.tdb
fi

#smbpasswd
if [ -f %{_sysconfdir}/samba/smbpasswd ]; then
	if [ -f /var/lib/samba/private/smbpasswd ]; then
		mv -f /var/lib/samba/private/smbpasswd /var/lib/samba/private/smbpasswd.old
	fi
	mv -f %{_sysconfdir}/samba/smbpasswd /var/lib/samba/private/smbpasswd
fi

#passdb.tdb
if [ -f %{_sysconfdir}/samba/passdb.tdb ]; then
	if [ -f /var/lib/samba/private/passdb.tdb ]; then
		mv -f /var/lib/samba/private/passdb.tdb /var/lib/samba/private/passdb.tdb.old
	fi
	mv -f %{_sysconfdir}/samba/passdb.tdb /var/lib/samba/private/passdb.tdb
fi

#remove schannel_store if existing, it is not info we need to keep across restarts
if [ -f %{_sysconfdir}/samba/schannel_store.tdb ]; then
	rm -f %{_sysconfdir}/samba/schannel_store.tdb
fi

if [ "$1" -ge "1" ]; then
	/sbin/service winbind condrestart >/dev/null 2>&1 || :
fi

%preun common
if [ $1 = 0 ] ; then
    /sbin/service winbind stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del winbind
fi
exit 0

%postun common
/sbin/ldconfig


%post -n libsmbclient
/sbin/ldconfig

%postun -n libsmbclient
/sbin/ldconfig

%files
%defattr(-,root,root)
%{_sbindir}/smbd
%{_sbindir}/nmbd
%{_bindir}/mksmbpasswd.sh
%{_bindir}/smbstatus
%{_bindir}/eventlogadm
%config(noreplace) %{_sysconfdir}/samba/smbusers
%attr(755,root,root) %{_initrddir}/smb
%attr(755,root,root) %{_initrddir}/nmb
%config(noreplace) %{_sysconfdir}/logrotate.d/samba
%config(noreplace) %{_sysconfdir}/pam.d/samba
%{_mandir}/man7/samba.7*
%{_mandir}/man8/nmbd.8*
%{_mandir}/man8/smbd.8*
%{_mandir}/man8/eventlogadm.8*
%{_mandir}/man8/vfs_*.8*
%{_libdir}/samba/vfs
%{_libdir}/samba/auth
%attr(1777,root,root) %dir /var/spool/samba
%dir %{_sysconfdir}/openldap/schema
%{_sysconfdir}/openldap/schema/samba.schema

%doc examples/autofs examples/LDAP examples/libsmbclient examples/misc examples/printer-accounting
%doc examples/printing
%doc docs/registry

%files swat
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/xinetd.d/swat
%{_datadir}/swat
%{_sbindir}/swat
%{_mandir}/man8/swat.8*
%attr(755,root,root) %{_libdir}/samba/*.msg

%files client
%defattr(-,root,root)
/sbin/mount.cifs
/sbin/umount.cifs
%{_bindir}/rpcclient
%{_bindir}/smbcacls
%{_bindir}/findsmb
%{_bindir}/smbget
%{_bindir}/nmblookup
%{_bindir}/smbclient
%{_bindir}/smbprint
%{_bindir}/smbspool
%{_bindir}/smbtar
%{_bindir}/smbtree
%{_mandir}/man1/findsmb.1*
%{_mandir}/man1/nmblookup.1*
%{_mandir}/man1/rpcclient.1*
%{_mandir}/man1/smbcacls.1*
%{_mandir}/man1/smbclient.1*
%{_mandir}/man1/smbtar.1*
%{_mandir}/man1/smbtree.1*
%{_mandir}/man1/smbget.1*
%{_mandir}/man8/smbspool.8*
%{_mandir}/man8/mount.cifs.8*
%{_mandir}/man8/umount.cifs.8*

%files common
%defattr(-,root,root)
%attr(755,root,root) /%{_lib}/security/pam_smbpass.so
%dir %{_libdir}/samba
%{_libdir}/samba/charset
%{_libdir}/samba/lowcase.dat
%{_libdir}/samba/upcase.dat
%{_libdir}/samba/valid.dat
#%{_libdir}/samba/libmsrpc.so
%{_libdir}/libnss_wins.so
/%{_lib}/libnss_wins.so.2
%{_libdir}/libnss_winbind.so
/%{_lib}/libnss_winbind.so.2
/%{_lib}/security/pam_winbind.so

%{_bindir}/net
%{_bindir}/testparm
%{_bindir}/smbpasswd
%{_bindir}/wbinfo
%{_bindir}/ntlm_auth
%{_bindir}/pdbedit
%{_bindir}/profiles
%{_bindir}/smbcquotas
%{_bindir}/smbcontrol
%{_bindir}/tdbbackup
%{_bindir}/tdbdump
%{_bindir}/tdbtool
%{_sbindir}/winbindd
%{_libdir}/samba/idmap
%{_libdir}/samba/nss_info
%dir /var/lib/samba
%attr(700,root,root) %dir /var/lib/samba/private
%dir /var/run/winbindd
%attr(750,root,wbpriv) %dir /var/lib/samba/winbindd_privileged
%dir /var/lib/samba/scripts
%config(noreplace) %{_sysconfdir}/samba/smb.conf
%config(noreplace) %{_sysconfdir}/samba/lmhosts
%config(noreplace) %{_sysconfdir}/sysconfig/samba
%config(noreplace) %{_sysconfdir}/security/pam_winbind.conf
%dir %{_datadir}/samba
#%dir %{_datadir}/samba/codepages
%dir %{_sysconfdir}/samba
%attr(0700,root,root) %dir /var/log/samba
%{_initrddir}/winbind
%{_mandir}/man1/ntlm_auth.1*
%{_mandir}/man1/profiles.1*
%{_mandir}/man1/smbcquotas.1*
%{_mandir}/man1/smbcontrol.1*
%{_mandir}/man1/wbinfo.1*
#%{_mandir}/man1/vfstest.1*
%{_mandir}/man1/testparm.1*
%{_mandir}/man1/smbstatus.1*
%{_mandir}/man5/smbpasswd.5*
%{_mandir}/man5/smb.conf.5*
%{_mandir}/man5/lmhosts.5*
%{_mandir}/man7/pam_winbind.7*
%{_mandir}/man7/libsmbclient.7*
%{_mandir}/man8/smbpasswd.8*
%{_mandir}/man8/pdbedit.8*
%{_mandir}/man8/net.8*
%{_mandir}/man8/winbindd.8*
%{_mandir}/man8/tdbbackup.8*
%{_mandir}/man8/tdbdump.8*
%{_mandir}/man8/tdbtool.8*
%{_mandir}/man8/idmap_*.8*

%doc README COPYING Manifest 
%doc WHATSNEW.txt Roadmap


%files doc
%doc docs/REVISION docs/Samba3-Developers-Guide.pdf docs/Samba3-ByExample.pdf
%doc docs/Samba3-HOWTO.pdf docs/THANKS docs/history
%doc docs/htmldocs

%files -n libsmbclient
%{_libdir}/libsmbclient.so.0

%files -n libsmbclient-devel
%{_libdir}/libsmbclient.so
%{_includedir}/libsmbclient.h
#%{_includedir}/libmsrpc.h

%changelog
* Tue May 29 2007 Günther Deschner <gdeschner@redhat.com>
- fix pam_smbpass patch.

* Fri May 25 2007 Simo Sorce <ssorce@redhat.com>
- update to 3.0.25a as it contains many fixes
- add a fix for pam_smbpass made by Günther but committed upstream after 3.0.25a was cut.

* Mon May 14 2007 Simo Sorce <ssorce@redhat.com>
- final 3.0.25
- includes security fixes for CVE-2007-2444,CVE-2007-2446,CVE-2007-2447

* Mon Apr 30 2007 Günther Deschner <gdeschner@redhat.com>
- move to 3.0.25rc3

* Thu Apr 19 2007 Simo Sorce <ssorce@redhat.com>
- fixes in the spec file
- moved to 3.0.25rc1
- addedd patches (merged upstream so they will be removed in 3.0.25rc2)

* Wed Apr 4 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-12.fc7
- fixes in smb.conf
- advice in smb.conf to put scripts in /var/lib/samba/scripts
- create /var/lib/samba/scripts so that selinux can be happy
- fix Vista problems with msdfs errors

* Tue Apr 03 2007 Guenther Deschner <gdeschner@redhat.com> 3.0.24-11.fc7
- enable PAM and NSS dlopen checks during build
- fix unresolved symbols in libnss_wins.so (bug #198230)

* Fri Mar 30 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-10.fc7
- set passdb backend = tdbsam as default in smb.conf
- remove samba-docs dependency from swat, that was a mistake
- put back COPYING and other files in samba-common
- put examples in samba not in samba-docs
- leave only stuff under docs/ in samba-doc

* Thu Mar 29 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-9.fc7
- integrate most of merge review proposed changes (bug #226387)
- remove libsmbclient-devel-static and simply stop shipping the
  static version of smbclient as it seem this is deprecated and
  actively discouraged

* Wed Mar 28 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-8.fc7
- fix for bug #176649

* Mon Mar 26 2007 Simo Sorce <ssorce@redhat.com>
- remove patch for bug 106483 as it introduces a new bug that prevents
  the use of a credentials file with the smbclient tar command
- move the samba private dir from being the same as the config dir
  (/etc/samba) to /var/lib/samba/private

* Mon Mar 26 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-7.fc7
- make winbindd start earlier in the init process, at the same time
  ypbind is usually started as well
- add a sepoarate init script for nmbd called nmb, we need to be able
  to restart nmbd without dropping al smbd connections unnecessarily

* Fri Mar 23 2007 Simo Sorce <ssorce@redhat.com>
- add samba.schema to /etc/openldap/schema

* Thu Mar 22 2007 Florian La Roche <laroche@redhat.com>
- adjust the Requires: for the scripts, add "chkconfig --add smb"

* Tue Mar 20 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-6.fc7
- do not put comments inline on smb.conf options, they may be read
  as part of the value (for example log files names)

* Mon Mar 19 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-5.fc7
- actually use the correct samba.pamd file not the old samba.pamd.stack file
- fix logifles and use upstream convention of log.* instead of our old *.log
  Winbindd creates its own log.* files anyway so we will be more consistent
- install our own (enhanced) default smb.conf file
- Fix pam_winbind acct_mgmt PAM result code (prevented local users from
  logging in). Fixed by Guenther.
- move some files from samba to samba-common as they are used with winbindd
  as well

* Fri Mar 16 2007 Guenther Deschner <gdeschner@redhat.com> 3.0.24-4.fc7
- fix arch macro which reported Vista to Samba clients.

* Thu Mar 15 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-3.fc7
- Directories reorg, tdb files must go to /var/lib, not
  to /var/cache, add migration script in %%post common
- Split out libsmbclient, devel and doc packages
- Remove libmsrpc.[h|so] for now as they are not really usable
- Remove kill -HUP from rotate, samba use -HUP for other things
  noit to reopen logs

* Tue Feb 20 2007 Simo Sorce <ssorce@redhat.com> 3.0.24-2.fc7
- New upstream release
- Fix packaging issue wrt idmap modules used only by smbd
- Addedd Vista Patchset for compatibility with Windows Vista
- Change default of "msdfs root", it seem to cause problems with
  some applications and it has been proposed to change it for
  3.0.25 upstream

* Fri Sep 1 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23c-2
- New upstream release.

* Tue Aug 8 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23b-2
- New upstream release.

* Mon Jul 24 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23a-3
- Fix the -logfiles patch to close
  bz#199607 Samba compiled with wrong log path.
  bz#199206 smb.conf has incorrect log file path

* Mon Jul 24 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23a-2
- Upgrade to new upstream 3.0.23a
- include upstream samr_alias patch

* Tue Jul 11 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23-2
- New upstream release.
- Use modified filter-requires-samba.sh from packaging/RHEL/setup/
  to get rid of bogus dependency on perl(Unicode::MapUTF8)
- Update the -logfiles and -smb.conf patches to work with 3.0.23

* Thu Jul 6 2006 Jay Fenlason <fenlason@redhat.com> 3.0.23-0.RC3
- New upstream RC release.
- Update the -logfiles, and -passwd patches for
  3.0.23rc3
- Include the change to smb.init from Bastien Nocera <bnocera@redhat.com>)
  to close
  bz#182560 Wrong retval for initscript when smbd is dead
- Update this spec file to build with 3.0.23rc3
- Remove the -install.mount.smbfs patch, since we don't install
  mount.smbfs any more.

* Wed Jun 14 2006 Tomas Mraz <tmraz@redhat.com> - 2.0.21c-3
- rebuilt with new gnutls

* Fri Mar 17 2006 Jay Fenlason <fenlason@redhat.com> 2.0.21c-2
- New upstream version.

* Mon Feb 13 2006 Jay Fenlason <fenlason@redhat.com> 3.0.21b-2
- New upstream version.
- Since the rawhide kernel has dropped support for smbfs, remove smbmount
  and smbumount.  Users should use mount.cifs instead.
- Upgrade to 3.0.21b

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:3.0.20b-2.1.1
- bump again for double-long bug on ppc(64)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Nov 13 2005 Jay Fenlason <fenlason@redhat.com> 3.0.20b-2
- turn on -DLDAP_DEPRECATED to allow access to ldap functions that have
  been depricated in 2.3.11, but which don't have well-documented
  replacements (ldap_simple_bind_s(), for example).
- Upgrade to 3.0.20b, which includes all the previous upstream patches.
- Updated the -warnings patch for 3.0.20a.
- Include  --with-shared-modules=idmap_ad,idmap_rid to close
  bz#156810 --with-shared-modules=idmap_ad,idmap_rid
- Include the new samba.pamd from Tomas Mraz (tmraz@redhat.com) to close
  bz#170259 pam_stack is deprecated

* Sun Nov 13 2005 Warren Togami <wtogami@redhat.com> 3.0.20-3
- epochs from deps, req exact release
- rebuild against new openssl

* Mon Aug 22 2005 Jay Fenlason <fenlason@redhat.com> 3.0.20-2
- New upstream release
  Includes five upstream patches -bug3010_v1, -groupname_enumeration_v3,
    -regcreatekey_winxp_v1, -usrmgr_groups_v1, and -winbindd_v1
  This obsoletes the -pie and -delim patches
  the -warning and -gcc4 patches are obsolete too
  The -man, -passwd, and -smbspool patches were updated to match 3.0.20pre1
  Also, the -quoting patch was implemented differently upstream
  There is now a umount.cifs executable and manpage
  We run autogen.sh as part of the build phase
  The testprns command is now gone
  libsmbclient now has a man page
- Include -bug106483 patch to close
  bz#106483 smbclient: -N negates the provided password, despite documentation
- Added the -warnings patch to quiet some compiler warnings.
- Removed many obsolete patches from CVS.

* Mon May 2 2005 Jay Fenlason <fenlason@redhat.com> 3.0.14a-2
- New upstream release.
- the -64bit-timestamps, -clitar, -establish_trust, user_rights_v1,
  winbind_find_dc_v2 patches are now obsolete.

* Thu Apr 7 2005 Jay Fenlason <fenlason@redhat.com> 3.0.13-2
- New upstream release
- add my -quoting patch, to fix swat with strings that contain
  html meta-characters, and to use correct quote characters in
  lists, closing bz#134310
- include the upstream winbindd_2k3sp1 patch
- include the -smbclient patch.
- include the -hang patch from upstream.

* Thu Mar 24 2005 Florian La Roche <laroche@redhat.com>
- add a "exit 0" to the postun of the main samba package

* Wed Mar  2 2005 Tomas Mraz <tmraz@redhat.com> 3.0.11-5
- rebuild with openssl-0.9.7e

* Thu Feb 24 2005 Jay Fenlason <fenlason@redhat.com> 3.0.11-4
- Use the updated filter-requires-samba.sh file, so we don't accidentally
  pick up a dependency on perl(Crypt::SmbHash)

* Fri Feb 18 2005 Jay Fenlason <fenlason@redhat.com> 3.0.11-3
- add -gcc4 patch to compile with gcc 4.
- remove the now obsolete -smbclient-kerberos.patch
- Include four upstream patches from
  http://samba.org/~jerry/patches/post-3.0.11/
  (Slightly modified the winbind_find_dc_v2 patch to apply easily with
  rpmbuild).

* Fri Feb 4 2005 Jay Fenlason <fenlason@redhat.com> 3.0.11-2
- include -smbspool patch to close bz#104136

* Wed Jan 12 2005 Jay Fenlason <fenlason@redhat.com> 3.0.10-4
- Update the -man patch to fix ntlm_auth.1 too.
- Move pam_smbpass.so to the -common package, so both the 32
  and 64-bit versions will be installed on multiarch platforms.
  This closes bz#143617
- Added new -delim patch to fix mount.cifs so it can accept
  passwords with commas in them (via environment or credentials
  file) to close bz#144198

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> 3.0.10-3
- Rebuilt for new readline.

* Fri Dec 17 2004 Jay Fenlason <fenlason@redhat.com> 3.0.10-2
- New upstream release that closes CAN-2004-1154  bz#142544
- Include the -64bit patch from Nalin.  This closes bz#142873
- Update the -logfiles patch to work with 3.0.10
- Create /var/run/winbindd and make it part of the -common rpm to close
  bz#142242

* Mon Nov 22 2004 Jay Fenlason <fenlason@redhat.com> 3.0.9-2
- New upstream release.  This obsoletes the -secret patch.
  Include my changetrustpw patch to make "net ads changetrustpw" stop
  aborting.  This closes #134694
- Remove obsolete triggers for ancient samba versions.
- Move /var/log/samba to the -common rpm.  This closes #76628
- Remove the hack needed to get around the bad docs files in the
  3.0.8 tarball.
- Change the comment in winbind.init to point at the correct pidfile.
  This closes #76641

* Mon Nov 22 2004 Than Ngo <than@redhat.com> 3.0.8-4
- fix unresolved symbols in libsmbclient which caused applications
  such as KDE's konqueror to fail when accessing smb:// URLs. #139894

* Thu Nov 11 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-3.1
- Rescue the install.mount.smbfs patch from Juanjo Villaplana
  (villapla@si.uji.es) to prevent building the srpm from trashing your
  installed /usr/bin/smbmount

* Tue Nov 9 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-3
- Include the corrected docs tarball, and use it instead of the
  obsolete docs from the upstream 3.0.8 tarball.
- Update the logfiles patch to work with the updated docs.

* Mon Nov 8 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-2
- New upstream version fixes CAN-2004-0930.  This obsoletes the
  disable-sendfile, salt, signing-shortkey and fqdn patches.
- Add my <fenlason@redhat.com> ugly non-ascii-domain patch.
- Updated the pie patch for 3.0.8.
- Updated the logfiles patch for 3.0.8.

* Tue Oct 26 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre2
- New upstream version
- Add Nalin's signing-shortkey patch.

* Tue Oct 19 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1.3
- disable the -salt patch, because it causes undefined references in
  libsmbclient that prevent gnome-vfs from building.

* Fri Oct 15 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1.2
- Re-enable the x_fclose patch that was accidentally disabled
  in 3.0.8-0.pre1.1.  This closes #135832
- include Nalin's -fqdn and -salt patches.

* Wed Oct 13 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1.1
- Include disable-sendfile patch to default "use sendfile" to "no".
  This closes #132779

* Wed Oct 6 2004 Jay Fenlason <fenlason@redhat.com>
- Include patch from Steven Lawrance (slawrance@yahoo.com) that modifies
  smbmnt to work with 32-bit uids.

* Mon Sep 27 2004 Jay Fenlason <fenlason@redhat.com> 3.0.8-0.pre1
- new upstream release.  This obsoletes the ldapsam_compat patches.

* Wed Sep 15 2004 Jay Fenlason <fenlason@redhat.com> 3.0.7-4
- Update docs section to not carryover the docs/manpages directory
  This moved many files from /usr/share/doc/samba-3.0.7/docs/* to
  /usr/share/doc/samba-3.0.7/*
- Modify spec file as suggested by Rex Dieter (rdieter@math.unl.edu)
  to correctly create libsmbclient.so.0 and to use %%_initrddir instead
  of rolling our own.  This closes #132642
- Add patch to default "use sendfile" to no, since sendfile appears to
  be broken
- Add patch from Volker Lendecke <vl@samba.org> to help make
  ldapsam_compat work again.
- Add patch from "Vince Brimhall" <vbrimhall@novell.com> for ldapsam_compat
  These two patches close bugzilla #132169

* Mon Sep 13 2004 Jay Fenlason <fenlason@redhat.com> 3.0.7-3
- Upgrade to 3.0.7, which fixes CAN-2004-0807 CAN-2004-0808
  This obsoletes the 3.0.6-schema patch.
- Update BuildRequires line to include openldap-devel openssl-devel
  and cups-devel

* Mon Aug 16 2004 Jay Fenlason <fenlason@redhat.com> 3.0.6-3
- New upstream version.
- Include post 3.0.6 patch from "Gerald (Jerry) Carter" <jerry@samba.org>
  to fix a duplicate in the LDAP schema.
- Include 64-bit timestamp patch from Ravikumar (rkumar@hp.com)
  to allow correct timestamp handling on 64-bit platforms and fix #126109.
- reenable the -pie patch.  Samba is too widely used, and too vulnerable
  to potential security holes to disable an important security feature
  like -pie.  The correct fix is to have the toolchain not create broken
  executables when programs compiled -pie are stripped.
- Remove obsolete patches.
- Modify this spec file to put libsmbclient.{a,so} in the right place on
  x86_64 machines.

* Wed Aug  5 2004 Jason Vas Dias <jvdias@redhat.com> 3.0.5-3
- Removed '-pie' patch - 3.0.5 uses -fPIC/-PIC, and the combination
- resulted in executables getting corrupt stacks, causing smbmnt to
- get a SIGBUS in the mount() call (bug 127420).

* Fri Jul 30 2004 Jay Fenlason <fenlason@redhat.com> 3.0.5-2
- Upgrade to 3.0.5, which is a regression from 3.0.5pre1 for a
  security fix.
- Include the 3.0.4-backport patch from the 3E branch.  This restores
  some of the 3.0.5pre1 and 3.0.5rc1 functionality.

* Tue Jul 20 2004 Jay Fenlason <fenlason@redhat.com> 3.0.5-0.pre1.1
- Backport base64_decode patche to close CAN-2004-0500
- Backport hash patch to close CAN-2004-0686
- use_authtok patch from Nalin Dahyabhai <nalin@redhat.com>
- smbclient-kerberos patch from Alexander Larsson <alexl@redhat.com>
- passwd patch uses "*" instead of "x" for "hashed" passwords for
  accounts created by winbind.  "x" means "password is in /etc/shadow" to
  brain-damaged pam_unix module.

* Fri Jul 2 2004 Jay Fenlason <fenlason@redhat.com> 3.0.5.0pre1.0
- New upstream version
- use %% { SOURCE1 } instead of a hardcoded path
- include -winbind patch from Gerald (Jerry) Carter (jerry@samba.org)
  https://bugzilla.samba.org/show_bug.cgi?id=1315
  to make winbindd work against Windows versions that do not have
  128 bit encryption enabled.
- Moved %%{_bindir}/net to the -common package, so that folks who just
  want to use winbind, etc don't have to install -client in order to
  "net join" their domain.
- New upstream version obsoletes the patches added in 3.0.3-5
- Remove smbgetrc.5 man page, since we don't ship smbget.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue May 4 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-5
- Patch to allow password changes from machines patched with
  Microsoft hotfix MS04-011.
- Include patches for https://bugzilla.samba.org/show_bug.cgi?id=1302
  and https://bugzilla.samba.org/show_bug.cgi?id=1309

* Thu Apr 29 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-4
- Samba 3.0.3 released.

* Wed Apr 21 2004 jay Fenlason <fenlason@redhat.com> 3.0.3-3.rc1
- New upstream version
- updated spec file to make libsmbclient.so executable.  This closes
  bugzilla #121356

* Mon Apr 5 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-2.pre2
- New upstream version  
- Updated configure line to remove --with-fhs and to explicitly set all
  the directories that --with-fhs was setting.  We were overriding most of
  them anyway.  This closes #118598

* Mon Mar 15 2004 Jay Fenlason <fenlason@redhat.com> 3.0.3-1.pre1
- New upstream version.
- Updated -pie and -logfiles patches for 3.0.3pre1
- add krb5-devel to buildrequires, fixes #116560
- Add patch from Miloslav Trmac (mitr@volny.cz) to allow non-root to run
  "service smb status".  This fixes #116559

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Feb 16 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2a-1
- Upgrade to 3.0.2a

* Mon Feb 16 2004 Karsten Hopp <karsten@redhat.de> 3.0.2-7 
- fix ownership in -common package

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Jay Fenlason <fenlason@redhat.com>
- Change all requires lines to list an explicit epoch.  Closes #102715
- Add an explicit Epoch so that %%{epoch} is defined.

* Mon Feb 9 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2-5
- New upstream version: 3.0.2 final includes security fix for #114995
  (CAN-2004-0082)
- Edit postun script for the -common package to restart winbind when
  appropriate.  Fixes bugzilla #114051.

* Mon Feb 2 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2-3rc2
- add %%dir entries for %%{_libdir}/samba and %%{_libdir}/samba/charset
- Upgrade to new upstream version
- build mount.cifs for the new cifs filesystem in the 2.6 kernel.

* Mon Jan 19 2004 Jay Fenlason <fenlason@redhat.com> 3.0.2-1rc1
- Upgrade to new upstream version

* Wed Dec 17 2003 Felipe Alfaro Solana <felipe_alfaro@linuxmail.org> 3.0.1-1
- Update to 3.0.1
- Removed testparm patch as it's already merged
- Removed Samba.7* man pages
- Fixed .buildroot patch
- Fixed .pie patch
- Added new /usr/bin/tdbdump file

* Thu Sep 25 2003 Jay Fenlason <fenlason@redhat.com> 3.0.0-15
- New 3.0.0 final release
- merge nmbd-netbiosname and testparm patches from 3E branch
- updated the -logfiles patch to work against 3.0.0
- updated the pie patch
- update the VERSION file during build
- use make -j if avaliable
- merge the winbindd_privileged change from 3E
- merge the "rm /usr/lib" patch that allows Samba to build on 64-bit
  platforms despite the broken Makefile

* Mon Aug 18 2003 Jay Fenlason <fenlason@redhat.com>
- Merge from samba-3E-branch after samba-3.0.0rc1 was released

* Wed Jul 23 2003 Jay Fenlason <fenlason@redhat.com> 3.0.0-3beta3
- Merge from 3.0.0-2beta3.3E
- (Correct log file names (#100981).)
- (Fix pidfile directory in samab.log)
- (Remove obsolete samba-3.0.0beta2.tar.bz2.md5 file)
- (Move libsmbclient to the -common package (#99449))

* Tue Jun 22 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2.8a-4
- rebuild

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 28 2003 Jay Fenlason <fenlason@redhat.com> 2.2.8a-2
- add libsmbclient.so for gnome-vfs-extras
- Edit specfile to specify /var/run for pid files
- Move /tmp/.winbindd/socket to /var/run/winbindd/socket

* Wed May 14 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- add proper ldconfig calls

* Thu Apr 24 2003 Jay Fenlason <fenlason@redhat.com> 2.2.8a-1
- upgrade to 2.2.8a
- remove old .md5 files
- add "pid directory = /var/run" to the smb.conf file.  Fixes #88495
- Patch from jra@dp.samba.org to fix a delete-on-close regression

* Mon Mar 24 2003 Jay Fenlason <fenlason@redhat.com> 2.2.8-0
- Upgrade to 2.2.8
- removed commented out patches.
- removed old patches and .md5 files from the repository.
- remove duplicate /sbin/chkconfig --del winbind which causes
  warnings when removing samba.
- Fixed minor bug in smbprint that causes it to fail when called with
  more than 10 parameters: the accounting file (and spool directory
  derived from it) were being set wrong due to missing {}.  This closes
  bug #86473.
- updated smb.conf patch, includes new defaults to close bug #84822.

* Mon Feb 24 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 20 2003 Jonathan Blandford <jrb@redhat.com> 2.2.7a-5
- remove swat.desktop file

* Thu Feb 20 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2.7a-4
- relink libnss_wins.so with SHLD="%%{__cc} -lnsl" to force libnss_wins.so to
  link with libnsl, avoiding unresolved symbol errors on functions in libnsl

* Mon Feb 10 2003 Jay Fenlason <fenlason@redhat.com> 2.2.7a-3
- edited spec file to put .so files in the correct directories
  on 64-bit platforms that have 32-bit compatability issues
  (sparc64, x86_64, etc).  This fixes bugzilla #83782.
- Added samba-2.2.7a-error.patch from twaugh.  This fixes
  bugzilla #82454.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jan  9 2003 Jay Fenlason <fenlason@redhat.com> 2.2.7a-1
- Update to 2.2.7a
- Change default printing system to CUPS
- Turn on pam_smbpass
- Turn on msdfs

* Sat Jan  4 2003 Jeff Johnson <jbj@redhat.com> 2.2.7-5
- use internal dep generator.

* Sat Dec 14 2002 Tim Powers <timp@redhat.com> 2.2.7-4
- don't use rpms internal dep generator

* Mon Dec 02 2002 Elliot Lee <sopwith@redhat.com> 2.2.7-3
- Fix missing doc files.
- Fix multilib issues

* Wed Nov 20 2002 Bill Nottingham <notting@redhat.com> 2.2.7-2
- update to 2.2.7
- add patch for LFS in smbclient (<tcallawa@redhat.com>)

* Wed Aug 28 2002 Trond Eivind Glomsød <teg@redhat.com> 2.2.5-10
- logrotate fixes (#65007)

* Mon Aug 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-9
- /usr/lib was used in place of %%{_libdir} in three locations (#72554)

* Mon Aug  5 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-8
- Initscript fix (#70720)

* Fri Jul 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-7
- Enable VFS support and compile the "recycling" module (#69796)
- more selective includes of the examples dir 

* Tue Jul 23 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-6
- Fix the lpq parser for better handling of LPRng systems (#69352)

* Tue Jul 23 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-5
- desktop file fixes (#69505)

* Wed Jun 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-4
- Enable ACLs

* Tue Jun 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-3
- Make it not depend on Net::LDAP - those are doc files and examples

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Jun 20 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.5-1
- 2.2.5

* Fri Jun 14 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-5
- Move the post/preun of winbind into the -common subpackage, 
  where the script is (#66128)

* Tue Jun  4 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-4
- Fix pidfile locations so it runs properly again (2.2.4 
  added a new directtive - #65007)

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 14 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-2
- Fix #64804

* Thu May  9 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.4-1
- 2.2.4
- Removed some zero-length and CVS internal files
- Make it build

* Wed Apr 10 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-6
- Don't use /etc/samba.d in smbadduser, it should be /etc/samba

* Thu Apr  4 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-5
- Add libsmbclient.a w/headerfile for KDE (#62202)

* Tue Mar 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-4
- Make the logrotate script look the correct place for the pid files 

* Thu Mar 14 2002 Nalin Dahyabhai <nalin@redhat.com> 2.2.3a-3
- include interfaces.o in pam_smbpass.so, which needs symbols from interfaces.o
  (patch posted to samba-list by Ilia Chipitsine)

* Thu Feb 21 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-2
- Rebuild

* Thu Feb  7 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3a-1
- 2.2.3a

* Mon Feb  4 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.2.3-1
- 2.2.3

* Thu Nov 29 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-8
- New pam configuration file for samba

* Tue Nov 27 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-7
- Enable PAM session controll and password sync

* Tue Nov 13 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-6
- Move winbind files to samba-common. Add separate initscript for
  winbind 
- Fixes for winbind - protect global variables with mutex, use
  more secure getenv

* Thu Nov  8 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-5
- Teach smbadduser about "getent passwd" 
- Fix more pid-file references
- Add (conditional) winbindd startup to the initscript, configured in
  /etc/sysconfig/samba

* Wed Nov  7 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-4
- Fix pid-file reference in logrotate script
- include pam and nss modules for winbind

* Mon Nov  5 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-3
- Add "--with-utmp" to configure options (#55372)
- Include winbind, pam_smbpass.so, rpcclient and smbcacls
- start using /var/cache/samba, we need to keep state and there is
  more than just locks involved

* Sat Nov 03 2001 Florian La Roche <Florian.LaRoche@redhat.de> 2.2.2-2
- add "reload" to the usage string in the startup script

* Mon Oct 15 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.2-1
- 2.2.2

* Tue Sep 18 2001 Trond Eivind Glomsrød <teg@redhat.com> 2.2.1a-5
- Add patch from Jeremy Allison to fix IA64 alignment problems (#51497)

* Mon Aug 13 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Don't include smbpasswd in samba, it's in samba-common (#51598)
- Add a disabled "obey pam restrictions" statement - it's not
  active, as we use encrypted passwords, but if the admin turns
  encrypted passwords off the choice is available. (#31351)

* Wed Aug  8 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Use /var/cache/samba instead of /var/lock/samba 
- Remove "domain controller" keyword from smb.conf, it's 
  deprecated (from #13704)
- Sync some examples with smb.conf.default
- Fix password synchronization (#16987)

* Fri Jul 20 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Tweaks of BuildRequires (#49581)

* Wed Jul 11 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.2.1a bugfix release

* Tue Jul 10 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.2.1, which should work better for XP

* Sat Jun 23 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 2.2.0a security fix
- Mark lograte and pam configuration files as noreplace

* Fri Jun 22 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add the /etc/samba directory to samba-common

* Thu Jun 21 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Add improvements to the smb.conf as suggested in #16931

* Tue Jun 19 2001 Trond Eivind Glomsrød <teg@redhat.com>
  (these changes are from the non-head version)
- Don't include /usr/sbin/samba, it's the same as the initscript
- unset TMPDIR, as samba can't write into a TMPDIR owned 
  by root (#41193)
- Add pidfile: lines for smbd and nmbd and a config: line
  in the initscript  (#15343)
- don't use make -j
- explicitly include /usr/share/samba, not just the files in it

* Tue Jun 19 2001 Bill Nottingham <notting@redhat.com>
- mount.smb/mount.smbfs go in /sbin, *not* %%{_sbindir}

* Fri Jun  8 2001 Preston Brown <pbrown@redhat.com>
- enable encypted passwords by default

* Thu Jun  7 2001 Helge Deller <hdeller@redhat.de> 
- build as 2.2.0-1 release
- skip the documentation-directories docbook, manpages and yodldocs
- don't include *.sgml documentation in package
- moved codepage-directory to /usr/share/samba/codepages
- make it compile with glibc-2.2.3-10 and kernel-headers-2.4.2-2   

* Mon May 21 2001 Helge Deller <hdeller@redhat.de> 
- updated to samba 2.2.0
- moved codepages to %%{_datadir}/samba/codepages
- use all available CPUs for building rpm packages
- use %%{_xxx} defines at most places in spec-file
- "License:" replaces "Copyright:"
- dropped excludearch sparc
- de-activated japanese patches 100 and 200 for now 
  (they need to be fixed and tested wth 2.2.0)
- separated swat.desktop file from spec-file and added
  german translations
- moved /etc/sysconfig/samba to a separate source-file
- use htmlview instead of direct call to netscape in 
  swat.desktop-file

* Mon May  7 2001 Bill Nottingham <notting@redhat.com>
- device-remove security fix again (<tridge@samba.org>)

* Fri Apr 20 2001 Bill Nottingham <notting@redhat.com>
- fix tempfile security problems, officially (<tridge@samba.org>)
- update to 2.0.8

* Sun Apr  8 2001 Bill Nottingham <notting@redhat.com>
- turn of SSL, kerberos

* Thu Apr  5 2001 Bill Nottingham <notting@redhat.com>
- fix tempfile security problems (patch from <Marcus.Meissner@caldera.de>)

* Thu Mar 29 2001 Bill Nottingham <notting@redhat.com>
- fix quota support, and quotas with the 2.4 kernel (#31362, #33915)

* Mon Mar 26 2001 Nalin Dahyabhai <nalin@redhat.com>
- tweak the PAM code some more to try to do a setcred() after initgroups()
- pull in all of the optflags on i386 and sparc
- don't explicitly enable Kerberos support -- it's only used for password
  checking, and if PAM is enabled it's a no-op anyway

* Mon Mar  5 2001 Tim Waugh <twaugh@redhat.com>
- exit successfully from preun script (bug #30644).

* Fri Mar  2 2001 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Wed Feb 14 2001 Bill Nottingham <notting@redhat.com>
- updated japanese stuff (#27683)

* Fri Feb  9 2001 Bill Nottingham <notting@redhat.com>
- fix trigger (#26859)

* Wed Feb  7 2001 Bill Nottingham <notting@redhat.com>
- add i18n support, japanese patch (#26253)

* Wed Feb  7 2001 Trond Eivind Glomsrød <teg@redhat.com>
- i18n improvements in initscript (#26537)

* Wed Jan 31 2001 Bill Nottingham <notting@redhat.com>
- put smbpasswd in samba-common (#25429)

* Wed Jan 24 2001 Bill Nottingham <notting@redhat.com>
- new i18n stuff

* Sun Jan 21 2001 Bill Nottingham <notting@redhat.com>
- rebuild

* Thu Jan 18 2001 Bill Nottingham <notting@redhat.com>
- i18n-ize initscript
- add a sysconfig file for daemon options (#23550)
- clarify smbpasswd man page (#23370)
- build with LFS support (#22388)
- avoid extraneous pam error messages (#10666)
- add Urban Widmark's bug fixes for smbmount (#19623)
- fix setgid directory modes (#11911)
- split swat into subpackage (#19706)

* Wed Oct 25 2000 Nalin Dahyabhai <nalin@redhat.com>
- set a default CA certificate path in smb.conf (#19010)
- require openssl >= 0.9.5a-20 to make sure we have a ca-bundle.crt file

* Mon Oct 16 2000 Bill Nottingham <notting@redhat.com>
- fix swat only_from line (#18726, others)
- fix attempt to write outside buildroot on install (#17943)

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
- add a %%defattr for -common

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
- add a %%trigger to work around (sort of) broken scripts in
  previous releases

* Mon Aug 16 1999 Bill Nottingham <notting@redhat.com>
- initscript munging

* Mon Aug  9 1999 Bill Nottingham <notting@redhat.com>
- add domain parsing to mount.smb

* Fri Aug  6 1999 Bill Nottingham <notting@redhat.com>
- add a -common package, shuffle files around.

* Fri Jul 23 1999 Bill Nottingham <notting@redhat.com>
- add a chmod in %%postun so /etc/services & inetd.conf don't become unreadable

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
- fix %%triggerpostun.

* Tue Jul 07 1998 Erik Troan <ewt@redhat.com>
- updated postun triggerscript to check $0
- clear /etc/codepages from %%preun instead of %%postun

* Mon Jun 08 1998 Erik Troan <ewt@redhat.com>
- made the %%postun script a tad less agressive; no reason to remove
  the logs or lock file (after all, if the lock file is still there,
  samba is still running)
- the %%postun and %%preun should only exectute if this is the final
  removal
- migrated %%triggerpostun from Red Hat's samba package to work around
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

