Name:           aTrust
Version:        2.5.16.30
Release:        %autorelease
Summary:        Sangfor aTrust VPN client
License:        Proprietary
URL:            https://ztna.nju.edu.cn/
Source0:        aTrustInstaller_amd64.deb

ExclusiveArch:  x86_64
BuildRequires:  bash
BuildRequires:  binutils
BuildRequires:  gzip
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  desktop-file-utils

Requires:       bash
Requires:       gawk
Requires:       grep
Requires:       psmisc
Requires:       procps-ng
Requires:       systemd
Requires:       xdg-utils
Requires(post):  systemd
Requires(pre):   psmisc
Requires(pre):   systemd
Requires(preun): psmisc
Requires(preun): systemd
Requires(postun): systemd

# 关闭 BRP 重写/strip，以保持上游 deb 包的行为
%global __os_install_post %{nil}

# 下面这些依赖被 libldap_r 所依赖，上游 deb 包中已经 bundled
# 且 libldap_r 疑似已经 unused
%filter_from_requires /^libgcrypt/d
%filter_from_requires /^libgnutls/d
%filter_from_requires /^libsasl2/d
%filter_from_requires /^libsqlite3/d
%filter_setup

%description
此客户端将对访问应用的请求进行全生命周期的保护，帮助用户安全快速的访问应用
注意：浏览器在安装过程中会被强制关闭

%prep
rm -rf ar payload
mkdir -p ar payload
cd ar
ar x %{SOURCE0}
cd ..
tar -xJf ar/data.tar.xz -C payload

test -x payload/usr/share/sangfor/aTrust/aTrustTray
test -x payload/usr/share/sangfor/aTrust/resources/bin/aTrustAgent
test -f payload/usr/lib/systemd/system/aTrustDaemon.service
test -f payload/usr/share/applications/cn.com.sangfor.atrust.desktop

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a payload/. %{buildroot}/

# deb 包 postinst 保留了 755 权限
chmod 4755 %{buildroot}/usr/share/sangfor/aTrust/uem/bin/uem_installer
chmod 4755 %{buildroot}/usr/share/sangfor/aTrust/resources/bin/dmidecode_processor_tool

# 修改原包中 desktop 的 `packagename=aTrustInstaller.deb` 字段，使之符合 XDG 规范
sed -i 's/^packagename=.*/X-Packagename=aTrustInstaller_amd64.rpm/' \
  %{buildroot}/usr/share/applications/cn.com.sangfor.atrust.desktop

%check
test -x %{buildroot}/usr/share/sangfor/aTrust/aTrustTray
test -x %{buildroot}/usr/share/sangfor/aTrust/resources/bin/aTrustAgent
test -L %{buildroot}/usr/share/sangfor/aTrust/aTrustTray2
test "$(readlink %{buildroot}/usr/share/sangfor/aTrust/aTrustTray2)" = "resources/bin/aTrustTray2"
test "$(readlink %{buildroot}/usr/share/sangfor/aTrust/resources/bin/libZipper.so)" = "libZipper.so.1"
desktop-file-validate %{buildroot}/usr/share/applications/cn.com.sangfor.atrust.desktop

%pre
# 安装之前先停止之前可能安装的 aTrust
if [ -x /usr/bin/systemctl ]; then
    /usr/bin/systemctl stop aTrustDaemon.service >/dev/null 2>&1 || :
fi
if command -v pkill >/dev/null 2>&1; then
    for process in aTrustAgent aTrustXtunnel-64 aTrustTray2 aTrustTray; do
        pkill -TERM -x "$process" >/dev/null 2>&1 || :
    done
fi
exit 0

%post
# 进行 preset
%systemd_post aTrustDaemon.service

