%undefine _debugsource_packages
%global services lactd.service
%define oname LACT

Name:           lact
Version:        0.8.0
Release:        1
Summary:        Linux AMDGPU Controller
Group:          Utility
License:        MIT
URL:            https://github.com/ilya-zlobintsev/LACT
Source:         https://github.com/ilya-zlobintsev/LACT/archive/v%{version}/%{oname}-%{version}.tar.gz
Source1:        vendor.tar.xz
# vendor.tar.xz is generated using
# tar -xvf LACT-0.7.2.tar.gz && cargo vendor LACT-0.7.2/vendor && tar -cJf vendor.tar.xz LACT-0.7.2/vendor

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

[source."git+https://github.com/Umio-Yasuno/libdrm-amdgpu-sys-rs"]
git = "https://github.com/Umio-Yasuno/libdrm-amdgpu-sys-rs"
replace-with = "vendored-sources"

[source."git+https://github.com/kenba/cl3?branch=develop"]
git = "https://github.com/kenba/cl3"
branch = "develop"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"

EOF

%build
cargo build -p lact --release --features=adw

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
%{_datadir}/pixmaps/io.github.ilya_zlobintsev.LACT.png
%{_datadir}/icons/hicolor/scalable/apps/io.github.ilya_zlobintsev.LACT.svg
%{_unitdir}/lactd.service

