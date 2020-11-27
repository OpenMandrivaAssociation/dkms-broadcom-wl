%define debug_package %{nil}
%define module_name broadcom-wl
%define kname	wl

Name:		dkms-%{module_name}
Version:	6.30.223.271
Release:	4
Summary:	DKMS-ready kernel-source for the %name driver
License:	Mixed
Group:		System/Kernel and hardware
URL:		http://www.broadcom.com/support/?gid=1
ExclusiveArch:	x86_64 %{ix86}
%ifarch x86_64
Source0:	http://www.broadcom.com/docs-and-downloads/docs/linux_sta/hybrid-v35_64-nodebug-pcoem-%(echo %{version} |sed -e 's,\.,_,g').tar.gz
%else
Source0:	http://www.broadcom.com/docs-and-downloads/docs/linux_sta/hybrid-v35-nodebug-pcoem-%(echo %{version} |sed -e 's,\.,_,g').tar.gz
%endif
Source100:	%{name}.rpmlintrc
Source2:	broadcom-wl-blacklist.conf
Source3:	broadcom-wl-alias.conf
# fix crash (ubuntu, mga#16390)
Patch6:		broadcom-wl-6.30.223.271-fix-null-pointer-crash.patch
# fix build with 4.3 (aur)
Patch7:		broadcom-wl-6.30.223.271-kernel-4.3-rdtscl-buildfix.patch
# (tmb) fix build with 4.7
Patch8:		broadcom-wl-6.30.223.271-kernel-4.7-buildfix.patch
# (tmb) fix build with 4.8 (aur)
Patch9:		broadcom-wl-6.30.223.271-kernel-4.8-buildfix.patch
# (tmb) fix build with 4.11 (debian)
Patch10:	broadcom-wl-6.30.223.271-kernel-4.11-buildfix.patch
# (tmb) fix build with 4.12 (aur)
Patch11:	broadcom-wl-6.30.223.271-kernel-4.12-buildfix.patch
# (tmb) fix build with 4.14 (debian)
Patch12:	broadcom-wl-6.30.223.271-kernel-4.14-buildfix.patch
# (tmb) fix build with 4.15 (debian)
Patch13:	broadcom-wl-6.30.223.271-kernel-4.15-buildfix.patch
# (tmb) fix build with 5.1
Patch14:	broadcom-wl-6.30.223.271-kernel-5.1-buildfix.patch
# fix kernel warnings (debian)
Patch15:	broadcom-wl-6.30.223.271-debian-fix-kernel-warnings.patch
# fix mac profile discrepancy (debian)
Patch16:	broadcom-wl-6.30.223.271-fix_mac_profile_discrepancy.patch
# Allow normal users to send ioctl requests (debian)
Patch17:	broadcom-wl-6.30.223.271-allow-user_ioctl.patch
# (tmb) default wifi interface name should be wlan, not eth
Patch18:	broadcom-wl-6.30.223.271-ifname-wlan.patch
# (tmb) fix build with 5.6
Patch19:	broadcom-wl-6.30.223.271-kernel-5.6-buildfix.patch
# (tmb) disable time-date warnign
Patch20:	broadcom-wl-6.30.223.271-no-date-time.patch
# fix build error "/bin/sh: 1: [: Illegal number:" (debian)
Patch21:	broadcom-wl-6.30.223.271-debian-fix-dkms-build-error.patch
# fix build with 5.9 (debian)
Patch22:	broadcom-wl-6.30.223.271-kernel-5.9-buildfix.patch


%description
DKMS driver for Broadcom WiFi chips

Provides:	kmod(%{kname}.ko) = %{version}
Requires:		dkms >= 2.0.19-37
Requires(post):		dkms >= 2.0.19-37
Requires(preun):	dkms >= 2.0.19-37
Requires:	%{name}-common

%rename		broadcom-wl-kernel-release-desktop
%rename		broadcom-wl-kernel--release-server

%package -n %{name}-common
Summary:	Common files for Broadcom-wl drivers
Group:		System/Kernel and hardware
Conflicts:	dkms-%{name} <= 5.100.82.112-7
Conflicts:	broadcom-bcma-config
Conflicts:	broadcom-ssb-config

%description -n %{name}-common
This package contains the blacklist and ldetect-lst files shared
between dkms-broadcom-wl and the prebuilt broadcom-wl-* drivers.


%prep
%setup -qcn %module_name-%version
%autopatch -p1

%build

%install
rm -rf %{buildroot}

# add blacklist for conflicting in-kernel modules
install -m755 -d %{buildroot}%{_sysconfdir}/modprobe.d/
install -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modprobe.d
# add pciids for ldetect-lst and libkmod
install -m644 %{SOURCE3} %{buildroot}%{_sysconfdir}/modprobe.d

# install dkms sources
mkdir -p %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}
cp -R * %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/
cat > %{buildroot}%{_usr}/src/%{name}-%{version}-%{release}/dkms.conf << EOF
MAKE="'make' -j\${parallel_jobs} -C \$kernel_source_dir M=\\\$(pwd)"
PACKAGE_NAME=%{name}
PACKAGE_VERSION=%{version}-%{release}
DEST_MODULE_LOCATION=/kernel/3rdparty/%{name}
BUILT_MODULE_NAME=%{kname}
AUTOINSTALL=yes
EOF

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{name} -v %{version}-%{release}
if [ -z "$DURING_INSTALL" ] ; then
    /usr/sbin/dkms --rpm_safe_upgrade build -m %{name} -v %{version}-%{release} &&
    /usr/sbin/dkms --rpm_safe_upgrade install -m %{name} -v %{version}-%{release}
fi

%preun
# rmmod can fail
/sbin/rmmod %{kname} >/dev/null 2>&1 ||:
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{name} -v %{version}-%{release} --all || :

%posttrans -n %{name}-common
if [ -z "$DURING_INSTALL" ] ; then
    /sbin/rmmod b43 >/dev/null 2>&1 ||:
    /sbin/rmmod b43legacy >/dev/null 2>&1 ||:
    /sbin/rmmod brcmfmac >/dev/null 2>&1 ||:
    /sbin/rmmod brcmsmac >/dev/null 2>&1 ||:
    /sbin/rmmod bcma >/dev/null 2>&1 ||:
    /sbin/rmmod ssb >/dev/null 2>&1 ||:
    /sbin/modprobe wl >/dev/null 2>&1 ||:
fi

%clean
rm -rf %{buildroot}

%files
%doc lib/LICENSE.txt
%dir %{_usr}/src/%{name}-%{version}-%{release}
%{_usr}/src/%{name}-%{version}-%{release}/*

%files -n %{name}-common
#config #{_sysconfdir}/modprobe.d/%{name}-alias.conf
#config #{_sysconfdir}/modprobe.d/%{name}-blacklist.conf

%config %{_sysconfdir}/modprobe.d/broadcom-wl-alias.conf
%config %{_sysconfdir}/modprobe.d/broadcom-wl-blacklist.conf
