package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/fatih/color"
	"github.com/shirou/gopsutil/process"
)

// 定义颜色输出
var (
	green  = color.New(color.FgGreen).SprintFunc()
	red    = color.New(color.FgRed).SprintFunc()
	yellow = color.New(color.FgYellow).SprintFunc()
	blue   = color.New(color.FgBlue).SprintFunc()
)

// 检查环境
func checkEnvironment() bool {
	// 检查Node.js版本
	nodeCmd := exec.Command("node", "-v")
	nodeOutput, err := nodeCmd.CombinedOutput()
	if err != nil {
		// 检查是否是 "executable file not found" 错误
		if strings.Contains(err.Error(), "executable file not found") {
			fmt.Println("请确保您的系统已安装Node.js（版本18及以上）和Git。")
			fmt.Println("- https://git-scm.com/downloads")
			fmt.Println("- https://nodejs.org/zh-cn/download")
			return false
		} else {
			fmt.Printf("执行 Node.js 版本检查时出错：%v\n", err)
			return false
		}
	}
	nodeVersion := strings.TrimSpace(string(nodeOutput))
	fmt.Printf("Node.js 版本: %s  √\n", nodeVersion)

	// 检查Node.js主版本号
	versionStr := strings.TrimPrefix(nodeVersion, "v")
	versionParts := strings.Split(versionStr, ".")
	if len(versionParts) > 0 {
		majorVersion, err := strconv.Atoi(versionParts[0])
		if err != nil || majorVersion < 18 {
			fmt.Println("Node.js 版本低于 18。请更新 Node.js ！请前往 https://nodejs.org/zh-cn/download 下载最新版！")
			return false
		}
	}

	// 检查Git版本
	gitCmd := exec.Command("git", "--version")
	gitOutput, err := gitCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("执行 Git 版本检查时出错：%v\n", err)
		return false
	}
	gitVersion := strings.TrimSpace(string(gitOutput))
	fmt.Printf("Git 版本: %s  √\n", gitVersion)

	// 打印TRSS标志
	fmt.Println(` 
 ______    ______     ______     ______    
/\__  _\  /\  == \   /\  ___\   /\  ___\   
\/_/\ \/  \ \  __<   \ \___  \  \ \___  \  
   \ \_\   \ \_\ \_\  \/\_____\  \/\_____\ 
    \/_/    \/_/ /_/   \/_____/   \/_____/                                                                                                                                                   
          `)
	return true
}

// 执行自定义命令
func executeCustomCommand(command string, newWindow bool) {
	originalCwd, _ := os.Getwd()
	directories := []string{"Yunzai-Bot", "Yunzai"}

	var rootDir string
	for _, dir := range directories {
		if fileExists(dir) {
			rootDir = dir
			break
		}
	}

	if rootDir != "" {
		os.Chdir(rootDir)
		if command != "" {
			if newWindow {
				cmd := exec.Command("cmd", "/c", "start", "cmd", "/k", command)
				cmd.Start()
			} else {
				runCommand(command, false)
			}
		} else {
			fmt.Println("请输入命令(输入0退出)：")
			scanner := bufio.NewScanner(os.Stdin)
			for {
				scanner.Scan()
				cmd := scanner.Text()
				if cmd == "0" {
					fmt.Println(green("退出自定义指令状态。"))
					break
				}
				fmt.Println(green("正在执行: " + cmd))
				try := func() {
					if newWindow {
						startCmd := exec.Command("cmd", "/c", "start", "cmd", "/k", cmd)
						startCmd.Start()
					} else {
						runCommand(cmd, false)
					}
				}
				try()
				fmt.Println(green("执行完成！(输入0退出)"))
			}
		}
		os.Chdir(originalCwd)
	} else {
		fmt.Println("未找到云崽根目录。请确保 Yunzai-Bot 或 Yunzai 目录存在。")
	}
}

// 启动TRSS
func startTrss() {
	executeCustomCommand("node .", true)
}

