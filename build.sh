#!/usr/bin/env bash
set -euo pipefail

# 获取本构建脚本所在的目录路径
root_dir=$(CDPATH="" cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
rpmbuild_dir="$root_dir/rpmbuild"

source_deb="$root_dir/aTrustInstaller_amd64.deb"

if [[ ! -f "$source_deb" ]]; then
    printf "No aTrustInstaller deb package found, start downloading...\n"
    wget -O "$root_dir/aTrustInstaller_amd64.deb" "https://ztna.nju.edu.cn/resource/client/linux/ubuntu/amd64/aTrustInstaller_amd64.deb"
fi

mkdir -p "$rpmbuild_dir/BUILD" "$rpmbuild_dir/BUILDROOT" "$rpmbuild_dir/RPMS" \
         "$rpmbuild_dir/SOURCES" "$rpmbuild_dir/SPECS" "$rpmbuild_dir/SRPMS" \
         "$rpmbuild_dir/tmp"
ln -sfn "$source_deb" "$rpmbuild_dir/SOURCES/aTrustInstaller_amd64.deb"

cd "$root_dir"
rpmbuild -bb \
    --define "_topdir $rpmbuild_dir" \
    --define "_tmppath $rpmbuild_dir/tmp" \
    --define "_build_id_links none" \
    "$root_dir/atrust-rpm.spec"

pkg_path=$(find "$rpmbuild_dir/RPMS" -type f -name 'aTrust-*.rpm' -print | sort | tail -n 1)
if [[ -z "$pkg_path" ]]; then
    printf 'rpmbuild completed but no RPM was found under %s\n' "$rpmbuild_dir/RPMS" >&2
    exit 1
fi

pkg=$(basename "$pkg_path")
output_path="$root_dir/$pkg"
cp -f -- "$pkg_path" "$output_path"
printf 'Built: %s\n' "$output_path"
printf 'SHA256: '
sha256sum "$output_path"
