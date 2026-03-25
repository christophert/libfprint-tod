%global __brp_check_rpaths %{nil}
%global with_selinux 1
%global modulename libfprint-tod
%global selinuxtype targeted

Name:           libfprint-tod

Version:        1.95.1+tod1
Release:        1%{?dist}
Summary:        Toolkit for fingerprint scanner (TOD version)

License:        LGPLv2+
URL:            http://www.freedesktop.org/wiki/Software/fprint/libfprint
Source0:        https://gitlab.freedesktop.org/3v1n0/libfprint/-/archive/v%{version}/libfprint-v%{version}.tar.gz
Source1:        %{modulename}.te
ExcludeArch:    s390 s390x

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  openssl-devel
BuildRequires:  pkgconfig(glib-2.0) >= 2.50
BuildRequires:  pkgconfig(gio-2.0) >= 2.44.0
BuildRequires:  pkgconfig(gusb) >= 0.3.0
BuildRequires:  pkgconfig(nss)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  gtk-doc
BuildRequires:  libgudev-devel
# For the udev.pc to install the rules
BuildRequires:  systemd
BuildRequires:  cmake
BuildRequires:  libgudev-devel
BuildRequires:  gdb
BuildRequires:  valgrind
BuildRequires:  gobject-introspection-devel
# For internal CI tests; umockdev 0.13.2 has an important locking fix
BuildRequires:  python3-cairo python3-gobject cairo-devel
BuildRequires:  umockdev >= 0.13.2
# For SELinux Module
%if 0%{?with_selinux}
# This ensures that the *-selinux package and all its dependencies are not pulled
# into containers and other systems that do not use SELinux
Requires:        (%{name}-selinux if selinux-policy-%{selinuxtype})
%endif
Conflicts:      libfprint

%description
libfprint-tod offers support for consumer fingerprint reader devices.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        tests
Summary:        Tests for the %{name} package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description tests
The %{name}-tests package contains tests that can be used to verify
the functionality of the installed %{name} package.

%if 0%{?with_selinux}
# SELinux subpackage
%package selinux
Summary:             libfprint-tod SELinux policy
BuildArch:           noarch
Requires:            selinux-policy-%{selinuxtype}
Requires(post):      selinux-policy-%{selinuxtype}
BuildRequires:       selinux-policy-devel
%{?selinux_requires}

%description selinux
Custom SELinux policy module for libfprint-tod
%endif

%prep
%autosetup -S git -n libfprint-v%{version}

%build
# Include the virtual image driver for integration tests
%meson -Ddrivers=all
%meson_build
%if 0%{?with_selinux}
# SELinux policy (originally from selinux-policy-contrib)
# this policy module will override the production module
mkdir selinux
cp -p %{SOURCE1} selinux/
make -f %{_datadir}/selinux/devel/Makefile %{modulename}.pp
bzip2 -9 %{modulename}.pp
%endif

%install
%meson_install
mkdir -vp %{buildroot}/usr/lib64/libfprint-2/tod-1
%if 0%{?with_selinux}
install -D -m 0644 %{modulename}.pp.bz2 %{buildroot}%{_datadir}/selinux/packages/%{selinuxtype}/%{modulename}.pp.bz2
install -D -p -m 0644 selinux/%{modulename}.if %{buildroot}%{_datadir}/selinux/devel/include/distributed/%{modulename}.if
%endif

%ldconfig_scriptlets

%if 0%{?with_selinux}
# SELinux contexts are saved so that only affected files can be
# relabeled after the policy module installation
%pre selinux
%selinux_relabel_pre -s %{selinuxtype}

%post selinux
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/%{selinuxtype}/%{modulename}.pp.bz2

%postun selinux
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall -s %{selinuxtype} %{modulename}
fi

%posttrans selinux
%selinux_relabel_post -s %{selinuxtype}
# if with_selinux
%endif

%check
#meson_test -t 4

%files
%license COPYING
%doc NEWS THANKS AUTHORS README.md README.tod.md
%{_libdir}/*.so.*
%{_libdir}/girepository-1.0/*.typelib
%{_udevhwdbdir}/60-autosuspend-libfprint-2.hwdb
%{_udevrulesdir}/70-libfprint-2.rules
%{_datadir}/metainfo/org.freedesktop.libfprint.metainfo.xml
%dir /usr/lib64/libfprint-2/tod-1

%files devel
%doc HACKING.md
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/libfprint-2.pc
%{_libdir}/pkgconfig/libfprint-2-tod-1.pc
%{_datadir}/gir-1.0/*.gir
%{_datadir}/gtk-doc/html/libfprint-2/

%files tests
%{_libexecdir}/installed-tests/libfprint-2/
%{_datadir}/installed-tests/libfprint-2/

%if 0%{?with_selinux}
%files selinux
%{_datadir}/selinux/packages/%{selinuxtype}/%{modulename}.pp.*
%{_datadir}/selinux/devel/include/distributed/%{modulename}.if
%ghost %verify(not md5 size mode mtime) %{_sharedstatedir}/selinux/%{selinuxtype}/active/modules/200/%{modulename}
%endif

%changelog
* Tue Mar 24 2026 Christopher Tran <christophert@noreply.users.github.com> - 1.95.1+tod1
- Update to 1.95.1+tod1

* Mon Feb 23 2026 Graham White <graham_alton@hotmail.com> - 1.94.10+tod1
- Update to 1.94.10+tod1

* Tue Jul 29 2025 Graham White <graham_alton@hotmail.com> - 1.94.9+tod1
- Add SELinux policy

* Wed Mar 22 2023 Navneet Dhody <navneet.dhody@gmail.com> add Conflicts: libfprint

* Wed Mar 22 2023 Navneet Dhody <navneet.dhody@gmail.com> update to 1.94.5-tod1

* Tue Mar 30 2021 Kevin Anderson <andersonkw2@gmail.com> - 1.90.7+git20210222+tod1-2
- Add directory for tod drivers

* Tue Mar 30 2021 Kevin Anderson <andersonkw2@gmail.com> - 1.90.7+git20210222+tod1
- Initial Release