# 为什么把配置文件放在这里。。。
state=/usr/share/sangfor/.aTrust
install -d -m 0777 "$state" "$state/bin" "$state/tmp" "$state/Crash" \
    "$state/iddbase" "$state/database" "$state/var" "$state/var/run" \
    "$state/var/conf" "$state/var/run/plugin-daemon" \
    "$state/var/run/plugins/aTrustCore" "$state/var/run/plugins/aTrustTunnel"

# 创建不存在的锁
for lock in \
    sapp-aTrustAgent-b269-lockfile \
    sapp-aTrustAgent_plugin-daemon-b49a-lockfile \
    sapp-aTrustAgent_plugins_aTrustCore_h_e-5c4f-lockfile \
    sapp-aTrustAgent_plugins_aTrustTunnel-f282-lockfile \
    Globalatrustdb_lock_atrust.spa \
    Globalatrustdb_lock_private.dns \
    Globalatrustdb_lock_tunnel.access2 \
    Globalatrustdb_lock_TunnelSharedConfig \
    GlobalDeviceIdLock \
    GlobalSdpUserLogin; do
    if [ ! -e "$state/$lock" ]; then
        : > "$state/$lock"
    fi
    chmod 0666 "$state/$lock" || :
done

printf '%s' 54630 > "$state/var/run/httpserver"
printf '%s' 55630 > "$state/var/run/eventbus"
printf '%s' 56630 > "$state/var/run/plugin-daemon/thrift"
printf '%s' 56641 > "$state/var/run/plugins/aTrustCore/thrift"
printf '%s' 56652 > "$state/var/run/plugins/aTrustTunnel/thrift"
chmod 0666 "$state/var/run/httpserver" "$state/var/run/eventbus" \
    "$state/var/run/plugin-daemon/thrift" \
    "$state/var/run/plugins/aTrustCore/thrift" \
    "$state/var/run/plugins/aTrustTunnel/thrift" 2>/dev/null || :

install -d -m 0755 /root/.aTrust/logs 2>/dev/null || :

# 如果之前安装过 aTrust（installAddr.conf 存在），需要转换 SQLite 数据库
if [ -x /usr/share/sangfor/aTrust/resources/bin/ConfigUpgrade ] && \
   [ -f "$state/var/conf/installAddr.conf" ]; then
    /usr/share/sangfor/aTrust/resources/bin/ConfigUpgrade \
        -d "$state/database" -a "$state/var/conf/installAddr.conf" \
        >/dev/null 2>&1 || :
fi

printf '%s\n' \
    'aTrust 已安装，请使用 systemctl 来启动服务：' \
    '立即启动：sudo systemctl start aTrustDaemon.service' \
    '设置开机启动：sudo systemctl enable aTrustDaemon.service'
exit 0

%preun
%systemd_preun aTrustDaemon.service
if [ "$1" -eq 0 ]; then
    if [ -x /usr/bin/systemctl ]; then
        /usr/bin/systemctl disable --now aTrustDaemon.service >/dev/null 2>&1 || :
    fi
    if command -v pkill >/dev/null 2>&1; then
        for process in aTrustAgent aTrustXtunnel-64 aTrustTray2 aTrustTray; do
            pkill -TERM -x "$process" >/dev/null 2>&1 || :
            pkill -KILL -x "$process" >/dev/null 2>&1 || :
        done
    fi
fi
exit 0

%postun
%systemd_postun_with_restart aTrustDaemon.service
if [ "$1" -eq 0 ] && [ -x /usr/bin/systemctl ]; then
    /usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
exit 0

%files
%defattr(-,root,root,-)
/opt/apps/cn.com.sangfor.atrust
/usr/lib/systemd/system/aTrustDaemon.service
/usr/lib/systemd/system/aTrustShell.service
/usr/lib/systemd/system/aTrustTray@.service
/usr/lib/systemd/user/aTrustShell.service
/usr/lib/systemd/user/aTrustTray.service
/usr/share/applications/cn.com.sangfor.atrust.desktop
/usr/share/pixmaps/aTrust.png
/usr/share/sangfor/aTrust

%changelog
%autochangelog
