# TRSS安装器

TRSS安装器是一个基于Yunzai框架的TRSS分支的安装脚本，专注于在Windows平台自动化安装和配置TRSS环境。

本安装器支持从Miao分支迁移至TRSS分支，并提供了一系列便捷的操作选项。

## 功能
- 检查Node.js和Git版本
- 自定义命令执行
- 从Git仓库下载TRSS相关脚本
- 迁移从Miao分支至TRSS分支
- 安装Redis和其他依赖
- 启动TRSS和Redis服务

## 安装步骤

### 1. 环境检查
运行安装器前，请确保您的系统已安装Node.js（版本18及以上）和Git。

- https://git-scm.com/downloads
- https://nodejs.org/zh-cn/download


### 2. 下载安装器
您可以通过以下方式获取安装器：
- 从Release页面下载 -> https://github.com/shangxueink/TRSSLauncher-Setup/releases


- 克隆本仓库并自行编译

```bash
git clone https://github.com/shangxueink/TRSSLauncher-Setup.git
cd TRSSLauncher-Setup
task install  # 需要安装Task工具
task build
```

### 3. 运行安装器
- Windows: 双击`trss_manager.exe`或在命令行中运行

---

## 使用说明

### 菜单选项
- `1` - 获取redis-windows-7.0.4
- `2` - Git Clone TRSS项目
- `3` - 安装插件（TRSS+Genshin+Miao）
- `4` - 安装 pnpm 和 依赖
- `5` - 启动 redis-windows
- `6` - 启动 TRSS
- `7` - 自定义终端命令
- `8` - 从Miao云崽迁移至TRSS云崽
- `0` - 退出程序

### 自定义命令
输入`7`进入自定义命令模式，您可以输入任意命令进行执行。命令执行前，安装器会显示绿色提示"正在执行：[命令]"。

### 迁移流程
输入`8`开始从Miao分支迁移至TRSS分支。安装器会自动下载必要的脚本并执行迁移。

## 开发者信息

### 构建项目
本项目使用[Task](https://taskfile.dev/)管理构建流程。安装Task后，可以使用以下命令：

```bash
# 显示所有可用任务
task

# 运行源码
task start

# 构建Windows版本
task build

# 构建所有平台版本
task build-all
```

## 注意事项
- 请确保在执行安装器前备份您的数据。
- 在自定义命令模式下，输入的命令会被执行在当前目录下，请注意命令的安全性。
- 如果遇到任何问题，请检查日志输出或查看[常见问题解答](#常见问题解答)。

## 常见问题解答

### Q: 安装器无法检查到Node.js或Git版本？
A: 请确保Node.js和Git已正确安装，并且它们的可执行文件路径已添加至系统环境变量。

### Q: 迁移过程中出现问题？
A: 请确保您的Miao分支项目是最新的，并且已正确安装所有依赖。如果问题依旧，请查看控制台输出的错误信息，并根据提示进行相应的修复。

### Q: 如何退出安装器？
A: 输入`0`或按下`Ctrl+C`即可退出安装器。

## 许可证
本项目采用MIT许可证。详情请参阅LICENSE文件。