// 删除并重新安装依赖
func delAndReinstallDependencies() {
	originalCwd, _ := os.Getwd()
	directories := []string{"Yunzai-Bot", "Yunzai"}

	var rootDir string
	for _, dir := range directories {
		if fileExists(dir) {
			rootDir = dir
			break
		}
	}

	if rootDir != "" {
		nodeModulesPath := filepath.Join(rootDir, "node_modules")
		if fileExists(nodeModulesPath) {
			fmt.Print(red("检测到node_modules文件夹，是否覆盖？(y/n): "))
			var choice string
			fmt.Scanln(&choice)
			if strings.ToLower(choice) == "y" {
				fmt.Println(yellow("正在删除node_modules..."))
				os.RemoveAll(nodeModulesPath)
				fmt.Println(green("node_modules 文件夹已删除。"))
			} else {
				fmt.Println(yellow("操作取消。"))
				return
			}
		}
		os.Chdir(rootDir)
		os.Chdir(originalCwd)
		executeCustomCommand("pnpm i --registry=https://registry.npmmirror.com", false)
	} else {
		fmt.Println(red("未找到云崽根目录。请确保 Yunzai-Bot 或 Yunzai 目录存在。"))
	}
}

// 从Git下载trss.js文件
func downloadTrssJsFromGit(repoURL, tempDir, targetFilename string) string {
	cmd := exec.Command("git", "clone", repoURL, tempDir)
	err := cmd.Run()
	if err != nil {
		return ""
	}

	srcPath := filepath.Join(tempDir, targetFilename)
	if fileExists(srcPath) {
		return srcPath
	}
	return ""
}

// 判断是否为Miao项目
func isMiaoProject(projectDir string) bool {
	packageJsonPath := filepath.Join(projectDir, "package.json")
	if fileExists(packageJsonPath) {
		data, err := os.ReadFile(packageJsonPath)
		if err != nil {
			return false
		}

		var packageData map[string]interface{}
		err = json.Unmarshal(data, &packageData)
		if err != nil {
			return false
		}

		if projectName, ok := packageData["name"].(string); ok {
			return strings.Contains(projectName, "miao")
		}
	}
	return false
}

// 从Miao迁移到TRSS
func migrateFromMiaoToTrss() {
	var rootDir string
	if fileExists("Yunzai-Bot") {
		rootDir = "Yunzai-Bot"
	} else if fileExists("Yunzai") {
		rootDir = "Yunzai"
	}

	if rootDir != "" && isMiaoProject(rootDir) {
		os.Chdir(rootDir)
		trssJsPath := "trss.js"

		if !fileExists(trssJsPath) {
			tempDir, err := os.MkdirTemp("", "trss-temp")
			if err == nil {
				defer os.RemoveAll(tempDir)

				fmt.Println("未找到 trss.js，开始从远程仓库下载...")
				repoURL := "https://gitee.com/yoimiya-kokomi/Miao-Yunzai.git"
				srcPath := downloadTrssJsFromGit(repoURL, tempDir, "trss.js")
				if srcPath != "" {
					copyFile(srcPath, trssJsPath)
					fmt.Println("下载 trss.js 成功。")
				} else {
					fmt.Println("下载 trss.js 失败。")
				}
			}
		}

		cmd := exec.Command("node", trssJsPath)
		cmd.Run()
		fmt.Println("迁移成功！")
		os.Chdir("..")
	} else {
		fmt.Println("当前不是Miao崽！暂不支持该选项操作！")
	}
}

// 运行命令
func runCommand(command string, ignoreErrors bool) bool {
	fmt.Println(green("正在执行: " + command))
	cmd := exec.Command("cmd", "/c", command)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Run()
	if err != nil && !ignoreErrors {
		fmt.Println(red("执行命令出错：" + err.Error()))
		return false
	}
	return true
}

// Git克隆
func gitClone(repositoryURL, targetFolder string) {
	if fileExists(targetFolder) {
		if isDir(targetFolder) && !isDirEmpty(targetFolder) {
			fmt.Print(red(fmt.Sprintf("文件夹 %s 已存在且不为空。是否覆盖? (y/n): ", targetFolder)))
			var answer string
			fmt.Scanln(&answer)
			if strings.ToLower(answer) != "y" {
				fmt.Println(green("已跳过克隆操作。"))
				return
			}
			os.RemoveAll(targetFolder)
		} else if !isDir(targetFolder) {
			os.Remove(targetFolder)
		}
	}

	runCommand(fmt.Sprintf("git clone --depth 1 %s %s", repositoryURL, targetFolder), false)
}

// 克隆Redis
func gitCloneRedis() {
	gitClone("https://gitee.com/bling_yshs/redis-windows-7.0.4", "redis-windows-7.0.4")
}

// 克隆TRSS
func gitCloneTrss() {
	gitClone("https://gitee.com/TimeRainStarSky/Yunzai", "Yunzai")
}

