# aTrust
南京大学 ztna VPN 客户端 aTrust（深信服）RPM Port  
由 NJU ztna.nju.edu.cn 的 [Ubuntu 客户端](https://ztna.nju.edu.cn/resource/client/linux/ubuntu/amd64/aTrustInstaller_amd64.deb) repackaging

# 构建
首先拉取 Github repo
```bash
git clone https://github.com/miyou379/aTrust.git
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
Fedora Linux 44 (Xfce, amd64)

在使用过程中遇到任何问题，欢迎开 issue 进行讨论

# Todo
- [ ] 使用 Github Action 自动化构建
- [ ] 维护 Copr 仓库
