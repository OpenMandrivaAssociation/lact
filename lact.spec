%global services lactd.service
%define oname LACT

Name:           lact
Version:        0.6.0
Release:        1
Summary:        Linux AMDGPU Controller
Group:          Utility
License:        MIT
URL:            https://github.com/ilya-zlobintsev/LACT
Source:         https://github.com/ilya-zlobintsev/LACT/archive/v%{version}/%{oname}-%{version}.tar.gz
Source1:        vendor.tar.xz

BuildRequires:  cargo
BuildRequires:  rust-packaging
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  blueprint-compiler
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(systemd)
Requires:       %{name}-daemon = %{version}-%{release}
%description
This application allows you to control your AMD GPU on a Linux system.

%package daemon
Summary:        Linux AMDGPU Controller - headless binary
%description daemon
This application allows you to control your AMD GPU on a Linux system.

This package holds a headless binary without all the GUI dependencies.

%prep
# Vendored sources
%autosetup -n %{oname}-%{version} -p1 -a1
%cargo_prep -v vendor

cat >>.cargo/config <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source."git+https://github.com/ilya-zlobintsev/nvml-wrapper?branch=lact"]
git = "https://github.com/ilya-zlobintsev/nvml-wrapper"
branch = "lact"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%build
cargo_build -p lact --no-default-features --features=adw
mv target/release/lact{,-headless}
cargo_build -p lact --features=adw

%install
%make_install PREFIX="%{_prefix}"

%pre
%service_add_pre %{services}

%preun
%service_del_preun %{services}

%post
%service_add_post %{services}

%postun
%service_del_postun %{services}

%files
%license LICENSE
%doc *.md
%{_bindir}/lact
%{_datadir}/applications/io.github.lact-linux.desktop
%{_datadir}/pixmaps/io.github.lact-linux.png
%{_datadir}/icons/hicolor/scalable/apps/io.github.lact-linux.svg

%files daemon
%{_bindir}/lact-headless
%{_unitdir}/lactd.service
%license LICENSE
%doc *.md