// 安装插件
func installPlugins() {
	executeCustomCommand("git clone --depth 1 https://gitee.com/TimeRainStarSky/TRSS-Plugin/ plugins/TRSS-Plugin", false)
	executeCustomCommand("git clone --depth 1 https://gitee.com/TimeRainStarSky/Yunzai-genshin plugins/genshin", false)
	executeCustomCommand("git clone --depth 1 https://gitcode.com/TimeRainStarSky/miao-plugin.git plugins/miao-plugin", false)
	executeCustomCommand("git -C plugins/miao-plugin remote set-url origin https://gitcode.com/TimeRainStarSky/miao-plugin.git", false)
}

// 安装pnpm和依赖
func installPnpmAndDependencies() {
	runCommand("npm i -g pnpm --registry=https://registry.npmmirror.com", false)
	executeCustomCommand("pnpm i --registry=https://registry.npmmirror.com", false)
}

// 检查端口是否被占用
func isPortInUse(port int) bool {
	// 尝试在指定端口上创建一个TCP监听器
	address := fmt.Sprintf("127.0.0.1:%d", port)
	listener, err := net.Listen("tcp", address)

	// 如果创建监听器出错，说明端口被占用
	if err != nil {
		return true
	}

	// 如果成功创建了监听器，说明端口未被占用
	// 关闭监听器并返回false
	listener.Close()
	return false
}

// 启动Redis (Windows)
func startRedisWindows() {
	entries, err := os.ReadDir(".")
	if err != nil {
		fmt.Println("读取目录失败:", err)
		return
	}

	var redisFolder string
	for _, entry := range entries {
		if entry.IsDir() && strings.HasPrefix(entry.Name(), "redis-windows") {
			redisFolder = entry.Name()
			break
		}
	}

	if redisFolder != "" {
		os.Chdir(redisFolder)
		configFile := "redis.conf"

		if fileExists(configFile) {
			// 检查端口是否被占用
			port := 6379 // 默认端口

			if isPortInUse(port) {
				fmt.Println(red(fmt.Sprintf("当前端口 %d 已被占用！可能已有redis服务正在运行！", port)))
			} else {
				// 使用start命令在新窗口中启动Redis服务器
				cmd := exec.Command("cmd", "/c", "start", "cmd", "/k", "redis-server.exe", "redis.conf")
				err := cmd.Start()
				if err != nil {
					fmt.Println(red("启动Redis服务器失败: " + err.Error()))
				} else {
					fmt.Println(green("Redis服务器已在新窗口中启动。"))
				}
			}
		} else {
			fmt.Println("未找到 redis.conf 文件。")
		}
		os.Chdir("..")
	} else {
		fmt.Println("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")
	}
}

// 停止所有Redis Windows进程
func stopAllRedisWindows() {
	redisFolder := ""
	files, err := os.ReadDir(".")
	if err == nil {
		for _, file := range files {
			if file.IsDir() && strings.HasPrefix(file.Name(), "redis-windows") {
				redisFolder = file.Name()
				break
			}
		}
	}

	if redisFolder != "" {
		os.Chdir(redisFolder)
		runCommand("taskkill /IM redis-server.exe /F", true)
		os.Chdir("..")
	} else {
		fmt.Println("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")
	}
}

// 停止所有Node.js进程
func stopAllNodejs() {
	runCommand("taskkill /IM node.exe /F", true)
	fmt.Println("所有 Node.js 进程已关闭。")
}

// 停止Redis Windows
func stopRedisWindows() {
	redisFolder := ""
	files, err := os.ReadDir(".")
	if err == nil {
		for _, file := range files {
			if file.IsDir() && strings.HasPrefix(file.Name(), "redis-windows") {
				redisFolder = file.Name()
				break
			}
		}
	}

	if redisFolder != "" {
		os.Chdir(redisFolder)
		absPath, _ := filepath.Abs("redis-server.exe")

		processes, err := process.Processes()
		if err == nil {
			for _, p := range processes {
				name, _ := p.Name()
				if name == "redis-server.exe" {
					exe, _ := p.Exe()
					if exe == absPath {
						p.Terminate()
						fmt.Printf("成功终止进程: %d\n", p.Pid)
					}
				}
			}
		}

		os.Chdir("..")
	} else {
		fmt.Println("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")
	}
}

// 显示主菜单
func displayMainMenu() string {
	fmt.Print(`
当前版本: v0.1.6
===TRSS管理===
1. 安装 TRSS 云崽
2. 管理 TRSS 云崽
3. TRSS 云崽工具
-1. 退出本程序
`)
	fmt.Print(yellow("\n请选择操作："))
	var choice string
	fmt.Scanln(&choice)
	fmt.Println()
	return choice
}

