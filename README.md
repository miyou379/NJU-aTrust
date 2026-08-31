# NJU-aTrust
南京大学 ztna VPN 客户端 aTrust（深信服）RPM Port  
对 NJU ztna.nju.edu.cn [Ubuntu 客户端](https://ztna.nju.edu.cn/resource/client/linux/ubuntu/amd64/aTrustInstaller_amd64.deb) 的重新打包

# 替代品
推荐使用 [zju-connect](https://github.com/Mythologyli/zju-connect)

# 构建
首先下载构建所需依赖
```bash
sudo dnf wget install rpm-build redhat-rpm-config rpmautospec
```
拉取 Github repo
```bash
git clone https://github.com/miyou379/NJU-aTrust.git
```
执行 `build.sh`
```bash
cd aTrust && ./build.sh
```

# Issues
已测试可用的平台：
- Fedora Linux 44 (Workstation Edition)
- Fedora Linux 44 (Xfce)

Release 构建平台：  
Github Actions with Docker fedora image (`fedora:latest`)  
目前 `fedora:latest` 为 Fedora 44

在使用过程中遇到任何问题，欢迎开 issue 进行讨论

# Todo
- [x] 使用 Github Actions 自动化构建
- [ ] 维护 Copr 仓库
