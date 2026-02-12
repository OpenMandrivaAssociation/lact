%undefine _debugsource_packages
%global services lactd.service
%define oname LACT

Name:           lact
Version:        0.8.4
Release:        1
Summary:        Linux AMDGPU Controller
Group:          Utility
License:        MIT
URL:            https://github.com/ilya-zlobintsev/LACT
Source0:        https://github.com/ilya-zlobintsev/LACT/archive/v%{version}/%{oname}-%{version}.tar.gz
Source1:        %{oname}-%{version}-vendor.tar.xz
# LACT-0.8.4-vendor.tar.xz is generated using:
# tar -xvf LACT-0.8.4.tar.gz && pushd LACT-0.8.4/ && cargo vendor && tar -cJf ../LACT-0.8.4-vendor.tar.xz vendor/ && popd

BuildRequires:  cargo
BuildRequires:  rust-packaging
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(blueprint-compiler)
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pygobject-3.0)
BuildRequires:  python-gi
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(OpenCL)

Requires: libadwaita-common
Requires: gtk4
Requires: python-gi
Requires: python-gobject3

%description
This application allows you to control your AMD GPU on a Linux system.

%prep
# Vendored sources
%autosetup -n %{oname}-%{version} -p1 -a1
%cargo_prep -v vendor

cat >>.cargo/config <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%build
%__cargo build -p lact --release --features=adw

%install
%make_install PREFIX="%{_prefix}"

%post
%systemd_post lactd.service
systemctl enable --now lactd.service || true

%preun
%systemd_preun lactd.service

%postun
%systemd_postun_with_restart lactd.service

%files
%license LICENSE
%doc *.md
%{_bindir}/lact
%{_datadir}/applications/io.github.ilya_zlobintsev.LACT.desktop
%{_datadir}/metainfo/io.github.ilya_zlobintsev.LACT.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/io.github.ilya_zlobintsev.LACT.svg
%{_datadir}/icons/hicolor/512x512/apps/io.github.ilya_zlobintsev.LACT.png
%{_unitdir}/lactd.service