// 显示安装菜单
func display1Menu() string {
	fmt.Print(`
===安装 TRSS 云崽===
1. 获取 redis-windows-7.0.4
2. 获取 TRSS 云崽
3. 安装插件( TRSS + Genshin + Miao )
4. 安装 pnpm 和 插件依赖
5. 启动 redis-windows 服务
6. 启动 TRSS 云崽
0. 返回上一级
`)
	fmt.Print(yellow("\n请选择操作："))
	var choice string
	fmt.Scanln(&choice)
	fmt.Println()
	return choice
}

// 显示管理菜单
func display2Menu() string {
	fmt.Print(`
===管理 TRSS 云崽===
1. 启动 redis-windows-7.0.4 服务
2. 启动 TRSS 云崽
3. 自定义 TRSS 终端命令
4. 安装依赖
5. **关闭 redis 和 TRSS 云崽**
6. **关闭所有 redis-server.exe 的进程**
7. **关闭所有 nodejs 的进程**
0. 返回上一级
`)
	fmt.Print(yellow("\n请选择操作："))
	var choice string
	fmt.Scanln(&choice)
	fmt.Println()
	return choice
}

// 显示工具菜单
func display3Menu() string {
	fmt.Print(`
===TRSS 云崽工具===
1. 从 Miao 云崽迁移至 TRSS 云崽
2. 重装 TRSS 的依赖
0. 返回上一级
`)
	fmt.Print(yellow("\n请选择操作："))
	var choice string
	fmt.Scanln(&choice)
	fmt.Println()
	return choice
}

// 主函数
func main() {
	if !checkEnvironment() {
		fmt.Println(green("按下任意键退出..."))
		fmt.Scanln()
		return
	}

	for {
		choice := displayMainMenu()
		if choice == "1" {
			for {
				choice := display1Menu()
				if choice == "1" {
					gitCloneRedis()
				} else if choice == "2" {
					gitCloneTrss()
				} else if choice == "3" {
					installPlugins()
				} else if choice == "4" {
					installPnpmAndDependencies()
				} else if choice == "5" {
					startRedisWindows()
				} else if choice == "6" {
					startTrss()
				} else if choice == "0" {
					break
				} else {
					fmt.Println(red("无效的选择，请重新输入。"))
				}
			}
		} else if choice == "2" {
			for {
				choice := display2Menu()
				if choice == "1" {
					startRedisWindows()
				} else if choice == "2" {
					startTrss()
				} else if choice == "3" {
					executeCustomCommand("", false)
				} else if choice == "4" {
					installPnpmAndDependencies()
				} else if choice == "5" {
					executeCustomCommand("node . stop", false)
					stopRedisWindows()
				} else if choice == "6" {
					stopAllRedisWindows()
				} else if choice == "7" {
					stopAllNodejs()
				} else if choice == "0" {
					break
				} else {
					fmt.Println(red("无效的选择，请重新输入。"))
				}
			}
		} else if choice == "3" {
			for {
				choice := display3Menu()
				if choice == "1" {
					migrateFromMiaoToTrss()
				} else if choice == "2" {
					delAndReinstallDependencies()
				} else if choice == "0" {
					break
				} else {
					fmt.Println(red("无效的选择，请重新输入。"))
				}
			}
		} else if choice == "-1" {
			break
		} else {
			fmt.Println(red("无效的选择，请重新输入。"))
		}
		fmt.Println(green("操作完成，按下任意键继续..."))
		fmt.Scanln()
	}
}

// 检查文件是否存在
func fileExists(path string) bool {
	_, err := os.Stat(path)
	return !os.IsNotExist(err)
}

// 检查路径是否为目录
func isDir(path string) bool {
	info, err := os.Stat(path)
	if err != nil {
		return false
	}
	return info.IsDir()
}

// 检查目录是否为空
func isDirEmpty(path string) bool {
	f, err := os.Open(path)
	if err != nil {
		return false
	}
	defer f.Close()

	_, err = f.Readdirnames(1)
	return err == io.EOF
}

// 复制文件
func copyFile(src, dst string) error {
	source, err := os.Open(src)
	if err != nil {
		return err
	}
	defer source.Close()

	destination, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer destination.Close()

	_, err = io.Copy(destination, source)
	return err
}
