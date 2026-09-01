%undefine _debugsource_packages
%global services lactd.service
%define oname LACT

# cargo test essentially recompiles the entire package _just_ to test it,
# this is a **gigantic waste of resources and time**.
# cargo needs to do better and be able to test using the as-built package the
# first time and not rebuild an entire package again just to test it.
# n.b. tests passing in VM local builds, disable for ABF.
%bcond cargotests 0

Name:           lact
Summary:        Linux GPU Configuration And Monitoring Tool
Version:        0.10.1
Release:        1
Group:          Utility
License:        MIT
URL:            https://github.com/ilya-zlobintsev/LACT
Source0:        https://github.com/ilya-zlobintsev/LACT/archive/v%{version}/%{oname}-%{version}.tar.gz
Source1:        vendor.tar.xz
# generate vendor by running inside source tree "cargo vendor" command.

BuildRequires: appstream-util
BuildRequires: cargo
BuildRequires: desktop-file-utils
BuildRequires: hicolor-icon-theme
BuildRequires: make
BuildRequires: pkgconfig(fuse3)
BuildRequires: pkgconfig(gtk4)
BuildRequires: pkgconfig(hwdata)
BuildRequires: pkgconfig(libdisplay-info)
BuildRequires: pkgconfig(libdrm)
BuildRequires: pkgconfig(libadwaita-1)
BuildRequires: pkgconfig(OpenCL)
BuildRequires: pkgconfig(pango)
BuildRequires: pkgconfig(vulkan)
BuildRequires: rust-packaging
BuildRequires: systemd-rpm-macros
BuildRequires: pkgconfig(pygobject-3.0)

Requires: clinfo
Requires: gtk4
Requires: hwdata
Requires: libadwaita-common
Requires: vulkan-tools
Requires: python-gi
Requires: python-gobject3

%description
This application allows you to control your AMD, Nvidia orIntel GPU on a
Linux system.

Features:

    Detailed GPU information reporting
    Monitoring
    Power configuration
    Thermals configuration
    Overclocking
    Settings profiles
    OpenTelemetry metrics exporter

GPU configuration is handled by a system service that does not depend on
a graphical session (Wayland/X11).

The service can also be used standalone with a config file, for example
in headless scenarios.

%prep
%autosetup -n %{oname}-%{version} -p1 -a1
# prep vendored crates
%cargo_prep -v vendor

cat >>.cargo/config <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source."git+https://github.com/ilya-zlobintsev/zbus_polkit?branch=fix-uid-type"]
git = "https://github.com/ilya-zlobintsev/zbus_polkit"
branch = "fix-uid-type"
replace-with = "vendored-sources"

[source."git+https://github.com/rust-nvml/nvml-wrapper.git?rev=eb47417eede43443f139053479618e96ad32893d"]
git = "https://github.com/rust-nvml/nvml-wrapper.git"
rev = "eb47417eede43443f139053479618e96ad32893d"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%build
%__cargo build -p lact --release
export CARGO_HOME=$PWD/.cargo
# sort out crate licenses
%cargo_license_summary
%{cargo_license} > LICENSES.dependencies

%install
%make_install PREFIX="%{_prefix}"

%check
%if %{with cargotests}
%__cargo test --release --frozen --all --all-features --verbose
%endif
desktop-file-validate %{buildroot}%{_datadir}/applications/*.%{oname}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/*.%{oname}.metainfo.xml

%post
%systemd_post lactd.service
systemctl enable --now lactd.service || true

%preun
%systemd_preun lactd.service

%postun
%systemd_postun_with_restart lactd.service

%files
%license LICENSE LICENSES.dependencies
%doc README.md docs/CONTRIBUTING.md docs/CONFIG.md docs/API.md docs/EXPORTER.md
%{_bindir}/lact
%{_datadir}/applications/io.github.ilya_zlobintsev.%{oname}.desktop
%{_datadir}/polkit-1/actions/io.github.ilya_zlobintsev.LACT.policy
%{_datadir}/metainfo/io.github.ilya_zlobintsev.%{oname}.metainfo.xml
%{_datadir}/icons/hicolor/*x*/apps/io.github.ilya_zlobintsev.%{oname}.png
%{_datadir}/icons/hicolor/scalable/apps/io.github.ilya_zlobintsev.%{oname}.svg
%{_unitdir}/lactd.service

