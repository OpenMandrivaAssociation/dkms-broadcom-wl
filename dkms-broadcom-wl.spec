%define debug_package %{nil}
%define module_name broadcom-wl

Name:		dkms-%{module_name}
Version:	6.30.223.271
Release:	1
Summary:	DKMS-ready kernel-source for the %name driver
License:	Mixed
URL:		http://www.broadcom.com/support/?gid=1
ExclusiveArch:	x86_64 %{ix86}
%ifarch x86_64
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-v35_64-nodebug-pcoem-%(echo %{version} |sed -e 's,\.,_,g').tar.gz
%else
Source0:	http://www.broadcom.com/docs/linux_sta/hybrid-v35-nodebug-pcoem-%(echo %{version} |sed -e 's,\.,_,g').tar.gz
%endif
Source100:	%{name}.rpmlintrc
# Patches stolen from https://aur.archlinux.org/packages/broadcom-wl-dkms/
Patch1:		broadcom-wl-6.30.223.271-fix-null-pointer-crash.patch
Group:		System/Kernel and hardware
Requires(pre):	dkms
Requires(post): dkms

%description
Driver for Broadcom WiFi chips

%prep
%setup -qcn %module_name-%version
%apply_patches

# Since we're actually packaging the source...
find . -name "*~" |xargs rm

%build

%install
mkdir -p %{buildroot}/usr/src/%{module_name}-%{version}-%{release}
cat >$RPM_BUILD_ROOT/usr/src/%{module_name}-%version-%release/dkms.conf <<"EOF"
PACKAGE_NAME="%{module_name}"
PACKAGE_VERSION="%{version}"
CLEAN="make clean"
BUILT_MODULE_NAME[0]="wl"
MAKE[0]="make"
DEST_MODULE_LOCATION[0]="/kernel/drivers/net/wireless/broadcom"
AUTOINSTALL="yes"
EOF
cp -a * $RPM_BUILD_ROOT/usr/src/%{module_name}-%version-%release/


%post
dkms add -m %{module_name} -v %{version}-%{release} --rpm_safe_upgrade
dkms build -m %{module_name} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m %{module_name} -v %{version}-%{release} --rpm_safe_upgrade

%preun
dkms remove -m %{module_name} -v %{version}-%{release} --rpm_safe_upgrade --all ||:

%files
%defattr(-,root,root)
/usr/src/%{module_name}-%{version}-%{release}
